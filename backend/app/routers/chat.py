"""
Chat Router
Handles chat-related endpoints
Compatible with existing frontend endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends
import time
import logging

from ..models.chat import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    NewSessionResponse,
    DeleteHistoryResponse,
    BatchMessageRequest,
    BatchMessageResponse,
    HealthStatusResponse,
    SessionStatsResponse
)
from ..dependencies import get_current_user_optional
from ..services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter()

# Global chat service instance
_chat_service: ChatService = None


def get_chat_service() -> ChatService:
    """Get chat service instance"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service


@router.post("/send", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Send a chat message and receive AI response

    Compatible with: POST /chat/send
    """
    start_time = time.time()
    session_short_id = (request.session_id or "new")[:8]
    user_id = current_user["uid"] if current_user else None

    logger.info(f"Chat request [session: {session_short_id}] [user: {user_id}] | message: {request.message[:50]}...")

    try:
        chat_service = get_chat_service()

        # Input validation
        if not request.message or not request.message.strip():
            raise ValueError("Message is empty")

        if len(request.message) > 5000:
            raise ValueError("Message is too long (max 5000 characters)")

        # Process message
        response_message, chat_history, session_id = await chat_service.process_message(
            message=request.message.strip(),
            session_id=request.session_id,
            custom_prompt=request.custom_prompt,
            user_language=request.user_language or "korean",
            user_id=user_id
        )

        processing_time = time.time() - start_time

        logger.info(
            f"Chat response completed [session: {session_id[:8]}] | "
            f"time: {processing_time:.2f}s | "
            f"response length: {len(response_message)}"
        )

        return ChatResponse(
            success=True,
            message=response_message,
            chat_history=chat_history,
            processing_time=processing_time,
            session_id=session_id
        )

    except ValueError as ve:
        processing_time = time.time() - start_time
        logger.warning(f"Input validation error [session: {session_short_id}]: {ve}")

        return ChatResponse(
            success=False,
            message=f"입력 오류: {str(ve)}",
            chat_history=[],
            processing_time=processing_time,
            session_id=request.session_id
        )

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Chat processing error [session: {session_short_id}]: {e}", exc_info=True)

        return ChatResponse(
            success=False,
            message="죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
            chat_history=[],
            processing_time=processing_time,
            session_id=request.session_id
        )


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Get chat history for a specific session

    Compatible with: GET /chat/history/{session_id}
    """
    session_short_id = session_id[:8] if len(session_id) >= 8 else session_id
    user_id = current_user["uid"] if current_user else None

    logger.info(f"History request [session: {session_short_id}] [user: {user_id}]")

    try:
        chat_service = get_chat_service()

        # Input validation
        if not session_id or len(session_id) < 8:
            raise ValueError("Invalid session ID")

        history = await chat_service.get_chat_history(session_id)

        logger.info(f"History retrieved [session: {session_short_id}] | messages: {len(history)}")

        return ChatHistoryResponse(
            success=True,
            session_id=session_id,
            chat_history=history,
            message_count=len(history)
        )

    except ValueError as ve:
        logger.warning(f"History request validation error [session: {session_short_id}]: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    except Exception as e:
        logger.error(f"History retrieval error [session: {session_short_id}]: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history"
        )


@router.post("/new-session", response_model=NewSessionResponse)
async def create_new_chat_session(current_user: dict = Depends(get_current_user_optional)):
    """
    Create a new chat session

    Compatible with: POST /chat/new-session
    """
    user_id = current_user["uid"] if current_user else None
    logger.info(f"New session request [user: {user_id}]")

    try:
        chat_service = get_chat_service()
        session_id = await chat_service.create_new_session(user_id=user_id)
        session_short_id = session_id[:8]

        logger.info(f"New session created [session: {session_short_id}] [user: {user_id}]")

        return NewSessionResponse(
            success=True,
            session_id=session_id,
            message="새로운 채팅 세션이 생성되었습니다."
        )

    except Exception as e:
        logger.error(f"Session creation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create new session"
        )


@router.delete("/history/{session_id}", response_model=DeleteHistoryResponse)
async def clear_chat_history(
    session_id: str,
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Clear chat history for a specific session

    Compatible with: DELETE /chat/history/{session_id}
    """
    session_short_id = session_id[:8] if len(session_id) >= 8 else session_id
    user_id = current_user["uid"] if current_user else None

    logger.info(f"Clear history request [session: {session_short_id}] [user: {user_id}]")

    try:
        chat_service = get_chat_service()

        # Input validation
        if not session_id or len(session_id) < 8:
            raise ValueError("Invalid session ID")

        success = await chat_service.clear_chat_history(session_id)

        if success:
            logger.info(f"History cleared [session: {session_short_id}]")
        else:
            logger.warning(f"History clear failed [session: {session_short_id}] - session not found")

        return DeleteHistoryResponse(
            success=success,
            message="채팅 히스토리가 삭제되었습니다." if success else "삭제에 실패했습니다. 세션을 찾을 수 없습니다.",
            session_id=session_id
        )

    except ValueError as ve:
        logger.warning(f"Clear history validation error [session: {session_short_id}]: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    except Exception as e:
        logger.error(f"Clear history error [session: {session_short_id}]: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear chat history"
        )


@router.get("/health", response_model=HealthStatusResponse)
async def get_chat_health():
    """
    Get detailed health status of chat service

    Returns:
    - Overall system status
    - Component status (LLM, VectorStore, Firestore)
    - Performance metrics (latency, success rate)
    - Configuration details
    - Session statistics
    """
    try:
        chat_service = get_chat_service()
        health_status = await chat_service.get_health_status()

        logger.info("Health status retrieved successfully")

        return HealthStatusResponse(**health_status)

    except Exception as e:
        logger.error(f"Health status error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health status"
        )


@router.get("/stats", response_model=SessionStatsResponse)
async def get_session_stats():
    """
    Get session statistics

    Returns:
    - Total sessions count
    - Active sessions count
    - Total messages count
    - Configuration details
    """
    try:
        chat_service = get_chat_service()
        stats = chat_service.get_session_stats()

        logger.info(f"Session stats: {stats['total_sessions']} sessions, {stats['total_messages']} messages")

        return SessionStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Session stats error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session statistics"
        )


@router.post("/batch", response_model=BatchMessageResponse)
async def batch_process_messages(
    request: BatchMessageRequest,
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Process multiple messages in batch

    Efficient way to send multiple messages at once.
    Uses semaphore to limit concurrent requests.
    """
    start_time = time.time()
    session_short_id = request.session_id[:8]
    user_id = current_user["uid"] if current_user else None

    logger.info(
        f"Batch request [session: {session_short_id}] [user: {user_id}] | "
        f"messages: {len(request.messages)}"
    )

    try:
        chat_service = get_chat_service()

        # Input validation
        if not request.messages:
            raise ValueError("No messages provided")

        if len(request.messages) > 10:
            raise ValueError("Too many messages (max 10 per batch)")

        # Prepare batch requests
        batch_requests = [
            {
                "message": msg.message,
                "session_id": request.session_id,
                "custom_prompt": msg.custom_prompt,
                "user_language": msg.user_language or "korean",
                "user_id": user_id,
            }
            for msg in request.messages
        ]

        # Process batch
        results = await chat_service.batch_process_messages(batch_requests)

        processing_time = time.time() - start_time

        # Format results
        formatted_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                formatted_results.append({
                    "success": False,
                    "message": str(result),
                    "index": i,
                })
            else:
                response_text, chat_history, session_id = result
                formatted_results.append({
                    "success": True,
                    "message": response_text,
                    "index": i,
                })

        logger.info(
            f"Batch completed [session: {session_short_id}] | "
            f"time: {processing_time:.2f}s | "
            f"processed: {len(formatted_results)}/{len(request.messages)}"
        )

        return BatchMessageResponse(
            success=True,
            results=formatted_results,
            processing_time=processing_time,
            session_id=request.session_id
        )

    except ValueError as ve:
        processing_time = time.time() - start_time
        logger.warning(f"Batch validation error [session: {session_short_id}]: {ve}")

        return BatchMessageResponse(
            success=False,
            results=[{"error": str(ve)}],
            processing_time=processing_time,
            session_id=request.session_id
        )

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Batch processing error [session: {session_short_id}]: {e}", exc_info=True)

        return BatchMessageResponse(
            success=False,
            results=[{"error": "Internal server error"}],
            processing_time=processing_time,
            session_id=request.session_id
        )
