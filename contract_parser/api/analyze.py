import os
import time
import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from config.settings import S3_BUCKET_NAME, TMP_DIR
from ocr.batch_ocr_processor import process_contract_images_from_s3
from llm.gpt_parser import extract_contract_items_from_summary
import boto3
import traceback
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)
router = APIRouter()

# S3 클라이언트 초기화
try:
    s3 = boto3.client("s3")
    logger.info("✅ S3 클라이언트 초기화 완료")
except Exception as e:
    logger.error(f"❌ S3 클라이언트 초기화 실패: {e}")
    s3 = None

# 업로드 API의 임시 저장소 참조
from .upload import get_temp_data

class AnalyzeRequest(BaseModel):
    user_id: str = Field(..., description="사용자 ID")
    contract_id: str = Field(..., description="계약서 ID")

class AnalyzeResponse(BaseModel):
    message: str = Field(default="계약서 분석 완료")
    structured_result: Dict[str, Any] = Field(..., description="구조화된 분석 결과")
    processing_info: Optional[Dict[str, Any]] = Field(None, description="처리 정보")

class AnalyzeWithChatbotRequest(BaseModel):
    user_id: str = Field(..., description="사용자 ID")
    contract_id: str = Field(..., description="계약서 ID")
    use_chatbot: bool = Field(default=True, description="챗봇 분석 사용 여부")
    user_language: Optional[str] = Field(None, description="사용자 언어 (없으면 임시 저장소에서 가져옴)")
    use_saved_data: bool = Field(default=True, description="저장된 분석 데이터 사용 여부")

class AnalyzeWithChatbotResponse(BaseModel):
    message: str = Field(default="계약서 분석 및 법률 상담 완료")
    page_summaries: Optional[List[str]] = Field(None, description="페이지별 요약")
    structured_result: Dict[str, Any] = Field(..., description="구조화된 분석 결과")
    chatbot_analysis: Optional[Dict[str, Any]] = Field(None, description="챗봇 법률 분석 결과")
    session_id: Optional[str] = Field(None, description="챗봇 세션 ID")
    processing_info: Optional[Dict[str, Any]] = Field(None, description="처리 정보")
    data_source: str = Field(..., description="데이터 소스 (saved_db, fresh_ocr)")

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_contract_images(req: AnalyzeRequest, request: Request):
    """
    **기본 워크플로우: 계약서 OCR + 구조화 분석만**
    
    🎯 사용 케이스: 
    - ChatBot 분석이 필요 없는 경우
    - 빠른 구조화 데이터만 필요한 경우
    - 개발/테스트 목적
    
    ⚠️ 권장: 대부분의 경우 `/analyze-with-chatbot` 사용 권장
    """
    start_time = time.time()
    
    if not s3:
        raise HTTPException(status_code=500, detail="S3 서비스를 사용할 수 없습니다.")
    
    logger.info(f"🚀 계약서 분석 시작 - 사용자: {req.user_id}, 계약서: {req.contract_id}")
    
    try:
        # S3 객체 목록 조회
        prefix = f"user_{req.user_id}/contracts/{req.contract_id}/"
        logger.info(f"📂 S3 객체 검색 중: {prefix}")
        
        paginator = s3.get_paginator("list_objects_v2")
        s3_keys = []
        
        try:
            for page in paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=prefix):
                contents = page.get("Contents", [])
                for obj in contents:
                    # 이미지 파일만 필터링
                    key = obj["Key"]
                    if key.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp')):
                        s3_keys.append(key)
                        
        except Exception as e:
            logger.error(f"❌ S3 객체 조회 실패: {e}")
            raise HTTPException(status_code=500, detail=f"S3 객체 조회 실패: {str(e)}")

        if not s3_keys:
            logger.warning(f"⚠️ 계약서 이미지 없음: {prefix}")
            raise HTTPException(status_code=404, detail="해당 계약서 이미지가 없습니다.")

        logger.info(f"📄 발견된 이미지 파일: {len(s3_keys)}개")

        # 임시 출력 파일 경로 생성
        os.makedirs(TMP_DIR, exist_ok=True)
        tmp_output = os.path.join(TMP_DIR, f"ocr_result_{req.user_id}_{req.contract_id}_{int(time.time())}.json")

        # OCR 배치 처리
        logger.info("🔍 OCR 배치 처리 시작")
        ocr_start = time.time()
        
        try:
            process_contract_images_from_s3(
                bucket=S3_BUCKET_NAME,
                s3_keys=s3_keys,
                output_path=tmp_output
            )
            ocr_time = time.time() - ocr_start
            logger.info(f"✅ OCR 처리 완료: {ocr_time:.2f}초")
            
        except Exception as e:
            logger.error(f"❌ OCR 처리 실패: {e}")
            raise HTTPException(status_code=500, detail=f"OCR 처리 실패: {str(e)}")

        # 계약서 항목 추출
        logger.info("📝 계약서 항목 추출 시작")
        parse_start = time.time()
        
        try:
            structured_result = extract_contract_items_from_summary(tmp_output)
            parse_time = time.time() - parse_start
            logger.info(f"✅ 계약서 파싱 완료: {parse_time:.2f}초")
            
        except Exception as e:
            logger.error(f"❌ 계약서 파싱 실패: {e}")
            raise HTTPException(status_code=500, detail=f"계약서 분석 실패: {str(e)}")
        
        finally:
            # 임시 파일 정리
            try:
                if os.path.exists(tmp_output):
                    os.remove(tmp_output)
                    logger.info("🧹 임시 파일 정리 완료")
            except Exception as cleanup_error:
                logger.warning(f"⚠️ 임시 파일 정리 실패: {cleanup_error}")

        total_time = time.time() - start_time
        processing_info = {
            "total_time": round(total_time, 2),
            "ocr_time": round(ocr_time, 2),
            "parse_time": round(parse_time, 2),
            "image_count": len(s3_keys),
            "timestamp": time.time()
        }
        
        logger.info(f"🎉 계약서 분석 완료: {total_time:.2f}초 (OCR: {ocr_time:.2f}초, 파싱: {parse_time:.2f}초)")

        return AnalyzeResponse(
            structured_result=structured_result,
            processing_info=processing_info
        )

    except HTTPException:
        # HTTPException은 그대로 다시 raise
        raise
    except Exception as e:
        # 예상치 못한 오류 처리
        tb = traceback.format_exc()
        logger.error(f"❌ 예상치 못한 오류:\n{tb}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/analyze/health")
def analyze_health_check():
    """분석 서비스 상태 확인"""
    try:
        # S3 연결 테스트
        s3_status = "healthy"
        if s3:
            try:
                s3.head_bucket(Bucket=S3_BUCKET_NAME)
                s3_status = "healthy"
            except Exception as e:
                s3_status = f"error: {str(e)}"
        else:
            s3_status = "not_initialized"
        
        # 임시 디렉토리 확인
        tmp_dir_status = "healthy" if os.path.exists(TMP_DIR) and os.access(TMP_DIR, os.W_OK) else "error"
        
        return {
            "status": "healthy",
            "service": "contract-analyzer",
            "timestamp": time.time(),
            "components": {
                "s3": s3_status,
                "tmp_dir": tmp_dir_status,
                "ocr": "operational",
                "parser": "operational"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ 헬스체크 실패: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

async def get_saved_contract_data(user_id: str, contract_id: str, auth_token: str = None) -> Optional[Dict[str, Any]]:
    """메인 API에서 저장된 계약서 분석 데이터 조회"""
    try:
        # 메인 API 서버 URL (환경 변수 또는 기본값)
        main_api_url = os.getenv("MAIN_API_URL", "http://16.176.26.197:8000")
        
        # 인증 헤더 설정
        headers = {
            "Content-Type": "application/json"
        }
        
        # 인증 토큰이 있으면 추가
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
            logger.info(f"🔐 인증 토큰으로 저장된 데이터 조회 시도: {contract_id}")
        else:
            logger.warning(f"⚠️ 인증 토큰 없이 저장된 데이터 조회 시도: {contract_id}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{main_api_url}/contract/analysis/{contract_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"🔍 Main API 응답 데이터: {data}")
                if data.get("success"):
                    analysis_result = data["analysis_result"]
                    logger.info(f"✅ DB에서 저장된 분석 데이터 조회 성공: {contract_id}")
                    logger.info(f"🔍 분석 결과 타입: {type(analysis_result)}")
                    logger.info(f"🔍 분석 결과 키들: {list(analysis_result.keys()) if isinstance(analysis_result, dict) else 'Not a dict'}")
                    return analysis_result
                else:
                    logger.warning(f"⚠️ 저장된 분석 데이터 조회 실패: {data}")
                    return None
            elif response.status_code == 404:
                logger.info(f"📋 저장된 분석 데이터 없음: {contract_id}")
                return None
            elif response.status_code == 401:
                logger.warning(f"🔐 인증 실패로 저장된 데이터 조회 불가: {contract_id}")
                return None
            else:
                logger.error(f"❌ 저장된 분석 데이터 조회 오류: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"❌ 저장된 분석 데이터 조회 중 예외 발생: {str(e)}")
        return None

@router.post("/analyze-with-chatbot", response_model=AnalyzeWithChatbotResponse)
async def analyze_contract_with_chatbot(req: AnalyzeWithChatbotRequest, request: Request):
    """
    **메인 워크플로우: 계약서 완전 통합 분석**
    
    🎯 권장 사용법: 업로드 후 이 엔드포인트 하나로 모든 분석 완료
    
    처리 단계:
    1. 저장된 분석 데이터 확인 (use_saved_data=True 시)
    2. 없으면 자동으로 OCR + 구조화 분석 실행
    3. ChatBot 법률 전문가 분석 추가 (use_chatbot=True 시)  
    4. 통합 결과 반환
    
    장점:
    - 원스톱 분석: 클라이언트는 한 번만 호출
    - 지능형 캐싱: 기존 데이터 재활용
    - AI 법률 분석: 전문적인 계약서 검토
    """
    start_time = time.time()
    
    logger.info(f"🚀 계약서 챗봇 통합 분석 시작 - 사용자: {req.user_id}, 계약서: {req.contract_id}, 저장된 데이터 사용: {req.use_saved_data}")
    
    try:
        # 1. 언어 정보 가져오기
        user_language = req.user_language
        if not user_language:
            temp_data = get_temp_data(req.contract_id)
            if temp_data:
                user_language = temp_data.get('language', 'korean')
                logger.info(f"📋 임시 저장소에서 언어 정보 가져옴: {user_language}")
            else:
                user_language = 'korean'  # 기본값
                logger.warning(f"⚠️ 임시 저장소에 언어 정보 없음. 기본값 사용: {user_language}")
        
        structured_result = None
        data_source = "fresh_ocr"
        ocr_time = 0
        parse_time = 0
        
        # 2. 저장된 분석 데이터 조회 시도 (use_saved_data=True인 경우)
        if req.use_saved_data:
            logger.info("🔍 저장된 분석 데이터 조회 시도 중...")
            try:
                # Authorization 헤더에서 토큰 추출
                auth_header = request.headers.get("authorization")
                auth_token = None
                if auth_header and auth_header.startswith("Bearer "):
                    auth_token = auth_header.replace("Bearer ", "")
                
                saved_data = await get_saved_contract_data(req.user_id, req.contract_id, auth_token)
                if saved_data:
                    structured_result = saved_data
                    data_source = "saved_db"
                    logger.info(f"✅ 저장된 분석 데이터 사용: {req.contract_id}")
                else:
                    logger.info(f"📋 저장된 분석 데이터 없음. 새로 분석 진행: {req.contract_id}")
            except Exception as e:
                logger.warning(f"⚠️ 저장된 데이터 조회 중 오류: {str(e)}. 새로 분석 진행")
        
        # 3. 저장된 데이터가 없으면 기본 분석 수행
        if not structured_result:
            if not s3:
                raise HTTPException(status_code=500, detail="S3 서비스를 사용할 수 없습니다.")
            
            logger.info("🔄 새로운 OCR 및 분석 수행")
            
            # S3 객체 목록 조회
            prefix = f"user_{req.user_id}/contracts/{req.contract_id}/"
            logger.info(f"📂 S3 객체 검색 중: {prefix}")
            
            paginator = s3.get_paginator("list_objects_v2")
            s3_keys = []
            
            try:
                for page in paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=prefix):
                    contents = page.get("Contents", [])
                    for obj in contents:
                        key = obj["Key"]
                        if key.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp')):
                            s3_keys.append(key)
                            
            except Exception as e:
                logger.error(f"❌ S3 객체 조회 실패: {e}")
                raise HTTPException(status_code=500, detail=f"S3 객체 조회 실패: {str(e)}")

            if not s3_keys:
                logger.warning(f"⚠️ 계약서 이미지 없음: {prefix}")
                raise HTTPException(status_code=404, detail="해당 계약서 이미지가 없습니다.")

            logger.info(f"📄 발견된 이미지 파일: {len(s3_keys)}개")

            # OCR 처리
            os.makedirs(TMP_DIR, exist_ok=True)
            tmp_output = os.path.join(TMP_DIR, f"ocr_result_{req.user_id}_{req.contract_id}_{int(time.time())}.json")

        logger.info("🔍 OCR 배치 처리 시작")
        ocr_start = time.time()
        
        try:
            process_contract_images_from_s3(
                bucket=S3_BUCKET_NAME,
                s3_keys=s3_keys,
                output_path=tmp_output
            )
            ocr_time = time.time() - ocr_start
            logger.info(f"✅ OCR 처리 완료: {ocr_time:.2f}초")
            
        except Exception as e:
            logger.error(f"❌ OCR 처리 실패: {e}")
            raise HTTPException(status_code=500, detail=f"OCR 처리 실패: {str(e)}")

            # 계약서 항목 추출
        logger.info("📝 계약서 항목 추출 시작")
        parse_start = time.time()
        
        try:
            structured_result = extract_contract_items_from_summary(tmp_output)
            parse_time = time.time() - parse_start
            logger.info(f"✅ 계약서 파싱 완료: {parse_time:.2f}초")
            
        except Exception as e:
            logger.error(f"❌ 계약서 파싱 실패: {e}")
            raise HTTPException(status_code=500, detail=f"계약서 분석 실패: {str(e)}")
        
        finally:
            # 임시 파일 정리
            try:
                if os.path.exists(tmp_output):
                    os.remove(tmp_output)
                    logger.info("🧹 임시 파일 정리 완료")
            except Exception as cleanup_error:
                logger.warning(f"⚠️ 임시 파일 정리 실패: {cleanup_error}")

        # 4. 챗봇 법률 분석 (요청 시에만)
        chatbot_analysis = None
        session_id = None
        
        if req.use_chatbot:
            try:
                logger.info("🤖 ChatBot 법률 분석 시작...")
                
                # ChatBot 통합 서비스 사용
                from services.chatbot_integration_service import ChatbotIntegrationService
                chatbot_service = ChatbotIntegrationService()
                
                # 파싱된 계약서 데이터를 ChatBot으로 법률 분석 요청
                chatbot_result = chatbot_service.analyze_contract_with_chatbot(
                    parsed_contract_data=structured_result,
                    user_id=req.user_id,
                    user_language=user_language
                )
                
                if chatbot_result["success"]:
                    chatbot_analysis = {
                        "legal_analysis": chatbot_result["analysis"],
                        "processing_time": chatbot_result["processing_time"],
                        "timestamp": chatbot_result["timestamp"]
                    }
                    session_id = chatbot_result["session_id"]
                    
                    logger.info(f"✅ ChatBot 법률 분석 완료 (세션: {session_id[:8] if session_id else 'N/A'}...)")
                else:
                    logger.error(f"❌ ChatBot 법률 분석 실패: {chatbot_result.get('error', 'Unknown error')}")
                    chatbot_analysis = {
                        "error": chatbot_result.get('error', 'Unknown error'),
                        "legal_analysis": "ChatBot 법률 분석에 실패했습니다. 기본 분석 결과를 참고해 주세요."
                    }
                    
            except Exception as chatbot_error:
                error_msg = str(chatbot_error)
                logger.error(f"❌ ChatBot 통합 오류: {error_msg}")
                logger.error(f"❌ ChatBot 오류 상세: {traceback.format_exc()}")
                
                # 오류 유형에 따른 구체적 메시지
                if "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                    user_message = "ChatBot 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요."
                elif "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
                    user_message = "ChatBot 서비스 인증에 실패했습니다. 관리자에게 문의해 주세요."
                else:
                    user_message = "ChatBot 법률 분석 중 오류가 발생했습니다. 기본 분석 결과를 참고해 주세요."
                
                chatbot_analysis = {
                    "error": error_msg,
                    "error_type": type(chatbot_error).__name__,
                    "legal_analysis": user_message,
                    "fallback_mode": True
                }

        total_time = time.time() - start_time
        processing_info = {
            "total_time": round(total_time, 2),
            "ocr_time": round(ocr_time, 2),
            "parse_time": round(parse_time, 2),
            "image_count": len(s3_keys) if 's3_keys' in locals() else 0,
            "user_language": user_language,
            "data_source": data_source,
            "timestamp": time.time()
        }
        
        logger.info(f"🎉 계약서 챗봇 통합 분석 완료: {total_time:.2f}초 (데이터 소스: {data_source})")

        return AnalyzeWithChatbotResponse(
            structured_result=structured_result,
            chatbot_analysis=chatbot_analysis,
            session_id=session_id,
            processing_info=processing_info,
            data_source=data_source
        )

    except HTTPException:
        # HTTPException은 그대로 다시 raise
        raise
    except Exception as e:
        # 예상치 못한 오류 처리
        error_msg = str(e) or "알 수 없는 오류"
        tb = traceback.format_exc()
        logger.error(f"❌ 예상치 못한 오류: {error_msg}")
        logger.error(f"❌ 상세 스택 트레이스:\n{tb}")
        
        # 사용자 친화적 오류 메시지
        if "timeout" in error_msg.lower():
            detail = "요청 처리 시간이 초과되었습니다. 파일 크기를 줄이거나 잠시 후 다시 시도해 주세요."
        elif "memory" in error_msg.lower() or "out of memory" in error_msg.lower():
            detail = "메모리 부족으로 처리할 수 없습니다. 파일 수를 줄여서 다시 시도해 주세요."
        elif "permission" in error_msg.lower() or "access" in error_msg.lower():
            detail = "파일 접근 권한 오류가 발생했습니다. 관리자에게 문의해 주세요."
        else:
            detail = f"계약서 분석 중 오류가 발생했습니다: {error_msg}"
        
        raise HTTPException(
            status_code=500, 
            detail={
                "message": detail,
                "error_type": type(e).__name__,
                "contract_id": req.contract_id if 'req' in locals() else None
            }
        )

@router.get("/chatbot-status")
def check_chatbot_status():
    """ChatBot 서버 연결 상태 확인"""
    try:
        logger.info("🔍 ChatBot 서버 상태 확인 시작")
        from services.chatbot_integration_service import ChatbotIntegrationService
        chatbot_service = ChatbotIntegrationService()
        health_check = chatbot_service.health_check()
        
        status_result = {
            "chatbot_available": health_check["success"],
            "status": health_check.get("status", "unknown"),
            "response_time": health_check.get("response_time"),
            "timestamp": time.time(),
            "details": health_check
        }
        
        if health_check["success"]:
            logger.info("✅ ChatBot 서버 정상 연결")
        else:
            logger.warning(f"⚠️ ChatBot 서버 연결 불안정: {health_check.get('error', 'Unknown')}")
        
        return status_result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ ChatBot 상태 확인 실패: {error_msg}")
        logger.error(f"❌ 상세 오류: {traceback.format_exc()}")
        
        return {
            "chatbot_available": False,
            "status": "error",
            "error": error_msg,
            "error_type": type(e).__name__,
            "timestamp": time.time()
        }
