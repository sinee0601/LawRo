"""
ChatBot 서버 연결 설정
"""
import os
from typing import Dict, Any

class ChatBotConfig:
    """ChatBot 서버 연결 설정"""
    
    def __init__(self):
        # 통일된 환경변수 사용
        self.base_url = os.getenv("CHATBOT_SERVICE_URL", "http://chatbot:8001")
        self.timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("RETRY_DELAY", "2.0"))
        self.environment = os.getenv("ENVIRONMENT", "docker")
        
    def get_base_url(self) -> str:
        """ChatBot 서버 기본 URL"""
        return self.base_url.rstrip('/')
    
    @property 
    def endpoints(self) -> Dict[str, str]:
        """ChatBot API 엔드포인트"""
        base = self.get_base_url()
        return {
            "health": f"{base}/health",
            "create_session": f"{base}/chat/new-session", 
            "chat": f"{base}/chat/send",
            "history": f"{base}/chat/history",
            "stats": f"{base}/stats"
        }
    
    def get_connection_config(self) -> Dict[str, Any]:
        """연결 설정 반환"""
        return {
            "base_url": self.get_base_url(),
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "environment": self.environment
        }
    
    def validate_config(self) -> bool:
        """설정 유효성 검사"""
        try:
            import requests
            response = requests.get(self.endpoints["health"], timeout=10)
            return response.status_code == 200
        except:
            return False

# 전역 설정 인스턴스
chatbot_config = ChatBotConfig()

# 편의 함수들
def get_chatbot_url() -> str:
    """ChatBot 서버 URL 반환"""
    return chatbot_config.get_base_url()

def get_chatbot_endpoints() -> Dict[str, str]:
    """ChatBot API 엔드포인트 반환"""
    return chatbot_config.endpoints

def is_chatbot_available() -> bool:
    """ChatBot 서버 연결 가능 여부 확인"""
    return chatbot_config.validate_config()

if __name__ == "__main__":
    # 설정 테스트
    print("ChatBot 설정 정보:")
    print(f"  환경: {chatbot_config.environment}")
    print(f"  서버 URL: {chatbot_config.get_base_url()}")
    print(f"  타임아웃: {chatbot_config.timeout}초")
    print(f"  최대 재시도: {chatbot_config.max_retries}회")
    
    print("\nAPI 엔드포인트:")
    for name, url in chatbot_config.endpoints.items():
        print(f"  {name}: {url}")
    
    print(f"\n연결 테스트: {'✅ 성공' if is_chatbot_available() else '❌ 실패'}") 