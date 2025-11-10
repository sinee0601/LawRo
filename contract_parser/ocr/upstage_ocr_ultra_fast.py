import requests
import time
import json
from typing import Optional, Dict, Any
from config.settings import UPSTAGE_OCR_API_KEY, UPSTAGE_OCR_ENDPOINT
import logging

logger = logging.getLogger(__name__)

class UltraFastUpstageOCR:
    """
    ⚡ Ultra Fast Upstage OCR 클래스
    최고 성능을 위한 최적화된 구현
    """
    
    def __init__(self):
        """초기화 및 세션 설정"""
        if not UPSTAGE_OCR_API_KEY:
            raise ValueError("UPSTAGE_OCR_API_KEY가 설정되지 않았습니다.")
            
        self.api_key = UPSTAGE_OCR_API_KEY
        self.endpoint = UPSTAGE_OCR_ENDPOINT
        
        # 재사용 가능한 세션 생성
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": "LawRo-ContractAnalyzer/1.0"
        })
        
        # 연결 풀 최적화
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=3,
            pool_maxsize=10,
            max_retries=requests.adapters.Retry(
                total=3,
                backoff_factor=0.3,
                status_forcelist=[500, 502, 503, 504]
            ),
            pool_block=False
        )
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        
        logger.info("⚡ Ultra Fast OCR 세션 초기화 완료")
    
    def extract_text_minimal(self, image_path: str) -> dict:
        """
        ⚡ 최소 파라미터로 최고 속도 OCR
        텍스트 추출에만 집중
        """
        start_time = time.time()
        
        try:
            # 파일 존재 확인
            import os
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")
            
            # 파일 크기 확인 (100MB 제한)
            file_size = os.path.getsize(image_path)
            if file_size > 100 * 1024 * 1024:  # 100MB
                raise ValueError(f"파일 크기가 너무 큽니다: {file_size / 1024 / 1024:.1f}MB (최대 100MB)")
            
            with open(image_path, "rb") as img_file:
                files = {"document": img_file}
                
                # 🎯 최소한의 파라미터만 사용
                data = {
                    "ocr": "force",
                    "model": "document-parse",
                    "output_formats": '["text"]'  # 텍스트만 요청
                }
                
                logger.info(f"⚡ Ultra Fast OCR 시작: {image_path} ({file_size / 1024:.1f}KB)")
                api_start = time.time()
                
                response = self.session.post(
                    self.endpoint,
                    files=files,
                    data=data,
                    timeout=(30, 120)  # (연결 타임아웃, 읽기 타임아웃)
                )
                
                api_time = time.time() - api_start
                total_time = time.time() - start_time
                
                logger.info(f"⚡ Ultra Fast OCR 완료: {api_time:.2f}초 (전체: {total_time:.2f}초)")
                
                if response.status_code == 200:
                    return response.json()
                else:
                    error_msg = f"OCR API 오류: {response.status_code}"
                    try:
                        error_detail = response.json()
                        error_msg += f", {error_detail}"
                    except:
                        error_msg += f", {response.text[:200]}"
                    
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except requests.exceptions.Timeout:
            logger.error("⏰ OCR 요청 타임아웃")
            raise Exception("OCR 요청이 시간 초과되었습니다.")
        except requests.exceptions.ConnectionError:
            logger.error("🔌 OCR 서버 연결 실패")
            raise Exception("OCR 서버에 연결할 수 없습니다.")
        except requests.exceptions.RequestException as e:
            logger.error(f"🌐 네트워크 오류: {str(e)}")
            raise Exception(f"네트워크 오류: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Ultra Fast OCR 실패: {str(e)}")
            raise
    
    def extract_text_optimized(self, image_path: str) -> dict:
        """
        🚀 최적화된 HTML OCR
        속도와 품질의 균형
        """
        start_time = time.time()
        
        try:
            # 파일 검증
            import os
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")
                
            file_size = os.path.getsize(image_path)
            if file_size > 100 * 1024 * 1024:  # 100MB
                raise ValueError(f"파일 크기가 너무 큽니다: {file_size / 1024 / 1024:.1f}MB")
            
            with open(image_path, "rb") as img_file:
                files = {"document": img_file}
                
                # 🎯 최적화된 파라미터
                data = {
                    "ocr": "force",
                    "model": "document-parse",
                    "output_formats": '["html"]',
                    "coordinates": False,      # 좌표 정보 비활성화
                    "chart_recognition": False  # 차트 인식 비활성화
                }
                
                logger.info(f"🚀 최적화된 OCR 시작: {image_path} ({file_size / 1024:.1f}KB)")
                api_start = time.time()
                
                response = self.session.post(
                    self.endpoint,
                    files=files,
                    data=data,
                    timeout=(30, 150)  # HTML은 텍스트보다 조금 더 오래 걸림
                )
                
                api_time = time.time() - api_start
                total_time = time.time() - start_time
                
                logger.info(f"🚀 최적화된 OCR 완료: {api_time:.2f}초 (전체: {total_time:.2f}초)")
                
                if response.status_code == 200:
                    return response.json()
                else:
                    error_msg = f"OCR API 오류: {response.status_code}"
                    try:
                        error_detail = response.json()
                        error_msg += f", {error_detail}"
                    except:
                        error_msg += f", {response.text[:200]}"
                    
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except requests.exceptions.Timeout:
            logger.error("⏰ OCR 요청 타임아웃")
            raise Exception("OCR 요청이 시간 초과되었습니다.")
        except requests.exceptions.ConnectionError:
            logger.error("🔌 OCR 서버 연결 실패")
            raise Exception("OCR 서버에 연결할 수 없습니다.")
        except requests.exceptions.RequestException as e:
            logger.error(f"🌐 네트워크 오류: {str(e)}")
            raise Exception(f"네트워크 오류: {str(e)}")
        except Exception as e:
            logger.error(f"❌ 최적화된 OCR 실패: {str(e)}")
            raise
    
    def extract_with_retry(self, image_path: str, max_retries: int = 2) -> dict:
        """
        🔄 재시도 로직이 포함된 OCR
        네트워크 불안정 상황 대응
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    wait_time = min(2 ** attempt, 10)  # 지수 백오프 (최대 10초)
                    logger.info(f"🔄 OCR 재시도 {attempt}/{max_retries} (대기: {wait_time}초)")
                    time.sleep(wait_time)
                
                return self.extract_text_optimized(image_path)
                
            except Exception as e:
                last_exception = e
                if attempt == max_retries:
                    logger.error(f"❌ 최종 OCR 실패 (재시도 {max_retries}회): {str(e)}")
                    raise e
                else:
                    logger.warning(f"⚠️ OCR 실패, 재시도 예정: {str(e)}")
                    continue
    
    def close_session(self):
        """세션 정리"""
        if hasattr(self, 'session') and self.session:
            self.session.close()
            logger.info("⚡ Ultra Fast OCR 세션 종료")
    
    def __del__(self):
        """소멸자에서 세션 정리"""
        try:
            self.close_session()
        except:
            pass

# 전역 인스턴스 (재사용을 위해)
_ocr_instance: Optional[UltraFastUpstageOCR] = None

def get_ocr_instance() -> UltraFastUpstageOCR:
    """OCR 인스턴스 싱글톤 패턴"""
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = UltraFastUpstageOCR()
    return _ocr_instance

def extract_text_ultra_fast(image_path: str) -> dict:
    """
    ⚡ Ultra Fast OCR - 외부 인터페이스
    기존 코드와 호환되는 함수형 인터페이스
    """
    ocr = get_ocr_instance()
    return ocr.extract_text_minimal(image_path)

def extract_text_optimized_global(image_path: str) -> dict:
    """
    🚀 최적화된 OCR - 외부 인터페이스
    기존 코드와 호환되는 함수형 인터페이스
    """
    ocr = get_ocr_instance()
    return ocr.extract_text_optimized(image_path)

def extract_text_with_retry_global(image_path: str) -> dict:
    """
    🔄 재시도 OCR - 외부 인터페이스
    기존 코드와 호환되는 함수형 인터페이스
    """
    ocr = get_ocr_instance()
    return ocr.extract_with_retry(image_path)

# 세션 정리를 위한 함수
def cleanup_ocr_session():
    """OCR 세션 정리"""
    global _ocr_instance
    if _ocr_instance:
        _ocr_instance.close_session()
        _ocr_instance = None
        logger.info("🧹 OCR 세션 정리 완료") 