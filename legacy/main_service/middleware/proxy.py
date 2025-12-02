from fastapi import Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import os

from services.user_service import UserService

security = HTTPBearer()
user_service = UserService()

async def proxy_request(
    request: Request,
    target_url: str,
    timeout: float = 300.0,
    require_auth: bool = True
) -> Response:
    """
    범용 프록시 함수
    - 요청을 그대로 대상 서버로 전달
    - 응답을 그대로 클라이언트로 반환
    """
    try:
        if require_auth:
            auth_header = request.headers.get("authorization")
            if auth_header:
                try:
                    token = auth_header.replace("Bearer ", "")
                    await user_service.get_user_by_token(token)
                except Exception as e:
                    return Response(
                        content=f'{{"error": "인증 실패: {str(e)}"}}',
                        status_code=401,
                        media_type="application/json"
                    )
        
        headers = {
            key: value for key, value in request.headers.items()
            if key.lower() not in ['host', 'content-length']
        }
        
        body = await request.body()
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            proxy_response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params
            )
            
            response_headers = {
                key: value for key, value in proxy_response.headers.items()
                if key.lower() not in ['content-length', 'transfer-encoding', 'connection']
            }
            
            return Response(
                content=proxy_response.content,
                status_code=proxy_response.status_code,
                headers=response_headers,
                media_type=proxy_response.headers.get('content-type', 'application/json')
            )
            
    except httpx.TimeoutException:
        return Response(
            content='{"error": "요청 시간 초과"}',
            status_code=504,
            media_type="application/json"
        )
    except httpx.HTTPStatusError as e:
        return Response(
            content=e.response.content,
            status_code=e.response.status_code,
            media_type="application/json"
        )
    except Exception as e:
        return Response(
            content=f'{{"error": "프록시 오류: {str(e)}"}}',
            status_code=500,
            media_type="application/json"
        )