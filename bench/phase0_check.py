"""
Phase 0 점검 — 측정이 가능한 상태인지 확인한다.

  1) Chroma 컬렉션 존재 여부와 count / peek
  2) UPSTAGE_API_KEY 스모크 콜 (임베딩 1회 + solar-pro2 1회)
  3) 운영 설정값(임계값·Top-k·거리함수·모델명) 출력

실행:
  .venv/bin/python bench/phase0_check.py

API 키는 backend/.env 에서만 읽는다. 값은 출력하지 않는다.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import git_commit, load_env, load_settings, resolve_persist_dir  # noqa: E402


def check_collection(settings) -> bool:
    import chromadb

    persist_dir = resolve_persist_dir(settings)
    print(f"[1] Chroma persist: {persist_dir}")

    if not persist_dir.exists():
        print("    → 디렉터리 없음. 컬렉션 미구축.")
        return False

    client = chromadb.PersistentClient(path=str(persist_dir))
    names = [c.name for c in client.list_collections()]
    print(f"    컬렉션 목록: {names or '(없음)'}")

    if settings.CHROMA_COLLECTION_NAME not in names:
        print(f"    → '{settings.CHROMA_COLLECTION_NAME}' 없음. 컬렉션 미구축.")
        return False

    col = client.get_collection(settings.CHROMA_COLLECTION_NAME)
    count = col.count()
    print(f"    count = {count}")
    print(f"    metadata = {col.metadata}")

    if count:
        peek = col.peek(3)
        for doc, md in zip(peek["documents"], peek["metadatas"]):
            head = doc.replace("\n", " ")[:70]
            print(f"      - {md.get('law_name','?')} {md.get('article_no','?')}: {head}...")
    return count > 0


def check_api(settings) -> bool:
    key = os.getenv("UPSTAGE_API_KEY")
    print("\n[2] UPSTAGE_API_KEY 스모크 콜")
    if not key:
        print("    → 키 없음. backend/.env 에 UPSTAGE_API_KEY 추가 필요.")
        return False

    ok = True
    try:
        from langchain_upstage import UpstageEmbeddings

        vec = UpstageEmbeddings(
            model=settings.CHAT_EMBEDDING_MODEL, upstage_api_key=key
        ).embed_query("최저임금은 얼마인가요")
        print(f"    임베딩 OK — model={settings.CHAT_EMBEDDING_MODEL}, dim={len(vec)}")
    except Exception as exc:
        print(f"    임베딩 실패 — {type(exc).__name__}: {exc}")
        ok = False

    try:
        from openai import OpenAI

        resp = OpenAI(api_key=key, base_url="https://api.upstage.ai/v1", timeout=30.0).chat.completions.create(
            model=settings.CHAT_LLM_MODEL,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
        )
        print(f"    생성 OK — model={settings.CHAT_LLM_MODEL}, tokens={resp.usage.total_tokens}")
    except Exception as exc:
        print(f"    생성 실패 — {type(exc).__name__}: {exc}")
        ok = False

    return ok


def main() -> int:
    load_env()
    settings = load_settings()

    print(f"commit = {git_commit()}\n")
    has_collection = check_collection(settings)
    has_api = check_api(settings)

    print("\n[3] 운영 설정 (측정 중 고정)")
    print(f"    collection        = {settings.CHROMA_COLLECTION_NAME}")
    print(f"    score_threshold   = {settings.CHAT_RETRIEVAL_SCORE_THRESHOLD}")
    print(f"    top_k             = {settings.CHAT_RETRIEVAL_K}")
    print(f"    distance          = cosine (chat_service.py:188)")
    print(f"    embedding (query) = {settings.CHAT_EMBEDDING_MODEL}")
    print(f"    llm               = {settings.CHAT_LLM_MODEL}")

    print("\n=== 판정 ===")
    if has_collection and has_api:
        print("Phase 1 진행 가능.")
        return 0
    if not has_collection:
        print("컬렉션 없음 → bench/fetch_laws.py → bench/build_index.py 로 재구축 필요.")
    if not has_api:
        print("API 키 미확보 → 임베딩·생성 모두 불가.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
