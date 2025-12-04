from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import os
from dotenv import load_dotenv

from services.user_service import UserService
from services.external_service import ExternalService
from database import create_tables
from routers import auth, contract, proxy

load_dotenv()

try:
    create_tables()
    print("✅ 데이터베이스 테이블 초기화 완료")
except Exception as e:
    print(f"⚠️ 데이터베이스 테이블 초기화 실패: {e}")

# FastAPI 앱 생성
app = FastAPI(
    title="LawRo 메인 API",
    description="LawRo 앱의 메인 API 서버 - 챗봇, 계약서 분석, 사용자 관리",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

external_service = ExternalService()
CONTRACT_SERVICE_URL = os.getenv("CONTRACT_SERVICE_URL", "http://3.106.213.23:8002")
CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", "http://chatbot:8001")

app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(contract.router, prefix="/contract", tags=["contract"])
app.include_router(proxy.router, tags=["proxy"])

@app.get("/")
async def root():
    """API 정보"""
    return {
        "message": "LawRo 메인 API",
        "version": "1.0.0",
        "docs": "/docs",
        "services": {
            "chatbot": CHATBOT_SERVICE_URL,
            "contract_analyzer": CONTRACT_SERVICE_URL
        },
        "proxy_endpoints": {
            "contract": "/contract/*",
            "chatbot": "/chat/*"
        }
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    # 외부 서비스 상태 확인
    chatbot_status = await external_service.check_chatbot_health()
    contract_status = await external_service.check_contract_health()
    
    return {
        "status": "healthy",
        "service": "LawRo Main API",
        "timestamp": time.time(),
        "external_services": {
            "chatbot": chatbot_status,
            "contract_analyzer": contract_status
        }
    }

app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(contract.router, prefix="/contract", tags=["contract"])
app.include_router(proxy.router, tags=["proxy"])



@app.get("/stats")
async def get_server_stats():
    """서버 통계 정보"""
    try:
        chatbot_stats = await external_service.get_chatbot_stats()
        user_service = UserService()
        user_stats = await user_service.get_user_stats()
        
        return {
            "success": True,
            "stats": {
                "users": user_stats,
                "chatbot": chatbot_stats,
                "timestamp": time.time()
            }
        }
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 