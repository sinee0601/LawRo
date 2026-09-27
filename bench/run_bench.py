"""
Phase 3 — 벤치 실행 (순차 단일 실행)

  .venv/bin/python bench/run_bench.py --run 1 --out bench/raw/run1.jsonl

회차 규약:
  run 1 = cold  (프로세스 재시작 직후 첫 실행)
  run 2,3 = warm
  각 회차는 별도 프로세스로 실행해야 cold/warm 구분이 성립한다.

질의 순서는 회차별로 셔플하되 시드를 회차 번호로 고정한다 —
순서 효과와 캐시 효과를 분리하면서 재현성은 유지하기 위함.

동시 요청·부하 테스트는 범위 밖이다(외부 API 쿼터, 별도 과제).
"""

import argparse
import asyncio
import json
import os
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import BACKEND_ROOT, git_commit, load_env, load_settings, resolve_persist_dir  # noqa: E402

QUERIES = Path(__file__).resolve().parent / "queries.jsonl"


def collection_count(settings) -> int:
    import chromadb

    client = chromadb.PersistentClient(path=str(resolve_persist_dir(settings)))
    return client.get_collection(settings.CHROMA_COLLECTION_NAME).count()


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=int, required=True, help="회차 번호 (1=cold, 2·3=warm)")
    parser.add_argument("--out", required=True, help="원시 레코드 JSONL 경로")
    parser.add_argument("--sleep", type=float, default=1.0, help="요청 간 간격(초) — rate limit 방어")
    parser.add_argument("--limit", type=int, default=0, help="앞 N건만 실행(스모크용)")
    args = parser.parse_args()

    load_env()
    # Firestore 자격증명이 없는 로컬 측정이므로 세션은 메모리 백엔드로 고정한다.
    # embed/search/generate 구간에는 영향이 없다(리포트 '한계'에 명시).
    os.environ["SESSION_BACKEND"] = "memory"

    # CHROMA_PERSIST_DIRECTORY 는 "./data/chroma" 상대경로다. 운영에서는 backend/ 에서
    # 기동하므로 측정도 같은 CWD 여야 한다. 아니면 빈 컬렉션을 새로 만들어 붙잡는다.
    out_path = Path(args.out).resolve()
    os.chdir(BACKEND_ROOT)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        print(f"이미 존재합니다: {out_path}\n덮어쓰지 않습니다. 지우고 다시 실행하세요.", file=sys.stderr)
        return 1
    os.environ["BENCH_TRACE_PATH"] = str(out_path)

    settings = load_settings()
    sys.path.insert(0, str(BACKEND_ROOT))
    from app.services import rag_trace
    from app.services.chat_service import ChatService

    count = collection_count(settings)
    rag_trace.write_header(
        {
            "commit": git_commit(),
            "run": args.run,
            "phase": "cold" if args.run == 1 else "warm",
            "collection": settings.CHROMA_COLLECTION_NAME,
            "collection_count": count,
            "score_threshold": settings.CHAT_RETRIEVAL_SCORE_THRESHOLD,
            "top_k": settings.CHAT_RETRIEVAL_K,
            "distance": "cosine",
            "embedding_model": settings.CHAT_EMBEDDING_MODEL,
            "llm_model": settings.CHAT_LLM_MODEL,
            "sleep_sec": args.sleep,
            "seed": args.run,
        }
    )

    queries = [json.loads(line) for line in QUERIES.read_text(encoding="utf-8").splitlines() if line.strip()]
    random.Random(args.run).shuffle(queries)
    if args.limit:
        queries = queries[: args.limit]

    service = ChatService()
    print(f"run={args.run} ({'cold' if args.run == 1 else 'warm'})  질의 {len(queries)}건  count={count}")

    started = time.perf_counter()
    for i, query in enumerate(queries, start=1):
        rag_trace.set_context(run=args.run, query_id=query["query_id"], lang=query["lang"])
        try:
            # 세션을 매 질의마다 새로 만든다 — 대화 이력이 쌓이면 프롬프트가 길어져
            # generate 구간이 질의 순서에 오염된다.
            await service.process_message(
                message=query["text"],
                session_id=None,
                user_language=query["lang"],
            )
        except Exception as exc:  # 트레이스는 이미 기록됨. 실행은 계속한다.
            print(f"  [{query['query_id']}] 예외: {type(exc).__name__}: {exc}", file=sys.stderr)
        finally:
            rag_trace.clear_context()

        print(f"  {i}/{len(queries)} {query['query_id']}", end="\r", flush=True)
        if i < len(queries):
            await asyncio.sleep(args.sleep)

    elapsed = time.perf_counter() - started
    print(f"\n완료: {len(queries)}건 / {elapsed:.1f}s → {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
