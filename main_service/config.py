"""
Main Service 환경 설정 모듈
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
    
    # HTTP 클라이언트 설정
    REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = float(os.getenv("RETRY_DELAY", "2.0"))
    MAX_KEEPALIVE_CONNECTIONS = int(os.getenv("MAX_KEEPALIVE_CONNECTIONS", "10"))
    MAX_CONNECTIONS = int(os.getenv("MAX_CONNECTIONS", "20"))
    
    # 데이터베이스 설정
    MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "lawro_db")
    MYSQL_USER = os.getenv("MYSQL_USER", "lawro_user")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "lawro_password")
    
    @classmethod
    def get_database_url(cls) -> str:
        """데이터베이스 URL 생성"""
        return f"mysql+pymysql://{cls.MYSQL_USER}:{cls.MYSQL_PASSWORD}@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DATABASE}"
    
    # JWT 설정
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "lawro-secret-key")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))
    
    # OAuth 설정
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
    
    KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
    KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
    KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")
    
    NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
    NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
    NAVER_REDIRECT_URI = os.getenv("NAVER_REDIRECT_URI")
    
    # CORS 설정
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    CORS_METHODS = os.getenv("CORS_METHODS", "GET,POST,PUT,DELETE").split(",")
    
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
            "database_url": cls.get_database_url(),
            "http": {
                "timeout": cls.REQUEST_TIMEOUT,
                "max_retries": cls.MAX_RETRIES,
                "retry_delay": cls.RETRY_DELAY
            }
        }