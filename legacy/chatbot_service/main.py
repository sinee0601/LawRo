from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import traceback
from typing import Dict, Any, Optional
import os
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from models import ChatRequest, ChatResponse, ChatMessage
from chat_service import ChatService
from config import Config
from logging_config import setup_default_logging, get_logger

# 환경 변수 로드
load_dotenv()

# 로거 설정
logger = setup_default_logging()

# 전역 변수
chat_service: Optional[ChatService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 생명주기 관리"""
    global chat_service
    
    # 시작 시
    logger.info("🚀 LawRo 챗봇 서비스 시작")
    try:
        chat_service = ChatService()
        logger.info("✅ ChatService 초기화 완료")
    except Exception as e:
        logger.error(f"❌ ChatService 초기화 실패: {e}")
        raise
    
    yield
    
    # 종료 시
    logger.info("🛑 LawRo 챗봇 서비스 종료")
    if chat_service:
        await chat_service.cleanup()
        logger.info("✅ ChatService 정리 완료")


# FastAPI 앱 생성
app = FastAPI(
    title="LawRo 챗봇 API",
    description="법률 상담 챗봇 서비스 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 전역 예외 처리기
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """전역 예외 처리"""
    error_id = f"error_{int(time.time())}"
    logger.error(
        f"🚨 예외 발생 [ID: {error_id}] | {request.method} {request.url} | "
        f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "서버 내부 오류가 발생했습니다.",
            "error_id": error_id,
            "detail": str(exc) if Config.DEBUG else "Internal Server Error"
        }
    )

@app.get("/")
async def root():
    """API 정보"""
    logger.info("📋 API 정보 요청")
    return {
        "message": "LawRo 챗봇 API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "environment": Config.ENVIRONMENT,
        "timestamp": time.time()
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    try:
        if not chat_service:
            raise HTTPException(status_code=503, detail="ChatService가 초기화되지 않았습니다")
        
        health_info = await chat_service.get_health_status()
        logger.debug("💚 헬스 체크 요청 처리")
        
        return {
            "status": "healthy" if health_info["overall_status"] else "unhealthy",
            "service": "LawRo Chatbot",
            "timestamp": time.time(),
            "components": health_info["components"],
            "session_stats": health_info["session_stats"]
        }
    except Exception as e:
        logger.error(f"❌ 헬스 체크 실패: {e}")
        raise HTTPException(status_code=503, detail=f"서비스 상태 확인 실패: {str(e)}")

# 기존 /chat 엔드포인트는 /chat/send로 통합됨

@app.post("/chat/send", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """
    채팅 메시지를 보내고 AI 응답을 받습니다.
    """
    start_time = time.time()
    session_short_id = (request.session_id or "new")[:8]
    
    logger.info(f"💬 채팅 요청 [세션: {session_short_id}] | 메시지: {request.message[:50]}...")
    
    if not chat_service:
        logger.error("❌ ChatService가 초기화되지 않았습니다")
        raise HTTPException(status_code=503, detail="서비스가 준비되지 않았습니다")
    
    try:
        # 입력 검증
        if not request.message or not request.message.strip():
            raise ValueError("메시지가 비어있습니다")
        
        if len(request.message) > 5000:  # 메시지 길이 제한
            raise ValueError("메시지가 너무 깁니다 (최대 5000자)")
        
        # 챗봇 응답 생성
        response_message, chat_history = await chat_service.process_message(
            message=request.message.strip(),
            session_id=request.session_id,
            custom_prompt=request.custom_prompt,
            user_language=request.user_language or "korean"
        )
        
        processing_time = time.time() - start_time
        
        logger.info(
            f"✅ 채팅 응답 완료 [세션: {session_short_id}] | "
            f"처리 시간: {processing_time:.2f}s | "
            f"응답 길이: {len(response_message)}자"
        )
        
        return ChatResponse(
            success=True,
            message=response_message,
            chat_history=chat_history,
            processing_time=processing_time
        )
        
    except ValueError as ve:
        processing_time = time.time() - start_time
        logger.warning(f"⚠️ 입력 검증 오류 [세션: {session_short_id}]: {ve}")
        
        return ChatResponse(
            success=False,
            message=f"입력 오류: {str(ve)}",
            chat_history=[],
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"❌ 채팅 처리 오류 [세션: {session_short_id}]: {e}\n{traceback.format_exc()}")
        
        return ChatResponse(
            success=False,
            message="죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
            chat_history=[],
            processing_time=processing_time
        )

@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """특정 세션의 채팅 히스토리를 조회합니다."""
    session_short_id = session_id[:8]
    logger.info(f"📚 히스토리 조회 요청 [세션: {session_short_id}]")
    
    if not chat_service:
        raise HTTPException(status_code=503, detail="서비스가 준비되지 않았습니다")
    
    try:
        # 입력 검증
        if not session_id or len(session_id) < 8:
            raise ValueError("올바르지 않은 세션 ID입니다")
        
        history = await chat_service.get_chat_history(session_id)
        
        logger.info(f"✅ 히스토리 조회 완료 [세션: {session_short_id}] | 메시지 수: {len(history)}")
        
        return {
            "success": True,
            "session_id": session_id,
            "chat_history": history,
            "message_count": len(history)
        }
    except ValueError as ve:
        logger.warning(f"⚠️ 히스토리 조회 입력 오류 [세션: {session_short_id}]: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"❌ 히스토리 조회 오류 [세션: {session_short_id}]: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"채팅 히스토리 조회 중 오류가 발생했습니다: {str(e)}"
        )

# 기존 /create_session 엔드포인트는 /chat/new-session으로 통합됨

@app.post("/chat/new-session")
async def create_new_chat_session():
    """새로운 채팅 세션을 생성합니다."""
    logger.info("🆕 새 세션 생성 요청")
    
    if not chat_service:
        raise HTTPException(status_code=503, detail="서비스가 준비되지 않았습니다")
    
    try:
        session_id = await chat_service.create_new_session()
        session_short_id = session_id[:8]
        
        logger.info(f"✅ 새 세션 생성 완료 [세션: {session_short_id}]")
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "새로운 채팅 세션이 생성되었습니다."
        }
    except Exception as e:
        logger.error(f"❌ 세션 생성 오류: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"세션 생성 중 오류가 발생했습니다: {str(e)}"
        )

@app.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """특정 세션의 채팅 히스토리를 삭제합니다."""
    session_short_id = session_id[:8]
    logger.info(f"🗑️ 히스토리 삭제 요청 [세션: {session_short_id}]")
    
    if not chat_service:
        raise HTTPException(status_code=503, detail="서비스가 준비되지 않았습니다")
    
    try:
        # 입력 검증
        if not session_id or len(session_id) < 8:
            raise ValueError("올바르지 않은 세션 ID입니다")
        
        success = await chat_service.clear_chat_history(session_id)
        
        if success:
            logger.info(f"✅ 히스토리 삭제 완료 [세션: {session_short_id}]")
        else:
            logger.warning(f"⚠️ 히스토리 삭제 실패 [세션: {session_short_id}] - 세션을 찾을 수 없음")
        
        return {
            "success": success,
            "message": "채팅 히스토리가 삭제되었습니다." if success else "삭제에 실패했습니다. 세션을 찾을 수 없습니다.",
            "session_id": session_id
        }
    except ValueError as ve:
        logger.warning(f"⚠️ 히스토리 삭제 입력 오류 [세션: {session_short_id}]: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"❌ 히스토리 삭제 오류 [세션: {session_short_id}]: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"채팅 히스토리 삭제 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/stats")
async def get_server_stats():
    """서버 통계 정보를 조회합니다."""
    logger.info("📊 서버 통계 조회 요청")
    
    if not chat_service:
        raise HTTPException(status_code=503, detail="서비스가 준비되지 않았습니다")
    
    try:
        stats = chat_service.get_session_stats()
        
        logger.info(f"✅ 통계 조회 완료 | 활성 세션: {stats.get('total_sessions', 0)}")
        
        return {
            "success": True,
            "stats": stats,
            "server_info": {
                "environment": Config.ENVIRONMENT,
                "debug_mode": Config.DEBUG,
                "uptime": time.time()
            }
        }
    except Exception as e:
        logger.error(f"❌ 통계 조회 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 서버 시작 | 환경: {Config.ENVIRONMENT} | 포트: {Config.CHATBOT_SERVICE_PORT}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=Config.CHATBOT_SERVICE_PORT,
        reload=Config.DEBUG,
        log_level="info" if not Config.DEBUG else "debug",
        access_log=Config.DEBUG
    ) 