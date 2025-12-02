from fastapi import APIRouter, HTTPException, Depends, Form, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import httpx
import uuid
import json
import os

from models import (
    ContractAnalyzeRequest, ContractAnalyzeResponse,
    ContractAnalysisSaveRequest, ContractAnalysisSaveResponse
)
from services.user_service import UserService
from services.external_service import ExternalService
from database import get_db, save_contract_analysis, get_contract_analysis, get_user_contract_history

router = APIRouter()
security = HTTPBearer()
user_service = UserService()
external_service = ExternalService()

CONTRACT_SERVICE_URL = os.getenv("CONTRACT_SERVICE_URL", "http://3.106.213.23:8002")

@router.post("/upload-and-extract")
async def upload_and_extract_contract_legacy(
    user_id: str = Form("anonymous"),
    language: str = Form("korean"),
    contract_id: str = Form(None),
    files: List[UploadFile] = File(...)
):
    """
    ⚠️ **DEPRECATED: 레거시 엔드포인트 - 단계적 제거 예정**
    
    🚨 권장 새로운 워크플로우:
    1. POST /contract/api/upload (파일 업로드)
    2. POST /contract/api/analyze-with-chatbot (완전 통합 분석)
    
    📅 지원 종료 예정: 2024년 하반기
    🔄 이 엔드포인트는 호환성을 위해 당분간 유지되지만, 새로운 개발에는 사용하지 마세요.
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="업로드할 파일이 없습니다")
        
        for file in files:
            if not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail=f"이미지 파일만 업로드 가능합니다: {file.filename}")
        
        if not contract_id:
            contract_id = str(uuid.uuid4())
        
        files_data = []
        for file in files:
            file.file.seek(0)
            content = await file.read()
            files_data.append(('files', (file.filename, content, file.content_type)))
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            upload_response = await client.post(
                f"{CONTRACT_SERVICE_URL}/api/upload",
                data={
                    'user_id': user_id,
                    'language': language,
                    'contract_id': contract_id
                },
                files=files_data
            )
            upload_response.raise_for_status()
            upload_result = upload_response.json()
            
            returned_contract_id = upload_result.get('contract_id', contract_id)
            
            analyze_response = await client.post(
                f"{CONTRACT_SERVICE_URL}/api/analyze",
                json={
                    'user_id': user_id,
                    'contract_id': returned_contract_id
                }
            )
            analyze_response.raise_for_status()
            analyze_result = analyze_response.json()
        
        return {
            "success": True,
            "message": "계약서 업로드 및 OCR 추출이 완료되었습니다",
            "contract_id": returned_contract_id,
            "extracted_data": analyze_result.get("structured_result", {}),
            "page_summaries": analyze_result.get("page_summaries", []),
            "processing_time": analyze_result.get("processing_info", {}).get("total_time", 0.0),
            "language": language
        }
        
    except httpx.HTTPStatusError as e:
        error_detail = f"계약서 서비스 오류: {e.response.text}"
        print(f"[ERROR] HTTPStatusError: {error_detail}")
        raise HTTPException(status_code=e.response.status_code, detail=error_detail)
    except httpx.TimeoutException as e:
        error_detail = f"계약서 서비스 타임아웃: {str(e)}"
        print(f"[ERROR] TimeoutException: {error_detail}")
        raise HTTPException(status_code=504, detail=error_detail)
    except Exception as e:
        error_detail = f"계약서 업로드 및 추출 중 오류가 발생했습니다: {str(e) or '알 수 없는 오류'}"
        print(f"[ERROR] General Exception: {error_detail}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_detail)

@router.post("/analyze-corrected")
async def analyze_corrected_contract(
    corrected_data: Dict[str, Any]
):
    """수정된 계약서 데이터 법률 분석 (레거시)"""
    try:
        response = await external_service.analyze_corrected_contract(corrected_data)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"계약서 분석 중 오류가 발생했습니다: {str(e)}")

@router.post("/analyze", response_model=ContractAnalyzeResponse)
async def analyze_contract(
    request: ContractAnalyzeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    ⚠️ **DEPRECATED: 레거시 분석 엔드포인트**
    
    🔄 새로운 방식: `/contract/api/analyze-with-chatbot` 사용 권장
    """
    try:
        token = credentials.credentials
        user_data = await user_service.get_user_by_token(token)
        
        response = await external_service.analyze_contract(request)
        
        if response.success:
            await user_service.save_contract_analysis(
                user_id=user_data["user_id"],
                contract_id=response.analysis_id or "legacy_analysis",
                language="korean",
                analysis_result=json.dumps(response.analysis_result) if response.analysis_result else None
            )
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"계약서 분석 중 오류가 발생했습니다: {str(e)}")

@router.post("/upload")
async def upload_contract(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    ⚠️ **DEPRECATED: 레거시 업로드 엔드포인트**
    
    🔄 새로운 방식: `/contract/api/upload` 프록시 사용 권장
    """
    try:
        token = credentials.credentials
        user_data = await user_service.get_user_by_token(token)
        
        response = await external_service.upload_contract()
        return response
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"계약서 업로드 중 오류가 발생했습니다: {str(e)}")

@router.get("/history")
async def get_contract_history(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """사용자의 계약서 분석 히스토리 조회 (DB 기반으로 수정)"""
    try:
        token = credentials.credentials
        user_data = await user_service.get_user_by_token(token)
        
        history = get_user_contract_history(db=db, user_id=user_data["user_id"])
        
        return {
            "success": True,
            "history": history
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/save-analysis", response_model=ContractAnalysisSaveResponse)
async def save_contract_analysis_data(
    request: ContractAnalysisSaveRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    수정된 계약서 분석 결과를 DB에 저장
    - 앱에서 사용자가 수정한 계약서 데이터를 받아서 저장
    - 나중에 챗봇 분석 시 이 데이터를 사용
    """
    try:
        token = credentials.credentials
        user_data = await user_service.get_user_by_token(token)
        
        if user_data["user_id"] != request.user_id:
            raise HTTPException(status_code=403, detail="다른 사용자의 데이터에 접근할 수 없습니다")
        
        success = save_contract_analysis(
            db=db,
            user_id=request.user_id,
            contract_id=request.contract_id,
            analysis_result=request.analysis_result,
            language=request.language
        )
        
        if success:
            return ContractAnalysisSaveResponse(
                success=True,
                message="계약서 분석 결과가 성공적으로 저장되었습니다",
                contract_id=request.contract_id
            )
        else:
            raise HTTPException(status_code=500, detail="데이터 저장에 실패했습니다")
            
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 결과 저장 중 오류가 발생했습니다: {str(e)}")

@router.get("/analysis/{contract_id}")
async def get_saved_contract_analysis(
    contract_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """저장된 계약서 분석 결과 조회"""
    try:
        token = credentials.credentials
        user_data = await user_service.get_user_by_token(token)
        
        analysis_data = get_contract_analysis(db=db, contract_id=contract_id)
        
        if not analysis_data:
            raise HTTPException(status_code=404, detail="해당 계약서 분석 결과를 찾을 수 없습니다")
        
        if analysis_data["user_id"] != user_data["user_id"]:
            raise HTTPException(status_code=403, detail="다른 사용자의 데이터에 접근할 수 없습니다")
        
        return {
            "success": True,
            "contract_id": contract_id,
            "analysis_result": analysis_data["analysis_result"],
            "language": analysis_data["language"],
            "created_at": analysis_data["created_at"],
            "updated_at": analysis_data["updated_at"]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 결과 조회 중 오류가 발생했습니다: {str(e)}")