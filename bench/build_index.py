"""
수집한 조문을 청킹·임베딩해서 ChromaDB 컬렉션을 재구축한다.

전제: bench/fetch_laws.py 를 먼저 실행해 backend/data/raw_laws/*.json 이 있어야 한다.

실행:
  .venv/bin/python bench/build_index.py            # 기존 컬렉션이 있으면 중단
  .venv/bin/python bench/build_index.py --reset    # 컬렉션 삭제 후 재구축

임베딩 모델 주의:
  Upstage solar-embedding-1-large 는 비대칭 모델이다.
  - 문서(색인) 측: solar-embedding-1-large-passage
  - 질의(검색) 측: solar-embedding-1-large-query  <- backend/app/config.py 의 운영값
  운영 코드를 건드리지 않고 색인만 passage 로 넣는 것이 설계 의도에 맞다.

산출물:
  backend/data/chroma/                  — persist 디렉터리 (config.py CHROMA_PERSIST_DIRECTORY)
  backend/data/chroma/_build_meta.json  — 청크 설정·건수·모델명 (리포트 헤더용)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import BACKEND_ROOT, load_env, load_settings, resolve_persist_dir  # noqa: E402

RAW_DIR = BACKEND_ROOT / "data" / "raw_laws"

# 청크 설정 — 이 값이 곧 지원서에 쓸 값이 된다. 바꾸면 리포트도 같이 바꿔야 한다.
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
PASSAGE_MODEL = "solar-embedding-1-large-passage"
EMBED_BATCH = 32  # Upstage 임베딩 API 배치 상한 방어


def load_articles() -> List[Dict[str, Any]]:
    if not RAW_DIR.exists():
        print(f"원본 조문이 없습니다: {RAW_DIR}\n먼저 bench/fetch_laws.py 를 실행하세요.", file=sys.stderr)
        sys.exit(1)

    articles: List[Dict[str, Any]] = []
    for path in sorted(RAW_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        articles.extend(json.loads(path.read_text(encoding="utf-8")))

    if not articles:
        print(f"조문 0건: {RAW_DIR}", file=sys.stderr)
        sys.exit(1)
    return articles


def chunk(articles: List[Dict[str, Any]]):
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    texts: List[str] = []
    metadatas: List[Dict[str, Any]] = []
    ids: List[str] = []

    for article in articles:
        # 검색 결과에 출처가 보이도록 조문 헤더를 본문에 포함시킨다
        header = f"{article['law_name']} {article['article_no']}"
        if article.get("article_title"):
            header += f"({article['article_title']})"
        full = f"{header}\n{article['text']}"

        pieces = splitter.split_text(full)
        for i, piece in enumerate(pieces):
            texts.append(piece)
            metadatas.append(
                {
                    "law_name": article["law_name"],
                    "article_no": article["article_no"],
                    "article_title": article.get("article_title", ""),
                    "enforce_date": article.get("enforce_date", ""),
                    "source_url": article.get("source_url", ""),
                    "chunk_index": i,
                }
            )
            ids.append(f"{article['law_name']}|{article['article_no']}|{i}")

    return texts, metadatas, ids


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="기존 컬렉션을 삭제하고 재구축")
    args = parser.parse_args()

    load_env()
    if not os.getenv("UPSTAGE_API_KEY"):
        print("UPSTAGE_API_KEY 가 없습니다. backend/.env 에 넣어주세요.", file=sys.stderr)
        return 1

    settings = load_settings()
    persist_dir = resolve_persist_dir(settings)

    import chromadb
    from langchain_upstage import UpstageEmbeddings

    persist_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(persist_dir))

    existing = [c.name for c in client.list_collections()]
    if settings.CHROMA_COLLECTION_NAME in existing:
        if not args.reset:
            col = client.get_collection(settings.CHROMA_COLLECTION_NAME)
            print(
                f"컬렉션이 이미 있습니다: {settings.CHROMA_COLLECTION_NAME} "
                f"(count={col.count()})\n덮어쓰려면 --reset 을 붙이세요.",
                file=sys.stderr,
            )
            return 1
        client.delete_collection(settings.CHROMA_COLLECTION_NAME)
        print(f"기존 컬렉션 삭제: {settings.CHROMA_COLLECTION_NAME}")

    # 운영 코드(chat_service.py:188)와 동일하게 cosine 으로 생성
    collection = client.create_collection(
        name=settings.CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    articles = load_articles()
    texts, metadatas, ids = chunk(articles)
    print(f"조문 {len(articles)}건 → 청크 {len(texts)}개 (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")

    embedder = UpstageEmbeddings(model=PASSAGE_MODEL, upstage_api_key=os.environ["UPSTAGE_API_KEY"])

    started = time.perf_counter()
    for start in range(0, len(texts), EMBED_BATCH):
        batch_texts = texts[start : start + EMBED_BATCH]
        vectors = embedder.embed_documents(batch_texts)
        collection.add(
            ids=ids[start : start + EMBED_BATCH],
            documents=batch_texts,
            metadatas=metadatas[start : start + EMBED_BATCH],
            embeddings=vectors,
        )
        done = min(start + EMBED_BATCH, len(texts))
        print(f"  임베딩 {done}/{len(texts)}", end="\r", flush=True)

    elapsed = time.perf_counter() - started
    count = collection.count()
    print(f"\n완료: {count} vectors / {elapsed:.1f}s → {persist_dir}")

    meta = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "collection": settings.CHROMA_COLLECTION_NAME,
        "persist_dir": str(persist_dir),
        "vector_count": count,
        "article_count": len(articles),
        "law_count": len(list(RAW_DIR.glob("[!_]*.json"))),
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "distance": "cosine",
        "passage_model": PASSAGE_MODEL,
        "query_model": settings.CHAT_EMBEDDING_MODEL,
        "top_k": settings.CHAT_RETRIEVAL_K,
        "score_threshold": settings.CHAT_RETRIEVAL_SCORE_THRESHOLD,
        "build_seconds": round(elapsed, 1),
    }
    (persist_dir / "_build_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
