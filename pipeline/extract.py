"""LLM 추출 — 동시성 제한, 재시도, 사후 검증, 토큰·지연 기록."""

from __future__ import annotations

import asyncio
import json
import os
import random
import time
from dataclasses import dataclass

import openai
from openai import AsyncOpenAI

from pipeline.lang import detect_language
from pipeline.prompt import PROMPT_VERSION, prompt_fingerprint, system_prompt, user_prompt
from pipeline.schema import output_schema, validate
from pipeline.sources import Item
from pipeline.store import Store, cache_key
from pipeline.taxonomy import Taxonomy

UPSTAGE_BASE_URL = "https://api.upstage.ai/v1"

# USD / 1M tokens (input, cached input, output). https://www.upstage.ai/pricing 2026-09-29 기준
PRICES = {
    "solar-pro2": (0.15, 0.015, 0.6),
    "solar-mini": (0.10, 0.01, 0.40),
}

MAX_ATTEMPTS = 4
# 재시도해도 결과가 달라지지 않는 오류는 바로 실패 처리한다
_RETRYABLE = (openai.RateLimitError, openai.APITimeoutError, openai.APIConnectionError, openai.InternalServerError)


# Upstage 기본 한도 (응답 헤더 x-upstage-ratelimit-limit-*). 한도보다 조금 낮게 잡는다
DEFAULT_RPM = 90
DEFAULT_TPM = 225_000


@dataclass
class Job:
    item: Item
    key: str


class RateLimiter:
    """분당 요청 수와 분당 토큰 수를 함께 지키는 슬라이딩 윈도 제한기.

    Upstage 는 캐시 적중 토큰도 분당 토큰 한도에 포함한다. 프롬프트가 5천 토큰이면
    요청 한도(100)보다 토큰 한도(25만 / 5천 = 50)가 먼저 걸린다.
    """

    def __init__(self, rpm: int, tpm: int, est_tokens: int = 6000):
        self.rpm, self.tpm = rpm, tpm
        self.est_tokens = est_tokens  # 실제 사용량을 보며 갱신한다
        self.window: list[tuple[float, int]] = []  # (시각, 토큰)
        self.blocked_until = 0.0
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        while True:
            async with self.lock:
                now = time.monotonic()
                self.window = [(t, n) for t, n in self.window if now - t < 60]
                used = sum(n for _, n in self.window)
                wait = self.blocked_until - now
                if wait <= 0 and len(self.window) < self.rpm and used + self.est_tokens <= self.tpm:
                    self.window.append((now, self.est_tokens))
                    return
                if wait <= 0:
                    wait = 60 - (now - self.window[0][0]) if self.window else 1.0
            await asyncio.sleep(max(wait, 0.05))

    def record(self, tokens: int) -> None:
        # 추정치를 실제 평균 쪽으로 옮긴다 (지수 이동 평균)
        self.est_tokens = int(0.8 * self.est_tokens + 0.2 * tokens)

    def block_until_reset(self, headers) -> None:
        """429 응답의 리셋 시각(epoch 초)까지 모든 요청을 멈춘다."""
        resets = []
        for k in ("x-upstage-ratelimit-reset-requests", "x-upstage-ratelimit-reset-tokens"):
            try:
                resets.append(float(headers.get(k)) - time.time())
            except (TypeError, ValueError):
                pass
        delay = max([r for r in resets if 0 < r < 120], default=10.0)
        self.blocked_until = max(self.blocked_until, time.monotonic() + delay + random.random())


def make_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=os.environ["UPSTAGE_API_KEY"], base_url=UPSTAGE_BASE_URL, timeout=60, max_retries=0)


def cost_usd(model: str, prompt_tokens: int, cached_tokens: int, completion_tokens: int) -> float | None:
    if model not in PRICES:
        return None
    p_in, p_cached, p_out = PRICES[model]
    return ((prompt_tokens - cached_tokens) * p_in + cached_tokens * p_cached + completion_tokens * p_out) / 1e6


def plan_jobs(tax: Taxonomy, items: list[Item], model: str) -> list[Job]:
    return [
        Job(item=it, key=cache_key(it.content_type, it.text, model, prompt_fingerprint(tax, it.content_type)))
        for it in items
    ]


async def _extract_one(
    client: AsyncOpenAI,
    tax: Taxonomy,
    job: Job,
    model: str,
    store: Store,
    sem: asyncio.Semaphore,
    limiter: RateLimiter,
) -> dict:
    item = job.item
    messages = [
        {"role": "system", "content": system_prompt(tax, item.content_type)},
        {"role": "user", "content": user_prompt(item.content_type, item.text, item.meta)},
    ]
    response_format = {
        "type": "json_schema",
        "json_schema": {"name": f"label_{item.content_type}", "strict": True, "schema": output_schema(tax, item.content_type)},
    }
    row = {
        "cache_key": job.key,
        "item_id": item.id,
        "source": item.source,
        "content_type": item.content_type,
        "model": model,
        "taxonomy_version": tax.version,
        "prompt_version": PROMPT_VERSION,
        "prompt_fp": prompt_fingerprint(tax, item.content_type),
        "language": detect_language(item.text),
        "prompt_tokens": 0,
        "cached_tokens": 0,
        "completion_tokens": 0,
    }

    last_error = ""
    attempt = rate_limited = 0
    call_ms = 0.0
    async with sem:
        while attempt < MAX_ATTEMPTS:
            attempt += 1
            await limiter.acquire()
            call_started = time.perf_counter()
            try:
                resp = await client.chat.completions.create(
                    model=model, messages=messages, response_format=response_format, temperature=0
                )
                # 지연은 API 응답 시간만 잰다. 속도 제한 대기는 처리량 쪽 지표다
                call_ms = (time.perf_counter() - call_started) * 1000
                usage = resp.usage
                if usage:
                    # 재시도 호출의 토큰도 비용이므로 누적한다
                    row["prompt_tokens"] += usage.prompt_tokens
                    row["completion_tokens"] += usage.completion_tokens
                    details = usage.prompt_tokens_details
                    row["cached_tokens"] += (details.cached_tokens or 0) if details else 0
                    limiter.record(usage.total_tokens)
                validated = validate(tax, item.content_type, json.loads(resp.choices[0].message.content))
                row.update(status="ok", labels=validated.labels, issues=validated.issues, error=None)
                break
            except (json.JSONDecodeError, ValueError) as e:
                # 스키마 강제에도 형식·라벨이 어긋난 경우. 같은 입력이라도 다시 시도하면 대개 통과한다
                last_error = f"{type(e).__name__}: {e}"
            except openai.RateLimitError as e:
                last_error = f"{type(e).__name__}: {e}"
                limiter.block_until_reset(e.response.headers)
                rate_limited += 1
                if rate_limited <= 10:
                    attempt -= 1  # 한도 대기는 재시도 횟수에 넣지 않는다. 대기는 limiter 가 맡는다
                continue
            except _RETRYABLE as e:
                last_error = f"{type(e).__name__}: {e}"
            except openai.APIStatusError as e:
                # 400·401 등은 다시 보내도 같다
                last_error = f"{type(e).__name__}({e.status_code}): {e.message}"
                break
            if attempt < MAX_ATTEMPTS:
                await asyncio.sleep(min(2**attempt, 20) + random.random())
        if row.get("status") != "ok":
            row.update(status="error", labels=None, issues=None, error=last_error)
        row["attempts"] = attempt
        row["latency_ms"] = call_ms

    store.upsert(row)
    return row


async def run_jobs(
    tax: Taxonomy,
    jobs: list[Job],
    model: str,
    store: Store,
    concurrency: int,
    on_done=None,
    rpm: int = DEFAULT_RPM,
    tpm: int = DEFAULT_TPM,
) -> list[dict]:
    client = make_client()
    sem = asyncio.Semaphore(concurrency)
    limiter = RateLimiter(rpm, tpm)

    async def wrapped(job: Job) -> dict:
        row = await _extract_one(client, tax, job, model, store, sem, limiter)
        if on_done:
            on_done(row)
        return row

    try:
        return await asyncio.gather(*(wrapped(j) for j in jobs))
    finally:
        await client.close()
