"""
Contract Parser Service 환경 설정 모듈
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
    CONTRACT_SERVICE_PORT = int(os.getenv("CONTRACT_SERVICE_PORT", "8002"))
    
    # HTTP 클라이언트 설정
    REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = float(os.getenv("RETRY_DELAY", "2.0"))
    
    # AI 설정
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # AWS 설정
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    
    # 파일 처리 설정
    TMP_DIR = os.getenv("TMP_DIR", "/tmp/lawro")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "jpg,jpeg,png,pdf").split(",")
    
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
            "port": cls.CONTRACT_SERVICE_PORT,
            "ai": {
                "openai_model": cls.OPENAI_MODEL
            },
            "aws": {
                "region": cls.AWS_REGION,
                "s3_bucket": cls.S3_BUCKET_NAME
            },
            "file_processing": {
                "tmp_dir": cls.TMP_DIR,
                "max_file_size": cls.MAX_FILE_SIZE,
                "allowed_types": cls.ALLOWED_FILE_TYPES
            },
            "http": {
                "timeout": cls.REQUEST_TIMEOUT,
                "max_retries": cls.MAX_RETRIES,
                "retry_delay": cls.RETRY_DELAY
            }
        }