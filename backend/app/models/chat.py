"""
Chat Models
Request and response models for chat endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role (user, assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message", min_length=1)
    session_id: Optional[str] = Field(None, description="Session ID")
    context: Optional[str] = Field(None, description="Context information (contract content)")
    custom_prompt: Optional[str] = Field(None, description="Custom QA prompt")
    user_language: Optional[str] = Field("korean", description="User language (korean, english, chinese, vietnamese, etc.)")


class ChatResponse(BaseModel):
    """Chat response model"""
    success: bool = Field(..., description="Processing success status")
    message: str = Field(..., description="Response message")
    chat_history: List[ChatMessage] = Field(..., description="Chat history")
    processing_time: float = Field(..., description="Processing time in seconds")
    session_id: Optional[str] = Field(None, description="Session ID")


class ChatHistoryResponse(BaseModel):
    """Chat history response"""
    success: bool
    session_id: str
    chat_history: List[ChatMessage]
    message_count: int


class NewSessionResponse(BaseModel):
    """New session creation response"""
    success: bool
    session_id: str
    message: str


class DeleteHistoryResponse(BaseModel):
    """Delete history response"""
    success: bool
    message: str
    session_id: str


class BatchMessageItem(BaseModel):
    """Single message in batch request"""
    message: str = Field(..., description="Message content")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt")
    user_language: Optional[str] = Field("korean", description="User language")


class BatchMessageRequest(BaseModel):
    """Batch message request"""
    session_id: str = Field(..., description="Session ID")
    messages: List[BatchMessageItem] = Field(..., description="List of messages to process")


class BatchMessageResponse(BaseModel):
    """Batch message response"""
    success: bool
    results: List[dict]
    processing_time: float
    session_id: str


class HealthStatusResponse(BaseModel):
    """Health status response"""
    overall_status: bool
    components: dict
    performance: dict
    config: dict
    session_stats: dict


class SessionStatsResponse(BaseModel):
    """Session statistics response"""
    total_sessions: int
    active_sessions: int
    total_messages: int
    max_sessions: int
    session_timeout_minutes: float
    storage_backend: str
