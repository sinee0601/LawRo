"""
RAG 구간 계측 트레이스 (measure/rag-latency 브랜치 전용)

요청 1건당 JSONL 1줄을 append 한다. 슬라이딩 윈도우 100은 평균만 주므로
p95 를 구하려면 원시 레코드가 필요하다.

BENCH_TRACE_PATH 가 설정되지 않으면 모든 함수가 no-op 이다 —
운영 실행 경로에는 파일 I/O 도 컨텍스트 설정도 발생하지 않는다.
"""

import json
import os
import threading
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# 요청 단위 메타(회차·질의 ID·언어)는 벤치 드라이버가 주입한다.
_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar("rag_trace_context", default=None)

_write_lock = threading.Lock()
_header_written = False


def enabled() -> bool:
    return bool(os.getenv("BENCH_TRACE_PATH"))


def set_context(run: int, query_id: str, lang: str) -> None:
    _context.set({"run": run, "query_id": query_id, "lang": lang})


def clear_context() -> None:
    _context.set(None)


def write_header(meta: Dict[str, Any]) -> None:
    """실행 메타(커밋·임계값·Top-k·모델명·컬렉션 count)를 첫 줄에 남긴다."""
    path = os.getenv("BENCH_TRACE_PATH")
    if not path:
        return
    global _header_written
    with _write_lock:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps({"type": "meta", **meta}, ensure_ascii=False) + "\n")
        _header_written = True


def record(**fields: Any) -> None:
    path = os.getenv("BENCH_TRACE_PATH")
    if not path:
        return

    ctx = _context.get() or {}
    row = {
        "type": "sample",
        "ts": datetime.now(timezone.utc).isoformat(),
        "run": ctx.get("run"),
        "query_id": ctx.get("query_id"),
        "lang": ctx.get("lang"),
        **fields,
    }
    with _write_lock:
        with Path(path).open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(row, ensure_ascii=False) + "\n")


def classify_error(exc: BaseException, retries_exhausted: bool = False) -> str:
    """
    실패를 리포트 집계 가능한 축으로 분류한다.
    주의: hits==0 은 실패가 아니다 — 임계값이 정상 동작한 결과이므로 호출하지 않는다.
    """
    name = type(exc).__name__

    if "Timeout" in name:
        return "timeout"
    if retries_exhausted:
        return "retry_exhausted"

    status = getattr(exc, "status_code", None) or getattr(
        getattr(exc, "response", None), "status_code", None
    )
    if isinstance(status, int):
        if 400 <= status < 500:
            return "http_4xx"
        if 500 <= status < 600:
            return "http_5xx"

    if "RateLimit" in name:
        return "http_4xx"  # 429
    if "Connection" in name:
        return "retry_exhausted"
    if isinstance(exc, (json.JSONDecodeError, ValueError, KeyError, AttributeError, IndexError)):
        return "parse_error"
    return "unknown"
