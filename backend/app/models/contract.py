"""
Contract Models
Request and response models for contract analysis endpoints
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Upload Models
class UploadResponse(BaseModel):
    """File upload response"""
    message: str
    contract_id: str
    uploaded_files: List[str]
    s3_urls: List[str]


# Analysis Models
class AnalyzeRequest(BaseModel):
    """Basic contract analysis request"""
    user_id: str = Field(..., description="User ID")
    contract_id: str = Field(..., description="Contract ID")


class AnalyzeResponse(BaseModel):
    """Basic contract analysis response"""
    message: str = Field(default="계약서 분석 완료")
    structured_result: Dict[str, Any] = Field(..., description="Structured analysis result")
    processing_info: Optional[Dict[str, Any]] = Field(None, description="Processing information")


class AnalyzeWithChatbotRequest(BaseModel):
    """Contract analysis with chatbot request"""
    user_id: str = Field(..., description="User ID")
    contract_id: str = Field(..., description="Contract ID")
    use_chatbot: bool = Field(default=True, description="Use chatbot analysis")
    user_language: Optional[str] = Field(None, description="User language")
    use_saved_data: bool = Field(default=True, description="Use saved analysis data")


class AnalyzeWithChatbotResponse(BaseModel):
    """Contract analysis with chatbot response"""
    message: str = Field(default="계약서 분석 및 법률 상담 완료")
    page_summaries: Optional[List[str]] = Field(None, description="Page summaries")
    structured_result: Dict[str, Any] = Field(..., description="Structured analysis result")
    chatbot_analysis: Optional[Dict[str, Any]] = Field(None, description="Chatbot legal analysis")
    session_id: Optional[str] = Field(None, description="Chatbot session ID")
    processing_info: Optional[Dict[str, Any]] = Field(None, description="Processing information")
    data_source: str = Field(..., description="Data source (saved_db, fresh_ocr)")
    saved_to_firestore: bool = Field(default=False, description="Whether analysis was saved to Firestore")


# Template Models
class TemplateResponse(BaseModel):
    """Contract template response"""
    templates: List[Dict[str, Any]]


# Health Check
class ChatbotStatusResponse(BaseModel):
    """Chatbot service status"""
    status: str
    available: bool
    message: Optional[str] = None
