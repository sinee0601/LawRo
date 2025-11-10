"""
Chat Service
Thread-safe multi-user chat service with RAG capabilities
Combines in-memory cache with Firestore persistence
Optimized with monitoring, error handling, and cost optimization
"""

import os
import threading
import time
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import deque
import logging

from openai import OpenAI, APIError, RateLimitError, APIConnectionError
from langchain_upstage import UpstageEmbeddings
from langchain_chroma import Chroma

from ..models.chat import ChatMessage
from ..config import settings
from ..database import get_firebase, Collections

logger = logging.getLogger(__name__)

# Solar Model Matrix
SOLAR_MODEL_MATRIX = {
    "solar-mini": {"type": "base", "speed": "fast", "cost": "low", "use_case": "간단한 대화"},
    "solar-pro": {"type": "pro", "speed": "moderate", "cost": "medium", "use_case": "일반 RAG"},
    "solar-pro2": {"type": "pro2", "speed": "moderate", "cost": "medium", "use_case": "복잡한 RAG/구조화 출력"},
    "solar-max": {"type": "max", "speed": "slow", "cost": "high", "use_case": "고품질 생성"}
}


class PerformanceMetrics:
    """Performance metrics tracker"""
    def __init__(self, max_samples: int = 100):
        self.latencies = deque(maxlen=max_samples)
        self.successes = deque(maxlen=max_samples)
        self._lock = threading.Lock()

    def record_latency(self, latency: float):
        with self._lock:
            self.latencies.append(latency)

    def record_success(self, success: bool):
        with self._lock:
            self.successes.append(success)

    def get_average_latency(self) -> float:
        with self._lock:
            return sum(self.latencies) / len(self.latencies) if self.latencies else 0.0

    def get_success_rate(self) -> float:
        with self._lock:
            if not self.successes:
                return 0.0
            return sum(1 for s in self.successes if s) / len(self.successes)


@dataclass
class SessionData:
    """Session data class"""
    session_id: str
    messages: List[ChatMessage] = field(default_factory=list)
    last_activity: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    used_custom_prompt: bool = False

    def to_firestore_dict(self) -> Dict:
        """Convert to Firestore-compatible dict"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.timestamp(),
            "updated_at": self.last_activity.timestamp(),
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.timestamp()
                }
                for msg in self.messages
            ]
        }


class ChatService:
    """
    Thread-safe multi-user chat service with RAG
    Uses 2-tier storage: in-memory cache + Firestore persistence
    Enhanced with performance monitoring and error handling
    """

    _instance: Optional['ChatService'] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Thread safety
        self._session_lock = threading.RLock()
        self._sessions: Dict[str, SessionData] = {}

        # Configuration from settings
        self.MAX_SESSIONS = settings.CHAT_MAX_SESSIONS
        self.SESSION_TIMEOUT = timedelta(seconds=settings.CHAT_SESSION_TIMEOUT)
        self.MAX_MESSAGES_PER_SESSION = settings.CHAT_MAX_MESSAGES
        self.CLEANUP_INTERVAL = 60  # 1 minute
        self.RETRIEVAL_K = settings.CHAT_RETRIEVAL_K
        self.RETRIEVAL_SCORE_THRESHOLD = settings.CHAT_RETRIEVAL_SCORE_THRESHOLD
        self.LLM_MODEL = settings.CHAT_LLM_MODEL
        self.EMBEDDING_MODEL = settings.CHAT_EMBEDDING_MODEL
        self.MAX_RETRIES = settings.CHAT_MAX_RETRIES
        self.RETRY_DELAY = settings.CHAT_RETRY_DELAY

        # Performance metrics
        self._llm_metrics = PerformanceMetrics()
        self._rag_metrics = PerformanceMetrics()

        # API key validation
        self.api_key = settings.UPSTAGE_API_KEY
        if not self.api_key:
            logger.error("UPSTAGE_API_KEY not configured")
            raise ValueError("UPSTAGE_API_KEY environment variable is required")

        # Validate API key format
        if not self.api_key.startswith("up_"):
            logger.warning("API key format validation failed - expected 'up_' prefix")

        # Firebase
        self.use_firestore = settings.SESSION_BACKEND == "firestore"
        if self.use_firestore:
            try:
                self.firebase = get_firebase()
                self.db = self.firebase.db
                logger.info("Firestore session storage enabled")
            except Exception as e:
                logger.warning(f"Firestore initialization failed, using memory only: {e}")
                self.use_firestore = False

        # Initialize RAG chain
        self._initialize_rag_chain()

        # Start background cleanup
        self._start_cleanup_task()

        self._initialized = True
        logger.info(f"ChatService initialized successfully with model: {self.LLM_MODEL}")

    def _initialize_rag_chain(self):
        """Initialize RAG chain with ChromaDB and OpenAI client"""
        try:
            # Initialize OpenAI client with Upstage base URL
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.upstage.ai/v1",
                timeout=30.0,
                max_retries=self.MAX_RETRIES
            )

            # Initialize embeddings
            self.embedding = UpstageEmbeddings(
                model=self.EMBEDDING_MODEL,
                upstage_api_key=self.api_key
            )

            chroma_path = settings.CHROMA_PERSIST_DIRECTORY
            if not os.path.exists(chroma_path):
                logger.warning(f"ChromaDB not found at {chroma_path}")
                os.makedirs(chroma_path, exist_ok=True)
                logger.info(f"Created ChromaDB directory: {chroma_path}")

            self.vectorstore = Chroma(
                persist_directory=chroma_path,
                embedding_function=self.embedding,
                collection_name=settings.CHROMA_COLLECTION_NAME
            )

            # Hybrid retriever with similarity score threshold
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={
                    "k": self.RETRIEVAL_K,
                    "score_threshold": self.RETRIEVAL_SCORE_THRESHOLD
                }
            )

            logger.info(f"RAG chain initialized with model={self.LLM_MODEL}, embedding={self.EMBEDDING_MODEL}")

        except Exception as e:
            logger.error(f"RAG chain initialization failed: {e}")
            self._initialize_basic_llm()

    def _initialize_basic_llm(self):
        """Initialize basic LLM without RAG"""
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.upstage.ai/v1",
                timeout=30.0,
                max_retries=self.MAX_RETRIES
            )
            self.vectorstore = None
            self.retriever = None
            logger.warning("Using basic LLM without RAG")
        except Exception as e:
            logger.error(f"LLM initialization failed: {e}")
            self.client = None

    def _start_cleanup_task(self):
        """Start background cleanup task"""
        def cleanup_worker():
            while True:
                try:
                    self._cleanup_expired_sessions()
                    time.sleep(self.CLEANUP_INTERVAL)
                except Exception as e:
                    logger.error(f"Session cleanup error: {e}")
                    time.sleep(self.CLEANUP_INTERVAL)

        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info("Background session cleanup started")

    def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        with self._session_lock:
            current_time = datetime.now()
            expired_sessions = []

            for session_id, session_data in self._sessions.items():
                if current_time - session_data.last_activity > self.SESSION_TIMEOUT:
                    expired_sessions.append(session_id)

            for session_id in expired_sessions:
                del self._sessions[session_id]
                logger.debug(f"Expired session removed: {session_id[:8]}...")

            # Remove oldest sessions if exceeding max
            if len(self._sessions) > self.MAX_SESSIONS:
                sorted_sessions = sorted(
                    self._sessions.items(),
                    key=lambda x: x[1].last_activity
                )

                sessions_to_remove = len(self._sessions) - self.MAX_SESSIONS
                for session_id, _ in sorted_sessions[:sessions_to_remove]:
                    del self._sessions[session_id]
                    logger.debug(f"Session removed due to capacity: {session_id[:8]}...")

    def _load_session_from_firestore(self, session_id: str) -> Optional[SessionData]:
        """Load session from Firestore"""
        if not self.use_firestore:
            return None

        try:
            session_ref = self.db.collection(Collections.CHAT_SESSIONS).document(session_id)
            session_doc = session_ref.get()

            if not session_doc.exists:
                return None

            session_data_dict = session_doc.to_dict()

            # Parse messages from embedded array
            messages = [
                ChatMessage(
                    role=msg["role"],
                    content=msg["content"],
                    timestamp=datetime.fromtimestamp(msg["timestamp"])
                )
                for msg in session_data_dict.get("messages", [])
            ]

            return SessionData(
                session_id=session_id,
                messages=messages,
                last_activity=datetime.fromtimestamp(session_data_dict.get("updated_at", time.time())),
                user_id=session_data_dict.get("user_id"),
                created_at=datetime.fromtimestamp(session_data_dict.get("created_at", time.time())),
                used_custom_prompt=False
            )

        except Exception as e:
            logger.error(f"Failed to load session from Firestore: {e}")
            return None

    def _save_session_to_firestore(self, session_data: SessionData):
        """Save session to Firestore with batch update"""
        if not self.use_firestore:
            return

        try:
            session_ref = self.db.collection(Collections.CHAT_SESSIONS).document(session_data.session_id)
            session_ref.set(session_data.to_firestore_dict(), merge=True)

        except Exception as e:
            logger.error(f"Failed to save session to Firestore: {e}")

    def _get_or_create_session(self, session_id: Optional[str] = None, user_id: Optional[str] = None) -> str:
        """Get or create session"""
        with self._session_lock:
            if not session_id:
                session_id = str(uuid.uuid4())

            if session_id not in self._sessions:
                # Try to load from Firestore
                session_data = self._load_session_from_firestore(session_id)

                if session_data:
                    self._sessions[session_id] = session_data
                    logger.info(f"Session loaded from Firestore: {session_id[:8]}...")
                else:
                    # Create new session
                    self._sessions[session_id] = SessionData(
                        session_id=session_id,
                        user_id=user_id
                    )
                    logger.info(f"New session created: {session_id[:8]}...")
            else:
                # Update activity time
                self._sessions[session_id].last_activity = datetime.now()

            return session_id

    def _add_message_to_session(self, session_id: str, message: ChatMessage):
        """Add message to session (thread-safe)"""
        with self._session_lock:
            if session_id in self._sessions:
                session_data = self._sessions[session_id]
                session_data.messages.append(message)
                session_data.last_activity = datetime.now()

                # Limit message count
                if len(session_data.messages) > self.MAX_MESSAGES_PER_SESSION:
                    keep_count = self.MAX_MESSAGES_PER_SESSION // 2
                    session_data.messages = session_data.messages[-keep_count:]
                    logger.debug(f"Session {session_id[:8]}... messages trimmed")

                # Save to Firestore
                self._save_session_to_firestore(session_data)

    def _get_chat_history(self, session_id: str, exclude_last: bool = True) -> List[Dict]:
        """Get chat history (thread-safe)"""
        with self._session_lock:
            if session_id not in self._sessions:
                return []

            messages = self._sessions[session_id].messages
            if exclude_last and messages:
                messages = messages[:-1]

            return [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

    def _get_language_prompt(self, user_language: str) -> str:
        """Get language-specific prompt"""
        language_prompts = {
            "korean": "한국어로 답변하세요.",
            "english": "Please respond in English.",
            "chinese": "请用中文回答。",
            "vietnamese": "Vui lòng trả lời bằng tiếng Việt.",
            "japanese": "日本語で答えてください.",
            "thai": "กรุณาตอบเป็นภาษาไทย"
        }
        return language_prompts.get(user_language.lower(), "한국어로 답변하세요.")

    def _build_system_prompt(self, custom_prompt: Optional[str] = None, user_language: str = "korean", context: str = "") -> str:
        """Build system prompt with context"""
        language_instruction = self._get_language_prompt(user_language)

        if custom_prompt:
            if "{{context}}" in custom_prompt or "{context}" in custom_prompt:
                prompt_text = custom_prompt.replace("{{context}}", context).replace("{context}", context)
                return f"{prompt_text}\n\n{language_instruction}"
            else:
                return f"{custom_prompt}\n\n참고 문서:\n{context}\n\n{language_instruction}"
        else:
            default_prompt = """[역할] 법률 전문가로서 사용자에게 법률 상담을 제공합니다.

[지침]
- 제공된 문서 내용을 바탕으로 간결하고 명확한 답변을 생성하세요
- 문서 내용을 직접 인용하지 말고 자연스럽게 풀어서 설명하세요
- 법률과 관련된 질문에만 답변하세요
- 답을 모르거나 확실하지 않으면 솔직하게 모른다고 하세요
- 법률 관련 질문이 아닌 경우 "이 질문은 법률 상담 범위를 벗어납니다" 라고 응답하세요

[참고 문서]
{context}

{language_instruction}"""
            return default_prompt.replace("{context}", context).replace("{language_instruction}", language_instruction)

    async def _call_llm_with_retry(self, messages: List[Dict], session_id: str) -> str:
        """Call LLM API with retry logic"""
        for attempt in range(self.MAX_RETRIES):
            try:
                start_time = time.time()

                response = self.client.chat.completions.create(
                    model=self.LLM_MODEL,
                    messages=messages,
                    stream=False
                )

                latency = time.time() - start_time
                self._llm_metrics.record_latency(latency)
                self._llm_metrics.record_success(True)

                logger.debug(f"LLM response latency: {latency:.2f}s")
                return response.choices[0].message.content

            except RateLimitError as e:
                logger.warning(f"Rate limit error (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
                else:
                    self._llm_metrics.record_success(False)
                    raise

            except APIConnectionError as e:
                logger.warning(f"API connection error (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY)
                else:
                    self._llm_metrics.record_success(False)
                    raise

            except APIError as e:
                logger.error(f"Upstage API error: {e}")
                self._llm_metrics.record_success(False)

                # Check for specific error codes
                if hasattr(e, 'status_code'):
                    if e.status_code == 401:
                        return "API 키 오류: 크레딧이 부족하거나 키가 유효하지 않습니다. https://console.upstage.ai/billing 에서 확인해주세요."
                    elif e.status_code == 402:
                        return "크레딧 부족: 결제 수단을 등록해주세요."

                raise

            except Exception as e:
                logger.error(f"Unexpected error calling LLM: {e}")
                self._llm_metrics.record_success(False)
                raise

    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        user_language: Optional[str] = "korean",
        user_id: Optional[str] = None
    ) -> Tuple[str, List[ChatMessage], str]:
        """
        Process message (thread-safe)
        Returns: (response_text, chat_history, session_id)
        """

        # Get or create session
        session_id = self._get_or_create_session(session_id, user_id)

        # Handle custom prompt
        with self._session_lock:
            session_data = self._sessions[session_id]

            if session_data.used_custom_prompt and not custom_prompt:
                logger.info(f"Session {session_id[:8]}... reverting to default prompt")
                session_data.used_custom_prompt = False

            if custom_prompt:
                logger.info(f"Session {session_id[:8]}... applying custom prompt")
                session_data.used_custom_prompt = True
                session_data.messages = []  # Reset on custom prompt

        # Add user message
        user_message = ChatMessage(role="user", content=message)
        self._add_message_to_session(session_id, user_message)

        # Get chat history
        chat_history = [] if custom_prompt else self._get_chat_history(session_id)

        try:
            # Generate response using OpenAI client
            if not self.client:
                response_text = "죄송합니다. 현재 시스템에 문제가 있어 답변을 제공할 수 없습니다."
            else:
                # Retrieve relevant documents if vectorstore is available
                context = ""
                if self.retriever and not custom_prompt:
                    try:
                        rag_start = time.time()
                        docs = self.retriever.get_relevant_documents(message)
                        context = "\n\n".join([doc.page_content for doc in docs])
                        rag_latency = time.time() - rag_start

                        self._rag_metrics.record_latency(rag_latency)
                        self._rag_metrics.record_success(len(docs) > 0)

                        logger.debug(f"Retrieved {len(docs)} documents (latency: {rag_latency:.2f}s)")
                    except Exception as e:
                        logger.warning(f"Document retrieval failed: {e}")
                        self._rag_metrics.record_success(False)
                        context = ""

                # Build system prompt
                system_prompt = self._build_system_prompt(
                    custom_prompt=custom_prompt,
                    user_language=user_language,
                    context=context
                )

                # Prepare messages for API call
                messages = [{"role": "system", "content": system_prompt}]

                # Add chat history
                for msg in chat_history:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

                # Add current user message
                messages.append({"role": "user", "content": message})

                # Call LLM with retry logic
                response_text = await self._call_llm_with_retry(messages, session_id)

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            response_text = f"답변 생성 중 오류가 발생했습니다: {str(e)}"

        # Add AI response
        assistant_message = ChatMessage(role="assistant", content=response_text)
        self._add_message_to_session(session_id, assistant_message)

        # Return current messages
        with self._session_lock:
            current_messages = list(self._sessions[session_id].messages)

        return response_text, current_messages, session_id

    async def batch_process_messages(
        self,
        batch_requests: List[Dict]
    ) -> List[Tuple[str, List[ChatMessage], str]]:
        """
        Batch process multiple messages in parallel
        batch_requests: List of dicts with keys: message, session_id, custom_prompt, user_language, user_id
        """
        semaphore = asyncio.Semaphore(10)  # Limit concurrent requests

        async def process_with_semaphore(request: Dict):
            async with semaphore:
                return await self.process_message(**request)

        tasks = [process_with_semaphore(req) for req in batch_requests]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def get_chat_history(self, session_id: str) -> List[ChatMessage]:
        """Get chat history"""
        with self._session_lock:
            if session_id in self._sessions:
                return list(self._sessions[session_id].messages)

        # Try loading from Firestore
        session_data = self._load_session_from_firestore(session_id)
        if session_data:
            return session_data.messages

        return []

    async def clear_chat_history(self, session_id: str) -> bool:
        """Clear chat history"""
        with self._session_lock:
            if session_id in self._sessions:
                self._sessions[session_id].messages = []

                # Clear from Firestore
                if self.use_firestore:
                    try:
                        session_ref = self.db.collection(Collections.CHAT_SESSIONS).document(session_id)
                        session_ref.update({"messages": []})
                    except Exception as e:
                        logger.error(f"Failed to clear Firestore messages: {e}")

                return True
            return False

    async def create_new_session(self, user_id: Optional[str] = None) -> str:
        """Create new session"""
        return self._get_or_create_session(user_id=user_id)

    def get_session_stats(self) -> Dict:
        """Get session statistics"""
        with self._session_lock:
            total_sessions = len(self._sessions)
            total_messages = sum(len(session.messages) for session in self._sessions.values())
            active_sessions = sum(
                1 for s in self._sessions.values()
                if (datetime.now() - s.last_activity) < timedelta(minutes=5)
            )

            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "total_messages": total_messages,
                "max_sessions": self.MAX_SESSIONS,
                "session_timeout_minutes": self.SESSION_TIMEOUT.total_seconds() / 60,
                "storage_backend": "firestore" if self.use_firestore else "memory"
            }

    async def get_health_status(self) -> Dict:
        """Get comprehensive health status with performance metrics"""
        components = {
            "llm": "healthy" if self.client else "unhealthy",
            "vectorstore": "healthy" if self.vectorstore else "unavailable",
            "firestore": "healthy" if self.use_firestore else "unavailable"
        }

        overall_status = self.client is not None

        performance = {
            "llm_avg_latency_sec": round(self._llm_metrics.get_average_latency(), 2),
            "llm_success_rate": round(self._llm_metrics.get_success_rate(), 2),
            "rag_avg_latency_sec": round(self._rag_metrics.get_average_latency(), 2),
            "rag_hit_rate": round(self._rag_metrics.get_success_rate(), 2)
        }

        config = {
            "model": self.LLM_MODEL,
            "embedding_model": self.EMBEDDING_MODEL,
            "retrieval_k": self.RETRIEVAL_K,
            "score_threshold": self.RETRIEVAL_SCORE_THRESHOLD
        }

        return {
            "overall_status": overall_status,
            "components": components,
            "performance": performance,
            "config": config,
            "session_stats": self.get_session_stats()
        }

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up ChatService resources")
        # Cleanup code if needed
