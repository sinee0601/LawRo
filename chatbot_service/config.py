"""
Chatbot Service 환경 설정 모듈
통일된 환경 변수 기반 설정 관리
"""
import os
from typing import Dict, Any

class Config:
    """통합 설정 클래스"""
    
    # 환경 설정
    ENVIRONMENT = os.getenv("ENVIRONMENT", "docker")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # 서비스 URL
    MAIN_SERVICE_URL = os.getenv("MAIN_SERVICE_URL", "http://main-api:8000")
    CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", "http://chatbot:8001")
    CONTRACT_SERVICE_URL = os.getenv("CONTRACT_SERVICE_URL", "http://contract-parser:8002")
    
    # 서비스 포트
    CHATBOT_SERVICE_PORT = int(os.getenv("CHATBOT_SERVICE_PORT", "8001"))
    
    # HTTP 클라이언트 설정
    REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = float(os.getenv("RETRY_DELAY", "2.0"))
    
    # AI 설정
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    UPSTAGE_MODEL = os.getenv("UPSTAGE_MODEL", "solar-1-mini-chat")
    
    # 벡터 DB 설정
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "/app/chroma_db")
    
    # 애플리케이션 설정
    PYTHONUNBUFFERED = os.getenv("PYTHONUNBUFFERED", "1")
    
    @classmethod
    def get_service_urls(cls) -> Dict[str, str]:
        """모든 서비스 URL 반환"""
        return {
            "main": cls.MAIN_SERVICE_URL,
            "chatbot": cls.CHATBOT_SERVICE_URL,
            "contract": cls.CONTRACT_SERVICE_URL
        }
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """설정을 딕셔너리로 반환"""
        return {
            "environment": cls.ENVIRONMENT,
            "debug": cls.DEBUG,
            "service_urls": cls.get_service_urls(),
            "port": cls.CHATBOT_SERVICE_PORT,
            "ai": {
                "openai_model": cls.OPENAI_MODEL,
                "upstage_model": cls.UPSTAGE_MODEL,
                "chroma_db_path": cls.CHROMA_DB_PATH
            },
            "http": {
                "timeout": cls.REQUEST_TIMEOUT,
                "max_retries": cls.MAX_RETRIES,
                "retry_delay": cls.RETRY_DELAY
            }
        }