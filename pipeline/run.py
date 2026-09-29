"""추출 실행 CLI.

    python -m pipeline.run --source seeds
    python -m pipeline.run --source laws --concurrency 8
    python -m pipeline.run --source laws --limit 20 --model solar-mini

이미 성공한 항목(같은 본문·모델·프롬프트)은 건너뛴다. 중간에 멈춰도 다시 실행하면 남은 것만 처리한다.
"""

from __future__ import annotations

import argparse
import asyncio
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

from pipeline.extract import cost_usd, plan_jobs, run_jobs
from pipeline.sources import load_law_items, load_seed_items
from pipeline.store import DEFAULT_DB, Store
from pipeline.taxonomy import REPO_ROOT, load_taxonomy


def _pct(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    return values[min(len(values) - 1, int(round(q * (len(values) - 1))))]


def summarize(rows: list[dict], model: str, wall_s: float) -> str:
    ok = [r for r in rows if r["status"] == "ok"]
    err = [r for r in rows if r["status"] != "ok"]
    p, c, o = (sum(r[k] or 0 for r in rows) for k in ("prompt_tokens", "cached_tokens", "completion_tokens"))
    cost = cost_usd(model, p, c, o)
    lat = [r["latency_ms"] for r in rows]
    issues = Counter(i.split(":")[0] for r in ok for i in r["issues"])
    retried = sum(1 for r in rows if (r["attempts"] or 1) > 1)
    lines = [
        f"호출 {len(rows)}건: 성공 {len(ok)} / 실패 {len(err)} / 재시도 발생 {retried}",
        f"토큰: 입력 {p:,} (캐시 {c:,}, {c / p:.0%}) / 출력 {o:,}" if p else "토큰: 0",
        f"비용: ${cost:.4f} (건당 ${cost / len(rows):.6f})" if cost is not None and rows else "비용: 단가 미등록 모델",
        f"API 지연: p50 {statistics.median(lat):.0f}ms / p95 {_pct(lat, 0.95):.0f}ms" if lat else "",
        f"처리량: {len(rows) / wall_s:.2f}건/s (벽시계 {wall_s:.1f}s)" if wall_s else "",
        f"검증 이슈: {dict(issues)}" if issues else "검증 이슈: 없음",
    ]
    for r in err[:5]:
        lines.append(f"  실패 {r['item_id']}: {r['error'][:200]}")
    return "\n".join(line for line in lines if line)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", choices=["seeds", "laws"], required=True)
    parser.add_argument("--model", default="solar-pro2")
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--limit", type=int, default=0, help="앞에서부터 N건만 (0 = 전체)")
    parser.add_argument("--db", default=str(DEFAULT_DB))
    args = parser.parse_args(argv)

    load_dotenv(REPO_ROOT / "backend" / ".env")
    tax = load_taxonomy()
    items = load_seed_items() if args.source == "seeds" else load_law_items()
    if args.limit:
        items = items[: args.limit]

    store = Store(Path(args.db))
    jobs = plan_jobs(tax, items, args.model)
    done = store.done_keys([j.key for j in jobs])
    todo = [j for j in jobs if j.key not in done]
    print(
        f"taxonomy v{tax.version} / model {args.model} / 대상 {len(jobs)}건 중 "
        f"캐시 {len(done)}건, 호출 {len(todo)}건 (동시성 {args.concurrency})",
        flush=True,
    )
    if not todo:
        return 0

    progress = {"n": 0}

    def on_done(row: dict) -> None:
        progress["n"] += 1
        if progress["n"] % 20 == 0 or progress["n"] == len(todo):
            print(f"  {progress['n']}/{len(todo)}", flush=True)

    started = time.perf_counter()
    rows = asyncio.run(run_jobs(tax, todo, args.model, store, args.concurrency, on_done))
    print(summarize(rows, args.model, time.perf_counter() - started))
    return 0 if all(r["status"] == "ok" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
