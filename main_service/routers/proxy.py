from fastapi import APIRouter, Request
import os

from middleware.proxy import proxy_request

router = APIRouter()

CONTRACT_SERVICE_URL = os.getenv("CONTRACT_SERVICE_URL", "http://3.106.213.23:8002")
CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", "http://chatbot:8001")

@router.api_route("/chat/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def chatbot_proxy(request: Request, path: str):
    """
    챗봇 서비스 프록시
    /chat/* 요청을 챗봇 서버로 직접 전달
    """
    target_url = f"{CHATBOT_SERVICE_URL}/chat/{path}"
    return await proxy_request(request, target_url, timeout=60.0, require_auth=True)

@router.api_route("/contract/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def contract_api_proxy(request: Request, path: str):
    """
    계약서 분석 API 프록시
    /contract/api/* 요청을 계약서 분석 서버의 /api/*로 전달
    """
    target_url = f"{CONTRACT_SERVICE_URL}/api/{path}"
    return await proxy_request(request, target_url, timeout=300.0, require_auth=False)

@router.api_route("/contract/health", methods=["GET"])
async def contract_health_proxy(request: Request):
    """계약서 분석 서비스 헬스 체크 프록시"""
    target_url = f"{CONTRACT_SERVICE_URL}/health"
    return await proxy_request(request, target_url, timeout=10.0, require_auth=False)

@router.api_route("/contract/docs", methods=["GET"])
async def contract_docs_proxy(request: Request):
    """계약서 분석 서비스 API 문서 프록시"""
    target_url = f"{CONTRACT_SERVICE_URL}/docs"
    return await proxy_request(request, target_url, timeout=10.0, require_auth=False)

@router.api_route("/contract/redoc", methods=["GET"])
async def contract_redoc_proxy(request: Request):
    """계약서 분석 서비스 ReDoc 프록시"""
    target_url = f"{CONTRACT_SERVICE_URL}/redoc"
    return await proxy_request(request, target_url, timeout=10.0, require_auth=False)