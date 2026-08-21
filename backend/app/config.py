"""
Unified Configuration Management
Loads all environment variables and provides centralized configuration
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "LawRo Unified Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, production
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: str = "*"  # Comma-separated list

    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH: str = "firebase-credentials.json"
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_API_KEY: Optional[str] = None

    # JWT Configuration (for custom tokens if needed)
    JWT_SECRET_KEY: str = "your-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24

    # OAuth Configuration
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    KAKAO_CLIENT_ID: Optional[str] = None
    KAKAO_CLIENT_SECRET: Optional[str] = None
    NAVER_CLIENT_ID: Optional[str] = None
    NAVER_CLIENT_SECRET: Optional[str] = None
    FRONTEND_URL: str = "http://localhost:3000"

    # AI API Keys
    UPSTAGE_API_KEY: Optional[str] = None  # Solar Pro 2 for chatbot & contract analysis

    # ChromaDB Configuration
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"
    CHROMA_COLLECTION_NAME: str = "lawro_legal_docs"

    # Chatbot Configuration
    CHAT_MAX_SESSIONS: int = 1000
    CHAT_MAX_MESSAGES: int = 50
    CHAT_SESSION_TIMEOUT: int = 300  # 5 minutes
    CHAT_RETRIEVAL_K: int = 2
    CHAT_RETRIEVAL_SCORE_THRESHOLD: float = 0.3  # Similarity threshold
    CHAT_LLM_MODEL: str = "solar-pro2"  # solar-mini, solar-pro, solar-pro2, solar-max
    CHAT_EMBEDDING_MODEL: str = "solar-embedding-1-large-query"
    CHAT_MAX_RETRIES: int = 3  # API retry count
    CHAT_RETRY_DELAY: float = 1.0  # Retry delay in seconds

    # Local Storage Configuration
    LOCAL_STORAGE_PATH: str = "./storage/contracts"

    # AWS S3 Configuration (Optional - 로컬 스토리지 사용 시 불필요)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "ap-northeast-2"
    S3_BUCKET_NAME: Optional[str] = None

    # Contract Analysis Configuration
    CONTRACT_MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    CONTRACT_ALLOWED_EXTENSIONS: str = ".jpg,.jpeg,.png,.pdf"

    # HTTP Configuration
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 2.0

    # Session Management
    SESSION_BACKEND: str = "firestore"  # "firestore" or "memory"
    SESSION_CACHE_TTL: int = 300  # 5 minutes for in-memory cache

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()
