import os
from dotenv import load_dotenv

load_dotenv()

# 환경 변수 검증 함수
def get_required_env(key: str) -> str:
    """필수 환경 변수를 가져오고 없으면 에러 발생"""
    value = os.getenv(key)
    if not value:
        raise ValueError(f"필수 환경 변수 {key}가 설정되지 않았습니다.")
    return value

def get_optional_env(key: str, default: str = None) -> str:
    """선택적 환경 변수를 가져오고 없으면 기본값 반환"""
    return os.getenv(key, default)

# API 설정
UPSTAGE_OCR_API_KEY = get_required_env("UPSTAGE_OCR_API_KEY")
UPSTAGE_OCR_ENDPOINT = get_optional_env("UPSTAGE_OCR_ENDPOINT", "https://api.upstage.ai/v1/document-digitization")

# AWS 설정
AWS_ACCESS_KEY_ID = get_required_env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = get_required_env("AWS_SECRET_ACCESS_KEY")
AWS_REGION = get_optional_env("AWS_DEFAULT_REGION", "ap-northeast-2")
S3_BUCKET_NAME = get_required_env("S3_BUCKET_NAME")

# OpenAI 설정
OPENAI_API_KEY = get_required_env("OPENAI_API_KEY")

# 디렉토리 설정
TMP_DIR = get_optional_env("TMP_DIR", "/tmp/lawro_contract_analyzer")

# 디렉토리 생성
os.makedirs(TMP_DIR, exist_ok=True)

# 설정 검증 로그
print(f"✅ 설정 로드 완료:")
print(f"   - Upstage OCR: {UPSTAGE_OCR_ENDPOINT}")
print(f"   - AWS Region: {AWS_REGION}")  
print(f"   - S3 Bucket: {S3_BUCKET_NAME}")
print(f"   - TMP Dir: {TMP_DIR}")
print(f"   - API Keys: {'✅' if UPSTAGE_OCR_API_KEY and OPENAI_API_KEY else '❌'}")