from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import upload, analyze, template
import time
import logging
from utils.s3_utils import test_s3_connection
from config.settings import S3_BUCKET_NAME

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LawRo 계약서 분석 API",
    description="계약서 OCR 및 분석 서비스 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 추가
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(template.router, prefix="/api", tags=["template"])

@app.get("/")
def root():
    return {
        "message": "Contract Analyzer API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
def health_check():
    try:
        # S3 연결 테스트
        s3_status = "healthy" if test_s3_connection(S3_BUCKET_NAME) else "unhealthy"
        
        # 임시 디렉토리 확인
        import os
        from config.settings import TMP_DIR
        tmp_dir_status = "healthy" if os.path.exists(TMP_DIR) and os.access(TMP_DIR, os.W_OK) else "unhealthy"
        
        # 전체 상태 결정
        overall_status = "healthy" if s3_status == "healthy" and tmp_dir_status == "healthy" else "degraded"
        
        return {
            "status": overall_status,
            "service": "contract-analyzer",
            "timestamp": time.time(),
            "components": {
                "ocr": "operational",
                "analyzer": "operational", 
                "s3": s3_status,
                "tmp_dir": tmp_dir_status,
                "api": "operational"
            },
            "details": {
                "s3_bucket": S3_BUCKET_NAME,
                "tmp_dir": TMP_DIR
            }
        }
        
    except Exception as e:
        logger.error(f"❌ 헬스체크 중 오류: {e}")
        return {
            "status": "unhealthy",
            "service": "contract-analyzer",
            "timestamp": time.time(),
            "error": str(e)
        }

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    logger.info("🚀 Contract Analyzer API 서버가 시작되었습니다.")
    
    # S3 연결 테스트
    logger.info("🔍 S3 연결 상태 확인 중...")
    if test_s3_connection(S3_BUCKET_NAME):
        logger.info("✅ S3 연결 상태: 정상")
    else:
        logger.warning("⚠️ S3 연결 상태: 문제 있음 - 업로드 기능이 제한될 수 있습니다.")
    
    # 임시 디렉토리 확인
    from config.settings import TMP_DIR
    import os
    os.makedirs(TMP_DIR, exist_ok=True)
    if os.access(TMP_DIR, os.W_OK):
        logger.info(f"✅ 임시 디렉토리 상태: 정상 ({TMP_DIR})")
    else:
        logger.warning(f"⚠️ 임시 디렉토리 쓰기 권한 없음: {TMP_DIR}")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    logger.info("🔚 Contract Analyzer API 서버가 종료됩니다.")
    # OCR 세션 정리
    try:
        from ocr.upstage_ocr_ultra_fast import cleanup_ocr_session
        cleanup_ocr_session()
        logger.info("✅ OCR 세션 정리 완료")
    except Exception as e:
        logger.warning(f"⚠️ OCR 세션 정리 중 오류: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
