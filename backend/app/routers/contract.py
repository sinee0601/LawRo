"""
Contract Router
Handles contract analysis endpoints
Compatible with existing frontend endpoints
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from ..dependencies import get_current_user_optional
from ..models.contract import (
    AnalyzeWithChatbotRequest,
    AnalyzeWithChatbotResponse,
    ChatbotStatusResponse,
    UploadResponse,
)
from ..services.contract_service import ContractService

logger = logging.getLogger(__name__)

router = APIRouter()

# Global contract service instance
_contract_service: ContractService = None


def get_contract_service() -> ContractService:
    """Get contract service instance"""
    global _contract_service
    if _contract_service is None:
        _contract_service = ContractService()
    return _contract_service


@router.post("/api/upload", response_model=UploadResponse)
async def upload_contract(
    user_id: str = Form(...),
    language: str = Form("korean"),
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Upload contract files

    Compatible with: POST /contract/api/upload
    """
    logger.info(f"Upload request from user {user_id}, {len(files)} files, language: {language}")

    try:
        contract_service = get_contract_service()

        # Validate files
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")

        # Upload to S3
        contract_id, uploaded_files, s3_urls = contract_service.upload_contract_files(
            files=files,
            user_id=user_id,
            language=language
        )

        logger.info(f"Upload successful: contract_id={contract_id}")

        return UploadResponse(
            message="파일 업로드 성공",
            contract_id=contract_id,
            uploaded_files=uploaded_files,
            s3_urls=s3_urls
        )

    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 업로드 실패: {str(e)}"
        )


@router.post("/api/analyze-with-chatbot", response_model=AnalyzeWithChatbotResponse)
async def analyze_with_chatbot(
    request: AnalyzeWithChatbotRequest,
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Analyze contract with OCR, GPT parsing, and chatbot analysis

    This is the main workflow for contract analysis
    Compatible with: POST /contract/api/analyze-with-chatbot
    """
    logger.info(
        f"Analyze request: user={request.user_id}, contract={request.contract_id}, "
        f"chatbot={request.use_chatbot}"
    )

    try:
        contract_service = get_contract_service()

        # Analyze contract
        result = await contract_service.analyze_contract_with_chatbot(
            user_id=request.user_id,
            contract_id=request.contract_id,
            use_chatbot=request.use_chatbot,
            user_language=request.user_language,
            use_saved_data=request.use_saved_data
        )

        logger.info(f"Analysis complete: contract={request.contract_id}, source={result['data_source']}, saved={result.get('saved_to_firestore', False)}")

        return AnalyzeWithChatbotResponse(
            message=result["message"],
            structured_result=result["structured_result"],
            chatbot_analysis=result.get("chatbot_analysis"),
            session_id=result.get("session_id"),
            data_source=result["data_source"],
            saved_to_firestore=result.get("saved_to_firestore", False),
            processing_info=result.get("processing_info")
        )

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계약서 분석 실패: {str(e)}"
        )


@router.get("/api/chatbot-status", response_model=ChatbotStatusResponse)
async def get_chatbot_status():
    """
    Check chatbot service status

    Compatible with: GET /contract/api/chatbot-status
    """
    try:
        from .chat import get_chat_service

        chat_service = get_chat_service()
        health = await chat_service.get_health_status()

        available = health["overall_status"]

        return ChatbotStatusResponse(
            status="available" if available else "unavailable",
            available=available,
            message="Chatbot service is ready" if available else "Chatbot service is not available"
        )

    except Exception as e:
        logger.error(f"Chatbot status check failed: {e}")
        return ChatbotStatusResponse(
            status="error",
            available=False,
            message=f"Failed to check chatbot status: {str(e)}"
        )


@router.get("/api/analysis-history/{user_id}")
async def get_analysis_history(
    user_id: str,
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Get analysis history for a user

    Returns list of all contract analyses saved in Firestore
    """
    logger.info(f"Fetching analysis history for user {user_id}")

    try:
        # Get analyses from Firestore
        from ..database import Collections, get_firebase
        firebase = get_firebase()

        # Query analyses for this user (without order_by to avoid index issues)
        query = firebase.db.collection(Collections.CONTRACT_ANALYSIS).where(
            "user_id", "==", user_id
        )

        docs = query.stream()
        analyses = []

        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            analyses.append(data)

        # Sort by created_at in Python instead of Firestore
        analyses.sort(
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )

        logger.info(f"Retrieved {len(analyses)} analyses for user {user_id}")

        return {
            "message": "분석 내역 조회 성공",
            "analyses": analyses,
            "count": len(analyses)
        }

    except Exception as e:
        logger.error(f"Failed to get analysis history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"분석 내역 조회 실패: {str(e)}"
        )


@router.delete("/api/analysis/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Delete a specific analysis from Firestore
    """
    logger.info(f"Deleting analysis {analysis_id}")

    try:
        from ..database import Collections, get_firebase
        firebase = get_firebase()

        # Delete document
        firebase.db.collection(Collections.CONTRACT_ANALYSIS).document(analysis_id).delete()

        logger.info(f"Analysis deleted: {analysis_id}")

        return {
            "message": "분석 내역이 삭제되었습니다",
            "analysis_id": analysis_id
        }

    except Exception as e:
        logger.error(f"Failed to delete analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"삭제 실패: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Contract service health check"""
    try:
        contract_service = get_contract_service()
        health_status = contract_service.get_health_status()

        return {
            "status": "healthy",
            "components": health_status
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
