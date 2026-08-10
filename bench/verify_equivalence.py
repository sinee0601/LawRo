"""
Phase 1 전제 검증 — 계측용 분해가 운영 경로와 같은 결과를 내는지 확인한다.

운영 경로(chat_service.py:507):
    docs = await retriever.ainvoke(message)      # embed + search 가 한 덩어리

계측 경로(embed / search 분리):
    vec  = embedding.embed_query(message)                                   # embed
    raw  = vectorstore.similarity_search_by_vector_with_relevance_scores(vec, k)  # search
    docs = [d for d, dist in raw if (1.0 - dist) >= threshold]              # cosine 정규화

두 경로가 같은 문서를 같은 순서로 돌려주지 않으면 계측을 붙일 수 없다.

실행:
  .venv/bin/python bench/verify_equivalence.py
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_env, load_settings, resolve_persist_dir  # noqa: E402

PROBES = [
    "야간에 일하면 수당을 더 받나요?",
    "최저임금은 얼마인가요?",
    "고용주가 여권을 보관해도 되나요?",
    "일하다 다쳤는데 치료비는 누가 내나요?",
    "오늘 서울 날씨 어때?",  # 임계값 미달 → 양쪽 모두 0건이어야 한다
]


async def main() -> int:
    load_env()
    settings = load_settings()

    from langchain_chroma import Chroma
    from langchain_upstage import UpstageEmbeddings

    embedding = UpstageEmbeddings(
        model=settings.CHAT_EMBEDDING_MODEL, upstage_api_key=os.environ["UPSTAGE_API_KEY"]
    )
    vectorstore = Chroma(
        persist_directory=str(resolve_persist_dir(settings)),
        embedding_function=embedding,
        collection_name=settings.CHROMA_COLLECTION_NAME,
        collection_metadata={"hnsw:space": "cosine"},
    )
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": settings.CHAT_RETRIEVAL_K,
            "score_threshold": settings.CHAT_RETRIEVAL_SCORE_THRESHOLD,
        },
    )

    k = settings.CHAT_RETRIEVAL_K
    threshold = settings.CHAT_RETRIEVAL_SCORE_THRESHOLD
    all_match = True

    for query in PROBES:
        baseline = await retriever.ainvoke(query)

        vec = embedding.embed_query(query)
        raw = vectorstore.similarity_search_by_vector_with_relevance_scores(vec, k=k)
        split = [(doc, 1.0 - dist) for doc, dist in raw if (1.0 - dist) >= threshold]

        base_ids = [(d.metadata["law_name"], d.metadata["article_no"], d.metadata["chunk_index"]) for d in baseline]
        split_ids = [(d.metadata["law_name"], d.metadata["article_no"], d.metadata["chunk_index"]) for d, _ in split]
        base_text = [d.page_content for d in baseline]
        split_text = [d.page_content for d, _ in split]

        ok = base_ids == split_ids and base_text == split_text
        all_match &= ok
        mark = "OK " if ok else "MISMATCH"
        scores = ", ".join(f"{s:.4f}" for _, s in split) or "-"
        print(f"[{mark}] {query}")
        print(f"         운영={len(baseline)}건  계측={len(split)}건  scores=[{scores}]")
        if not ok:
            print(f"         운영 문서: {base_ids}")
            print(f"         계측 문서: {split_ids}")

    print("\n=== 판정 ===")
    if all_match:
        print("동일. 계측 분해를 적용해도 응답이 바뀌지 않는다.")
        return 0
    print("불일치. 분해 방식을 수정하기 전까지 계측을 붙이면 안 된다.")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
