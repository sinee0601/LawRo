from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import List, Optional, Dict, Any
from utils.s3_utils import upload_image_to_s3
from config.settings import S3_BUCKET_NAME
import uuid
import json
import os
import logging
import traceback
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 임시 데이터 저장을 위한 간단한 메모리 저장소 (실제 운영에서는 Redis 사용 권장)
temp_storage = {}

def clean_expired_data():
    """만료된 임시 데이터 정리"""
    current_time = datetime.now()
    expired_keys = []
    for key, data in temp_storage.items():
        if data.get('expires_at') and current_time > datetime.fromisoformat(data['expires_at']):
            expired_keys.append(key)
    
    for key in expired_keys:
        del temp_storage[key]

def store_temp_data(contract_id: str, language: str):
    """임시 데이터 저장 (24시간 보관)"""
    try:
        clean_expired_data()
        expires_at = datetime.now() + timedelta(hours=24)
        temp_storage[contract_id] = {
            'language': language,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at.isoformat()
        }
        logger.info(f"✅ 임시 데이터 저장 완료: {contract_id} (언어: {language})")
    except Exception as e:
        logger.error(f"❌ 임시 데이터 저장 실패: {contract_id}, 오류: {str(e)}")

def get_temp_data(contract_id: str) -> Optional[dict]:
    """임시 데이터 조회"""
    try:
        clean_expired_data()
        return temp_storage.get(contract_id)
    except Exception as e:
        logger.error(f"❌ 임시 데이터 조회 실패: {contract_id}, 오류: {str(e)}")
        return None

def validate_files(files: List[UploadFile]) -> None:
    """파일 유효성 검사"""
    if not files:
        raise HTTPException(status_code=400, detail="업로드할 파일이 없습니다")
    
    # 지원하는 이미지 확장자
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}
    max_file_size = 10 * 1024 * 1024  # 10MB
    
    for file in files:
        if not file.filename:
            raise HTTPException(status_code=400, detail="파일명이 없는 파일이 있습니다")
        
        # 확장자 검사
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"지원하지 않는 파일 형식입니다: {file.filename}. 지원 형식: {', '.join(allowed_extensions)}"
            )
        
        # 파일 크기 검사 (approximate)
        if hasattr(file, 'size') and file.size and file.size > max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"파일 크기가 너무 큽니다: {file.filename}. 최대 10MB까지 지원합니다."
            )
        
        # MIME 타입 검사
        if file.content_type and not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail=f"이미지 파일만 업로드 가능합니다: {file.filename} (타입: {file.content_type})"
            )

class UploadSuccessResponse(BaseModel):
    """업로드 성공 응답 모델"""
    message: str = Field(default="이미지 업로드 완료")
    contract_id: str = Field(..., description="계약서 ID")
    s3_keys: List[str] = Field(..., description="업로드된 S3 객체 키 목록")
    language: str = Field(..., description="사용자 언어")
    file_count: int = Field(..., description="업로드된 파일 수")
    warnings: Optional[Dict[str, Any]] = Field(None, description="경고 메시지 (부분 실패 시)")

class TempDataResponse(BaseModel):
    """임시 데이터 응답 모델"""
    success: bool = Field(default=True)
    contract_id: str = Field(..., description="계약서 ID")
    data: Optional[Dict[str, Any]] = Field(None, description="임시 데이터")
    error: Optional[str] = Field(None, description="오류 메시지")

@router.post("/upload", response_model=UploadSuccessResponse)
async def upload_contract_images(
    user_id: str = Form(..., description="사용자 ID"),
    language: str = Form(default="korean", description="사용자 언어 (korean, english, etc.)"),
    contract_id: Optional[str] = Form(None, description="계약서 ID (선택사항, 없으면 자동 생성)"),
    files: List[UploadFile] = File(..., description="업로드할 이미지 파일들")
):
    """
    계약서 이미지 업로드 API
    - contract_id가 없으면 자동 생성
    - language 정보를 임시 저장하여 분석 시 사용  
    - 강화된 예외 처리 및 로깅
    """
    
    logger.info(f"🚀 업로드 요청 시작 - 사용자: {user_id}, 언어: {language}, 계약서: {contract_id}, 파일 수: {len(files)}")
    
    try:
        # 1. 파일 유효성 검사
        validate_files(files)
        logger.info("✅ 파일 유효성 검사 통과")
        
        # 2. contract_id가 없으면 자동 생성
        if not contract_id or contract_id.strip() == "":
            contract_id = f"contract_{uuid.uuid4().hex[:12]}"
            logger.info(f"📝 계약서 ID 자동 생성: {contract_id}")
        else:
            logger.info(f"📝 계약서 ID 사용: {contract_id}")
        
        # 3. language 정보를 임시 저장
        store_temp_data(contract_id, language)
        
        # 4. 파일 업로드 처리
        uploaded_keys = []
        failed_uploads = []
        
        for i, file in enumerate(files):
            try:
                logger.info(f"📁 파일 업로드 시작: {file.filename} ({i+1}/{len(files)})")
                
                # 파일명 처리
                original_filename = file.filename or f"contract_{i+1}.jpg"
                file_extension = os.path.splitext(original_filename)[1] or ".jpg"
                new_filename = f"contract_{i+1:03d}{file_extension}"
                
                # 파일 포인터를 처음으로 되돌리기
                file.file.seek(0)
                
                # S3에 업로드
                s3_key = upload_image_to_s3(S3_BUCKET_NAME, file, user_id, contract_id, new_filename)
                uploaded_keys.append(s3_key)
                
                logger.info(f"✅ 파일 업로드 성공: {new_filename} -> {s3_key}")
                
            except Exception as upload_error:
                error_msg = f"파일 업로드 실패: {file.filename}, 오류: {str(upload_error)}"
                logger.error(f"❌ {error_msg}")
                logger.error(f"❌ 상세 오류: {traceback.format_exc()}")
                
                # 오류 유형 분류
                error_type = type(upload_error).__name__
                if "permission" in str(upload_error).lower() or "access" in str(upload_error).lower():
                    error_category = "permission_error"
                elif "network" in str(upload_error).lower() or "connection" in str(upload_error).lower():
                    error_category = "network_error"
                elif "size" in str(upload_error).lower() or "large" in str(upload_error).lower():
                    error_category = "size_error"
                else:
                    error_category = "unknown_error"
                
                failed_uploads.append({
                    "filename": file.filename,
                    "error": str(upload_error),
                    "error_type": error_type,
                    "error_category": error_category
                })
                # 개별 파일 업로드 실패는 전체 실패로 이어지지 않도록 함

        # 5. 결과 검증
        if not uploaded_keys:
            # 모든 파일 업로드가 실패한 경우
            logger.error("❌ 모든 파일 업로드 실패")
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "모든 파일 업로드에 실패했습니다",
                    "failed_uploads": failed_uploads
                }
            )
        
        # 6. 성공 응답 생성
        success_response = {
            "message": "이미지 업로드 완료",
            "contract_id": contract_id,
            "s3_keys": uploaded_keys,
            "language": language,
            "file_count": len(uploaded_keys)
        }
        
        # 부분적 실패가 있는 경우 경고 추가
        if failed_uploads:
            success_response["warnings"] = {
                "message": f"{len(failed_uploads)}개 파일 업로드 실패",
                "failed_uploads": failed_uploads
            }
            logger.warning(f"⚠️ 부분적 성공: {len(uploaded_keys)}개 성공, {len(failed_uploads)}개 실패")
        
        logger.info(f"🎉 업로드 완료 - 계약서: {contract_id}, 성공: {len(uploaded_keys)}개")
        return success_response
        
    except HTTPException:
        # HTTPException은 그대로 re-raise
        raise
    except Exception as e:
        # 예상치 못한 오류 처리
        error_msg = str(e) or "알 수 없는 오류"
        tb = traceback.format_exc()
        logger.error(f"❌ 업로드 처리 중 예상치 못한 오류: {error_msg}")
        logger.error(f"❌ 상세 스택 트레이스:\n{tb}")
        
        # 사용자 친화적 오류 메시지
        if "timeout" in error_msg.lower():
            user_message = "업로드 시간이 초과되었습니다. 파일 크기를 확인하거나 잠시 후 다시 시도해 주세요."
        elif "memory" in error_msg.lower() or "out of memory" in error_msg.lower():
            user_message = "메모리 부족으로 업로드할 수 없습니다. 파일 수를 줄여서 다시 시도해 주세요."
        elif "network" in error_msg.lower() or "connection" in error_msg.lower():
            user_message = "네트워크 연결 오류가 발생했습니다. 인터넷 연결을 확인해 주세요."
        else:
            user_message = f"파일 업로드 중 오류가 발생했습니다: {error_msg}"
        
        raise HTTPException(
            status_code=500,
            detail={
                "message": user_message,
                "contract_id": contract_id if 'contract_id' in locals() else None,
                "error_type": type(e).__name__,
                "technical_error": error_msg
            }
        )

@router.get("/temp-data/{contract_id}", response_model=TempDataResponse)
async def get_contract_temp_data(contract_id: str):
    """계약서 임시 데이터 조회 (디버깅용)"""
    try:
        logger.info(f"🔍 임시 데이터 조회 요청: {contract_id}")
        data = get_temp_data(contract_id)
        
        if not data:
            logger.warning(f"⚠️ 임시 데이터 없음: {contract_id}")
            return {"error": "임시 데이터가 없거나 만료되었습니다.", "contract_id": contract_id}
        
        logger.info(f"✅ 임시 데이터 조회 성공: {contract_id}")
        return {
            "success": True,
            "contract_id": contract_id,
            "data": data
        }
        
    except Exception as e:
        error_msg = f"임시 데이터 조회 중 오류: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.error(f"❌ 상세 오류: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500, 
            detail={
                "message": "임시 데이터 조회에 실패했습니다",
                "contract_id": contract_id,
                "error_type": type(e).__name__,
                "technical_error": error_msg
            }
        )
