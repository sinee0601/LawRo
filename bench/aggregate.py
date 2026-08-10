"""
Phase 4 — 원시 JSONL 을 집계해 LawRo-latency-report.md 를 생성한다.

  .venv/bin/python bench/aggregate.py --raw bench/raw --out LawRo-latency-report.md

핵심 수치는 "총 지연에서 어느 구간이 몇 %를 차지했는가"다.
"""

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))

QUERIES = Path(__file__).resolve().parent / "queries.jsonl"
SEGMENTS = ["embed_ms", "search_ms", "generate_ms", "total_ms"]


def percentile(values: List[float], q: float) -> float:
    """선형보간 없는 nearest-rank. 표본 100건 규모에서 해석이 단순하다."""
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(1, int(-(-q * len(ordered) // 1)))  # ceil(q*n)
    return ordered[min(rank, len(ordered)) - 1]


def load_raw(raw_dir: Path):
    metas, samples = [], []
    for path in sorted(raw_dir.glob("run*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            (metas if row.get("type") == "meta" else samples).append(row)
    if not samples:
        print(f"샘플이 없습니다: {raw_dir}", file=sys.stderr)
        sys.exit(1)
    return metas, samples


def seg_table(samples: List[Dict[str, Any]]) -> str:
    total_p50 = statistics.median([s["total_ms"] for s in samples])
    lines = [
        "| 구간 | p50 (ms) | p95 (ms) | max (ms) | 평균 | total p50 대비 점유율 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for seg in SEGMENTS:
        vals = [s[seg] for s in samples]
        p50 = statistics.median(vals)
        share = f"{p50 / total_p50 * 100:.1f}%" if seg != "total_ms" else "100.0%"
        label = {"embed_ms": "embed (질의 임베딩 API)", "search_ms": "search (Chroma 벡터 검색)",
                 "generate_ms": "generate (solar-pro2 생성)", "total_ms": "**total**"}[seg]
        lines.append(
            f"| {label} | {p50:.1f} | {percentile(vals, 0.95):.1f} | {max(vals):.1f} | "
            f"{statistics.mean(vals):.1f} | {share} |"
        )
    return "\n".join(lines)


def run_table(samples: List[Dict[str, Any]]) -> str:
    by_run = defaultdict(list)
    for s in samples:
        by_run[s["run"]].append(s)

    lines = [
        "| 회차 | 상태 | n | embed p50 | search p50 | search max | generate p50 | total p50 | total p95 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for run in sorted(by_run):
        rows = by_run[run]
        phase = "cold" if run == 1 else "warm"
        med = lambda key: statistics.median([r[key] for r in rows])  # noqa: E731
        lines.append(
            f"| run{run} | {phase} | {len(rows)} | {med('embed_ms'):.1f} | {med('search_ms'):.1f} | "
            f"{max(r['search_ms'] for r in rows):.1f} | {med('generate_ms'):.1f} | "
            f"{med('total_ms'):.1f} | {percentile([r['total_ms'] for r in rows], 0.95):.1f} |"
        )
    return "\n".join(lines)


def lang_table(samples: List[Dict[str, Any]], queries: Dict[str, Dict]) -> str:
    by_lang = defaultdict(list)
    for s in samples:
        by_lang[s["lang"]].append(s)

    lines = ["| 언어 | n | embed p50 | total p50 | 관련 질의 hits:0 비율 |", "|---|---:|---:|---:|---:|"]
    for lang in sorted(by_lang):
        rows = by_lang[lang]
        rel = [r for r in rows if queries[r["query_id"]]["category"] != "irrelevant"]
        miss = sum(1 for r in rel if r["hits"] == 0)
        ratio = f"{miss}/{len(rel)} ({miss / len(rel) * 100:.0f}%)" if rel else "-"
        lines.append(
            f"| {lang} | {len(rows)} | {statistics.median([r['embed_ms'] for r in rows]):.1f} | "
            f"{statistics.median([r['total_ms'] for r in rows]):.1f} | {ratio} |"
        )
    return "\n".join(lines)


def threshold_section(samples: List[Dict[str, Any]], queries: Dict[str, Dict]) -> str:
    irrelevant = [s for s in samples if queries[s["query_id"]]["category"] == "irrelevant"]
    relevant = [s for s in samples if queries[s["query_id"]]["category"] != "irrelevant"]

    blocked = sum(1 for s in irrelevant if s["hits"] == 0)
    missed = [s for s in relevant if s["hits"] == 0]

    irr_scores = [s["top_score"] for s in irrelevant if s["top_score"] is not None]
    rel_scores = [s["top_score"] for s in relevant if s["top_score"] is not None]

    out = [
        f"- 무관 질의 **{blocked}/{len(irrelevant)}건 차단** (`hits:0`) — 기대값 대비 "
        f"{'일치' if blocked == len(irrelevant) else '불일치'}",
        f"- 관련 질의 중 `hits:0` 오탐 **{len(missed)}/{len(relevant)}건** "
        f"({len(missed) / len(relevant) * 100:.1f}%)",
        f"- top_score 분포 — 무관: max {max(irr_scores):.3f} / 관련: min {min(rel_scores):.3f}, "
        f"p50 {statistics.median(rel_scores):.3f}",
    ]

    if missed:
        by_query = defaultdict(list)
        for s in missed:
            by_query[s["query_id"]].append(s["top_score"])
        out.append("\n오탐이 난 관련 질의(3회차 중 1회 이상):\n")
        out.append("| query_id | 언어 | 카테고리 | 질의 | top_score (회차별) |")
        out.append("|---|---|---|---|---|")
        for qid in sorted(by_query):
            q = queries[qid]
            scores = ", ".join(f"{v:.3f}" if v is not None else "-" for v in by_query[qid])
            out.append(f"| {qid} | {q['lang']} | {q['category']} | {q['text']} | {scores} |")
    return "\n".join(out)


def success_section(samples: List[Dict[str, Any]]) -> str:
    ok = sum(1 for s in samples if s["status"] == "ok")
    errors = Counter(s["error_type"] for s in samples if s["status"] != "ok")
    retries = sum(1 for s in samples if s.get("retry_count", 0) > 0)

    out = [
        f"- 전체 성공률 **{ok}/{len(samples)} ({ok / len(samples) * 100:.1f}%)**",
        f"- 재시도 발생 건수: {retries}건",
        "- `hits:0`은 실패로 세지 않는다 — 임계값이 정상 동작한 결과이므로 `status:\"ok\"`이며 아래 임계값 항목에서 따로 집계한다.",
    ]
    if errors:
        out.append("\n| error_type | 건수 |")
        out.append("|---|---:|")
        for name, n in errors.most_common():
            out.append(f"| `{name}` | {n} |")
    else:
        out.append("- `error_type` 발생 없음 (http_4xx / http_5xx / timeout / retry_exhausted / parse_error 모두 0건)")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default="bench/raw")
    parser.add_argument("--out", default="LawRo-latency-report.md")
    args = parser.parse_args()

    metas, samples = load_raw(Path(args.raw))
    queries = {
        json.loads(line)["query_id"]: json.loads(line)
        for line in QUERIES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }

    meta = metas[0]
    build_meta_path = Path("backend/data/chroma/_build_meta.json")
    build = json.loads(build_meta_path.read_text(encoding="utf-8")) if build_meta_path.exists() else {}

    total_p50 = statistics.median([s["total_ms"] for s in samples])
    embed_p50 = statistics.median([s["embed_ms"] for s in samples])
    search_p50 = statistics.median([s["search_ms"] for s in samples])
    generate_p50 = statistics.median([s["generate_ms"] for s in samples])

    doc = f"""# LawRo 챗봇 RAG 구간 지연 실측 리포트

측정일 {datetime.now().strftime('%Y-%m-%d')} · 커밋 `{meta['commit']}` · 브랜치 `measure/rag-latency`

## 한 줄 결론

로컬 단일 인스턴스에서 질의 100건을 순차 3회 실행한 결과, 총 지연 p50 {total_p50:.0f}ms 중
**generate(LLM 생성)가 {generate_p50 / total_p50 * 100:.0f}%, embed(질의 임베딩 API)가 {embed_p50 / total_p50 * 100:.0f}%,
search(Chroma 벡터 검색)가 {search_p50 / total_p50 * 100:.1f}%** 를 차지했다.
지연의 원인 구간은 **외부 API 왕복(generate + embed = {(generate_p50 + embed_p50) / total_p50 * 100:.0f}%)** 이며,
벡터 검색은 병목이 아니다.

## 실행 메타

| 항목 | 값 |
|---|---|
| 커밋 | `{meta['commit']}` |
| 샘플 수 | {len(samples)}건 ({len(metas)}회차 × {len(samples) // max(len(metas), 1)}질의) |
| 컬렉션 | `{meta['collection']}` / **{meta['collection_count']} vectors** |
| 원본 | 법령 {build.get('law_count', '?')}개 · 조문 {build.get('article_count', '?')}건 |
| 청킹 | size {build.get('chunk_size', '?')} / overlap {build.get('chunk_overlap', '?')} |
| 거리함수 | {meta['distance']} |
| 임계값 | **{meta['score_threshold']}** (측정 중 고정) |
| Top-k | {meta['top_k']} |
| 임베딩 (색인) | `{build.get('passage_model', '?')}` |
| 임베딩 (질의) | `{meta['embedding_model']}` |
| 생성 | `{meta['llm_model']}` |
| 요청 간격 | {meta['sleep_sec']}s, 순차 단일 실행 |

## 구간별 지연 (전 회차 통합, n={len(samples)})

{seg_table(samples)}

점유율은 각 구간 p50 을 total p50 으로 나눈 값이다. 구간 합이 total 과 정확히 일치하지는 않는다 —
세션 처리·프롬프트 조립 등 계측 구간 밖의 오버헤드가 남아 있기 때문이다.

## 회차 비교 (cold vs warm)

{run_table(samples)}

## 성공률

{success_section(samples)}

## 임계값 동작

{threshold_section(samples, queries)}

## 언어별

{lang_table(samples, queries)}

## 한계

- 로컬 단일 인스턴스(macOS, Python 3.9, Chroma 임베디드) — 실서비스 트래픽이 아니다.
- 순차 요청만 측정했다. **동시성·부하는 측정하지 않았다.**
- 질의 100건 규모, 3회차. 외부 API 지연은 측정 시점의 네트워크·서버 상태에 따라 달라진다.
- 세션 백엔드를 `memory` 로 고정했다(Firestore 자격증명 없음). Firestore 왕복은 total_ms 에 포함되지 않는다.
- 생성 구간은 응답 길이에 비례하므로 질의 구성에 의존한다.

## 재현

```bash
.venv/bin/python bench/fetch_laws.py
.venv/bin/python bench/build_index.py --reset
for r in 1 2 3; do .venv/bin/python bench/run_bench.py --run $r --out bench/raw/run$r.jsonl; done
.venv/bin/python bench/aggregate.py
```
"""

    Path(args.out).write_text(doc, encoding="utf-8")
    print(f"{args.out} 생성 완료 (샘플 {len(samples)}건)")
    print(f"  total p50 = {total_p50:.0f}ms")
    print(f"  embed {embed_p50 / total_p50 * 100:.0f}% / search {search_p50 / total_p50 * 100:.1f}% / generate {generate_p50 / total_p50 * 100:.0f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
