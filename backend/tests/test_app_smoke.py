"""
애플리케이션 기동 스모크 테스트.

외부 자격증명 없이도 FastAPI 앱 객체가 조립되는지, 5개 라우터가 빠짐없이
마운트되는지 확인한다. 임포트 단계에서만 검증하므로 Firebase/Upstage 호출은 없다.
"""

import pytest

fastapi_app = pytest.importorskip("app.main", reason="런타임 의존성 미설치")

EXPECTED_ROUTER_ENDPOINTS = {
    "/auth": 11,
    "/chat": 8,
    "/contract": 6,
    "/worktime": 9,
    "/support": 5,
}

DOCS_PATHS = {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}


@pytest.fixture(scope="module")
def routes():
    return [r for r in fastapi_app.app.routes if hasattr(r, "methods")]


def test_app_metadata():
    assert fastapi_app.app.title


def test_root_and_health_endpoints_exist(routes):
    paths = {r.path for r in routes}
    assert {"/", "/health", "/stats"} <= paths


def test_all_routers_are_mounted(routes):
    for prefix, expected in EXPECTED_ROUTER_ENDPOINTS.items():
        mounted = [r for r in routes if r.path.startswith(prefix + "/")]
        assert len(mounted) == expected, f"{prefix}: {expected}개 예상, {len(mounted)}개 마운트"


def test_total_api_endpoint_count(routes):
    api_routes = [r for r in routes if r.path not in DOCS_PATHS]
    # 라우터 39개 + 앱 레벨 3개(/ , /health, /stats)
    assert len(api_routes) == 42


def test_service_routers_expose_health_endpoints(routes):
    """외부 의존성을 가진 4개 서비스 라우터는 각자 health를 노출한다(auth 제외)."""
    paths = {r.path for r in routes}
    for prefix in ("/chat", "/contract", "/worktime", "/support"):
        assert f"{prefix}/health" in paths, f"{prefix}: health 엔드포인트 없음"


def test_no_duplicate_path_method_pairs(routes):
    seen = set()
    for r in routes:
        for method in r.methods - {"HEAD", "OPTIONS"}:
            key = (method, r.path)
            assert key not in seen, f"중복 라우트: {key}"
            seen.add(key)
