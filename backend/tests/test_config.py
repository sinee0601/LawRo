"""
설정 기본값 회귀 테스트.

발표자료·문서에 인용되는 RAG 파라미터가 코드에서 조용히 바뀌는 것을 막는다.
로컬 .env 값에 영향받지 않도록 인스턴스가 아닌 '선언된 기본값'을 검증한다.
"""

import pytest

from app.config import Settings


def default_of(name: str):
    return Settings.model_fields[name].default


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("CHAT_RETRIEVAL_K", 2),
        ("CHAT_RETRIEVAL_SCORE_THRESHOLD", 0.3),
        ("CHAT_LLM_MODEL", "solar-pro2"),
        ("CHAT_EMBEDDING_MODEL", "solar-embedding-1-large-query"),
        ("CHROMA_COLLECTION_NAME", "lawro_legal_docs"),
    ],
)
def test_rag_defaults(field, expected):
    assert default_of(field) == expected


def test_retrieval_threshold_is_a_valid_cosine_score():
    threshold = default_of("CHAT_RETRIEVAL_SCORE_THRESHOLD")
    assert 0.0 < threshold < 1.0


def test_session_limits():
    assert default_of("CHAT_MAX_SESSIONS") == 1000
    assert default_of("CHAT_MAX_MESSAGES") == 50
    assert default_of("CHAT_SESSION_TIMEOUT") == 300


def test_contract_upload_limits():
    assert default_of("CONTRACT_MAX_FILE_SIZE") == 10 * 1024 * 1024
    extensions = default_of("CONTRACT_ALLOWED_EXTENSIONS").split(",")
    assert sorted(extensions) == [".jpeg", ".jpg", ".pdf", ".png"]


def test_workplace_default_radius():
    from app.models.worktime import WorkplaceLocation

    assert WorkplaceLocation.model_fields["radius_meters"].default == 500
