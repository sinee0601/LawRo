"""
계약서 분석 경로의 실행 모델 회귀 테스트.

이 경로는 페이지당 최대 60초가 걸리는 외부 OCR 호출과 Firestore I/O를 포함한다.
이벤트 루프에서 직접 실행되면 처리 시간 내내 서버 전체가 다른 요청을 받지 못한다.

지키려는 규칙 두 가지:
  1) await 없이 동기 I/O만 하는 라우터 핸들러는 `def` 로 선언한다 (FastAPI가 스레드풀 실행)
  2) async 서비스 메서드 안의 블로킹 호출은 run_in_threadpool 로 넘긴다
"""

import ast
import inspect
from pathlib import Path

import pytest

contract_router = pytest.importorskip("app.routers.contract", reason="런타임 의존성 미설치")

SERVICE_SOURCE = Path(__file__).resolve().parent.parent / "app" / "services" / "contract_service.py"

# 스레드풀로 넘겨야 하는 블로킹 헬퍼 (외부 HTTP / Firestore)
MUST_BE_OFFLOADED = {"_process_ocr", "_parse_with_solar", "_get_saved_analysis", "_save_analysis"}


def analyze_function() -> ast.AsyncFunctionDef:
    tree = ast.parse(SERVICE_SOURCE.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "analyze_contract_with_chatbot":
            return node
    pytest.fail("analyze_contract_with_chatbot 를 찾지 못했다")


def self_method_name(node: ast.AST):
    """self._foo 형태면 '_foo' 를 돌려준다."""
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self":
        return node.attr
    return None


# --- 라우터 핸들러 실행 모델 -------------------------------------------


@pytest.mark.parametrize("handler", ["upload_contract", "get_analysis_history", "delete_analysis", "health_check"])
def test_blocking_handlers_are_sync(handler):
    """동기 I/O만 하는 핸들러는 def 여야 스레드풀에서 돈다."""
    fn = getattr(contract_router, handler)
    assert not inspect.iscoroutinefunction(fn), f"{handler}: async def 로 되돌아가면 이벤트 루프를 막는다"


@pytest.mark.parametrize("handler", ["analyze_with_chatbot", "get_chatbot_status"])
def test_awaiting_handlers_stay_async(handler):
    fn = getattr(contract_router, handler)
    assert inspect.iscoroutinefunction(fn)


# --- 서비스 계층 오프로딩 ----------------------------------------------


def test_blocking_calls_are_offloaded_to_threadpool():
    offloaded = set()
    for node in ast.walk(analyze_function()):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "run_in_threadpool":
            if node.args:
                name = self_method_name(node.args[0])
                if name:
                    offloaded.add(name)
    missing = MUST_BE_OFFLOADED - offloaded
    assert not missing, f"run_in_threadpool 로 넘기지 않은 블로킹 호출: {sorted(missing)}"


def test_blocking_helpers_are_not_called_directly():
    """self._process_ocr(...) 처럼 직접 호출하면 이벤트 루프에서 실행된다."""
    direct = set()
    for node in ast.walk(analyze_function()):
        if isinstance(node, ast.Call):
            name = self_method_name(node.func)
            if name in MUST_BE_OFFLOADED:
                direct.add(name)
    assert not direct, f"이벤트 루프에서 직접 호출되고 있다: {sorted(direct)}"


def test_offloaded_helpers_remain_synchronous():
    """스레드풀에 넘기는 대상은 동기 함수여야 한다 (코루틴이면 실행되지 않는다)."""
    tree = ast.parse(SERVICE_SOURCE.read_text(encoding="utf-8"))
    kinds = {
        node.name: type(node).__name__
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in MUST_BE_OFFLOADED
    }
    for name in MUST_BE_OFFLOADED:
        assert kinds.get(name) == "FunctionDef", f"{name}: 동기 def 여야 한다 (현재 {kinds.get(name)})"
