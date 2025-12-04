"""
LawRo Unified Backend - Main Application
FastAPI application combining Auth, Chatbot, and Contract Analysis services
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from .config import settings
from .database import get_firebase
from .routers import auth, chat, contract, worktime, support_center
from .services.chat_service import ChatService

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting LawRo Unified Backend...")

    # Initialize Firebase
    try:
        firebase = get_firebase()
        if firebase.is_initialized():
            logger.info("Firebase initialized successfully")
        else:
            logger.warning("Firebase not initialized - check credentials")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")

    # Initialize ChatService (Phase 2)
    try:
        chat_service = ChatService()
        logger.info("ChatService initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ChatService: {e}")

    # Initialize ContractService (Phase 3)
    try:
        from .services.contract_service import ContractService
        contract_service = ContractService()
        logger.info("ContractService initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ContractService: {e}")

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down LawRo Unified Backend...")

    # Cleanup ChatService
    try:
        if 'chat_service' in locals():
            await chat_service.cleanup()
            logger.info("ChatService cleanup complete")
    except Exception as e:
        logger.error(f"ChatService cleanup error: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Unified API service for AI legal consultation and contract analysis",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# CORS Middleware
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/chat", tags=["Chatbot"])
app.include_router(contract.router, prefix="/contract", tags=["Contract Analysis"])
app.include_router(worktime.router, tags=["Work Time Tracking"])
app.include_router(support_center.router, prefix="/support", tags=["Support Centers"])


# Root endpoint
@app.get("/")
async def root():
    """API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    Returns the status of all services
    """
    firebase = get_firebase()

    # Get ChatService health
    try:
        from .routers.chat import get_chat_service
        chat_service = get_chat_service()
        chat_health = await chat_service.get_health_status()
        chatbot_status = "healthy" if chat_health["overall_status"] else "degraded"
        chatbot_components = chat_health["components"]
    except Exception as e:
        logger.error(f"ChatService health check failed: {e}")
        chatbot_status = "unavailable"
        chatbot_components = {}

    # Get ContractService health
    try:
        from .routers.contract import get_contract_service
        contract_service = get_contract_service()
        contract_health = contract_service.get_health_status()
        contract_status = "healthy" if all(
            v in ["healthy", "not_configured"] for v in contract_health.values()
        ) else "degraded"
    except Exception as e:
        logger.error(f"ContractService health check failed: {e}")
        contract_status = "unavailable"
        contract_health = {}

    health_status = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "services": {
            "firebase": "healthy" if firebase.is_initialized() else "unavailable",
            "chatbot": chatbot_status,
            "contract": contract_status,
        },
        "chatbot_components": chatbot_components,
        "contract_components": contract_health
    }

    # Overall status
    all_healthy = all(
        svc_status == "healthy"
        for svc_status in health_status["services"].values()
    )

    if not all_healthy:
        health_status["status"] = "degraded"

    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(content=health_status, status_code=status_code)


# Statistics endpoint
@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    # Get ChatService stats
    try:
        from .routers.chat import get_chat_service
        chat_service = get_chat_service()
        chatbot_stats = chat_service.get_session_stats()
    except Exception as e:
        logger.error(f"Failed to get ChatService stats: {e}")
        chatbot_stats = {}

    return {
        "version": settings.APP_VERSION,
        "firebase_initialized": get_firebase().is_initialized(),
        "chatbot_stats": chatbot_stats,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
