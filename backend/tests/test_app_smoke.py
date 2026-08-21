"""
애플리케이션 기동 스모크 테스트.

외부 자격증명 없이 FastAPI 앱이 조립되고 5개 라우터가 빠짐없이 마운트되는지
확인한다. 임포트 단계에서만 검증하므로 Firebase/Upstage 호출은 없다.

라우트 집계는 app.routes(내부 구조)가 아니라 OpenAPI 스키마를 기준으로 한다.
Starlette 1.x부터 include_router가 하위 라우트를 평탄화하지 않아 내부 구조가
버전마다 다르지만, OpenAPI 스키마는 앱이 실제로 노출하는 계약이라 안정적이다.
"""

import pytest

fastapi_app = pytest.importorskip("app.main", reason="런타임 의존성 미설치")

HTTP_METHODS = {"get", "post", "put", "patch", "delete"}

EXPECTED_ROUTER_OPERATIONS = {
    "/auth": 11,
    "/chat": 8,
    "/contract": 6,
    "/worktime": 9,
    "/support": 5,
}

APP_LEVEL_PATHS = {"/", "/health", "/stats"}


@pytest.fixture(scope="module")
def schema():
    """OpenAPI 스키마 생성 자체가 응답 모델 전체에 대한 검증이다."""
    return fastapi_app.app.openapi()


@pytest.fixture(scope="module")
def operations(schema):
    """(경로, 메서드) 단위로 펼친 목록."""
    return [
        (path, method.upper())
        for path, item in schema["paths"].items()
        for method in item
        if method in HTTP_METHODS
    ]


def test_openapi_schema_builds(schema):
    assert schema["info"]["title"]
    assert schema["info"]["version"]


def test_app_level_endpoints_exist(schema):
    assert APP_LEVEL_PATHS <= schema["paths"].keys()


def test_all_routers_are_mounted(operations):
    for prefix, expected in EXPECTED_ROUTER_OPERATIONS.items():
        mounted = [op for op in operations if op[0].startswith(prefix + "/")]
        assert len(mounted) == expected, f"{prefix}: {expected}개 예상, {len(mounted)}개 마운트"


def test_total_operation_count(operations):
    # 라우터 39개 + 앱 레벨 3개(/ , /health, /stats)
    assert len(operations) == 42


def test_service_routers_expose_health_endpoints(schema):
    """외부 의존성을 가진 4개 서비스 라우터는 각자 health를 노출한다(auth 제외)."""
    for prefix in ("/chat", "/contract", "/worktime", "/support"):
        assert f"{prefix}/health" in schema["paths"], f"{prefix}: health 엔드포인트 없음"


def test_every_operation_declares_a_response(schema):
    for path, item in schema["paths"].items():
        for method, operation in item.items():
            if method in HTTP_METHODS:
                assert operation.get("responses"), f"{method.upper()} {path}: 응답 정의 없음"
