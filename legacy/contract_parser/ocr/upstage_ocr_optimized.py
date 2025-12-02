import requests
import time
from config.settings import UPSTAGE_OCR_API_KEY, UPSTAGE_OCR_ENDPOINT

def extract_text_from_image_optimized(image_path: str) -> dict:
    """
    🚀 최적화된 Upstage OCR 처리
    - 불필요한 파라미터 제거
    - 최적화된 설정 적용
    - 성능 측정 추가
    """
    start_time = time.time()
    
    headers = {"Authorization": f"Bearer {UPSTAGE_OCR_API_KEY}"}
    
    with open(image_path, "rb") as img_file:
        files = {"document": img_file}
        
        # 🎯 최적화된 파라미터 설정
        data = {
            "ocr": "force",                    # 이미지이므로 force 필요
            "model": "document-parse",         # 최신 모델 사용
            "output_formats": '["html"]',      # HTML만 요청 (불필요한 형식 제거)
            "coordinates": False,              # 좌표 정보 비활성화 (속도 향상)
            "chart_recognition": False,        # 차트 인식 비활성화 (계약서에 불필요)
            # base64_encoding 제거 (불필요한 인코딩 제거)
        }
        
        print(f"🚀 Upstage OCR API 호출 시작...")
        api_start = time.time()
        
        response = requests.post(
            UPSTAGE_OCR_ENDPOINT,
            headers=headers,
            files=files,
            data=data,
            timeout=120  # 타임아웃 설정
        )
        
        api_time = time.time() - api_start
        total_time = time.time() - start_time
        
        print(f"📊 API 응답 시간: {api_time:.2f}초")
        print(f"📊 전체 처리 시간: {total_time:.2f}초")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ OCR 처리 성공 - 상태코드: {response.status_code}")
        return result
    else:
        error_msg = f"OCR 요청 실패: {response.status_code}, {response.text}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)

def extract_text_from_image_ultra_fast(image_path: str) -> dict:
    """
    ⚡ 초고속 OCR 처리 (최소 파라미터)
    - 텍스트 추출만 집중
    - 모든 부가 기능 비활성화
    """
    start_time = time.time()
    
    headers = {"Authorization": f"Bearer {UPSTAGE_OCR_API_KEY}"}
    
    with open(image_path, "rb") as img_file:
        files = {"document": img_file}
        
        # ⚡ 최소 파라미터로 최대 속도
        data = {
            "ocr": "force",
            "model": "document-parse",
            "output_formats": '["text"]',      # 텍스트만 요청
            # 모든 부가 기능 비활성화
        }
        
        print(f"⚡ 초고속 OCR 모드 시작...")
        
        response = requests.post(
            UPSTAGE_OCR_ENDPOINT,
            headers=headers,
            files=files,
            data=data,
            timeout=60
        )
        
        total_time = time.time() - start_time
        print(f"⚡ 초고속 처리 완료: {total_time:.2f}초")

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"초고속 OCR 실패: {response.status_code}, {response.text}")

# 기존 함수와의 호환성을 위한 래퍼
def extract_text_from_image(image_path: str) -> dict:
    """기존 함수명 유지하면서 최적화된 버전 사용"""
    return extract_text_from_image_optimized(image_path) 