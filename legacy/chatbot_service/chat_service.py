import os
import asyncio
import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

from models import ChatMessage
from langchain_upstage import UpstageEmbeddings, ChatUpstage
from langchain_chroma import Chroma
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

@dataclass
class SessionData:
    """세션 데이터 클래스"""
    session_id: str
    messages: List[ChatMessage]
    last_activity: datetime
    user_id: Optional[str] = None
    created_at: datetime = None
    used_custom_prompt: bool = False  # 커스텀 프롬프트 사용 여부 추적
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class ChatService:
    """스레드 안전한 멀티유저 채팅 서비스"""
    
    def __init__(self):
        # 스레드 안전을 위한 락
        self._session_lock = threading.RLock()
        self._sessions: Dict[str, SessionData] = {}
        
        # 설정
        self.MAX_SESSIONS = 1000  # 최대 세션 수
        self.SESSION_TIMEOUT = timedelta(minutes=5)  # 5분 후 세션 만료
        self.MAX_MESSAGES_PER_SESSION = 50  # 세션당 최대 메시지 수
        self.CLEANUP_INTERVAL = 60  # 1분마다 정리
        
        # API 키 설정
        self.api_key = os.getenv("UPSTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("UPSTAGE_API_KEY 환경변수가 설정되지 않았습니다.")
        
        # RAG 체인 초기화
        self._initialize_rag_chain()
        
        # 백그라운드 정리 작업 시작
        self._start_cleanup_task()
    
    def _initialize_rag_chain(self):
        """RAG 체인 초기화"""
        try:
            self.embedding = UpstageEmbeddings(
                model="solar-embedding-1-large",
                upstage_api_key=self.api_key
            )
            
            chroma_path = "chroma_db"
            if not os.path.exists(chroma_path):
                print(f"⚠️ Chroma DB를 찾을 수 없습니다: {chroma_path}")
                self._initialize_basic_llm()
                return
                
            self.vectorstore = Chroma(
                persist_directory=chroma_path,
                embedding_function=self.embedding
            )
            self.retriever = self.vectorstore.as_retriever(k=2)
            
            self.chat_llm = ChatUpstage(
                model="solar-pro",
                upstage_api_key=self.api_key
            )
            
            contextualize_q_prompt = ChatPromptTemplate.from_messages([
                ("system", "이전 대화 내용과 사용자 질문을 바탕으로, 문맥 없이도 이해할 수 있도록 질문을 다시 표현하세요."),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])
            
            self.history_aware_retriever = create_history_aware_retriever(
                self.chat_llm, self.retriever, contextualize_q_prompt
            )
            
            self.default_qa_prompt_text = """질문에 검색된 문서 내용을 바탕으로 답변하세요. 답을 모르면 모른다고 하세요. 답변은 20자 이내로 간결하고 명확하게 작성하세요. 법률과 관련된 질문에만 답변하세요. 관련되지 않을 경우 법률과 관련된 질문을 할 수 있도록 유도하는 말을 해주세요.

참고 문서: {context}"""
            
            print("✅ RAG 체인 초기화 완료")
            
        except Exception as e:
            print(f"❌ RAG 체인 초기화 오류: {e}")
            self._initialize_basic_llm()
    
    def _initialize_basic_llm(self):
        """기본 LLM만 초기화"""
        try:
            self.chat_llm = ChatUpstage(
                model="solar-pro", 
                upstage_api_key=self.api_key
            )
            self.rag_chain = None
            self.history_aware_retriever = None
            print("⚠️ 기본 LLM만 사용합니다")
        except Exception as llm_error:
            print(f"❌ LLM 초기화도 실패: {llm_error}")
            self.chat_llm = None
    
    def _start_cleanup_task(self):
        """백그라운드 정리 작업 시작"""
        def cleanup_worker():
            while True:
                try:
                    self._cleanup_expired_sessions()
                    time.sleep(self.CLEANUP_INTERVAL)
                except Exception as e:
                    print(f"⚠️ 세션 정리 중 오류: {e}")
                    time.sleep(self.CLEANUP_INTERVAL)
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        print("🔄 백그라운드 세션 정리 작업 시작")
    
    def _cleanup_expired_sessions(self):
        """만료된 세션 정리"""
        with self._session_lock:
            current_time = datetime.now()
            expired_sessions = []
            
            for session_id, session_data in self._sessions.items():
                if current_time - session_data.last_activity > self.SESSION_TIMEOUT:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self._sessions[session_id]
                print(f"🗑️ 만료된 세션 삭제: {session_id[:8]}...")
            
            # 최대 세션 수 초과 시 오래된 세션 삭제
            if len(self._sessions) > self.MAX_SESSIONS:
                sorted_sessions = sorted(
                    self._sessions.items(),
                    key=lambda x: x[1].last_activity
                )
                
                sessions_to_remove = len(self._sessions) - self.MAX_SESSIONS
                for session_id, _ in sorted_sessions[:sessions_to_remove]:
                    del self._sessions[session_id]
                    print(f"🗑️ 용량 초과로 삭제: {session_id[:8]}...")
    
    def _get_or_create_session(self, session_id: Optional[str] = None) -> str:
        """세션 가져오기 또는 생성"""
        with self._session_lock:
            if not session_id:
                session_id = str(uuid.uuid4())
            
            if session_id not in self._sessions:
                self._sessions[session_id] = SessionData(
                    session_id=session_id,
                    messages=[],
                    last_activity=datetime.now()
                )
                print(f"🆕 새 세션 생성: {session_id[:8]}...")
            else:
                # 활동 시간 업데이트
                self._sessions[session_id].last_activity = datetime.now()
            
            return session_id
    
    def _add_message_to_session(self, session_id: str, message: ChatMessage):
        """세션에 메시지 추가 (스레드 안전)"""
        with self._session_lock:
            if session_id in self._sessions:
                session_data = self._sessions[session_id]
                session_data.messages.append(message)
                session_data.last_activity = datetime.now()
                
                # 메시지 수 제한
                if len(session_data.messages) > self.MAX_MESSAGES_PER_SESSION:
                    # 오래된 메시지 삭제 (절반 유지)
                    keep_count = self.MAX_MESSAGES_PER_SESSION // 2
                    session_data.messages = session_data.messages[-keep_count:]
                    print(f"📝 세션 {session_id[:8]}... 메시지 개수 제한으로 정리")
    
    def _get_chat_history(self, session_id: str, exclude_last: bool = True) -> List[Dict]:
        """대화 히스토리 가져오기 (스레드 안전)"""
        with self._session_lock:
            if session_id not in self._sessions:
                return []
            
            messages = self._sessions[session_id].messages
            if exclude_last and messages:
                messages = messages[:-1]  # 마지막 메시지 제외
            
            return [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
    
    def _get_language_prompt(self, user_language: str) -> str:
        """언어별 프롬프트 반환"""
        language_prompts = {
            "korean": "한국어로 답변하세요.",
            "english": "Please respond in English.",
            "chinese": "请用中文回答。",
            "vietnamese": "Vui lòng trả lời bằng tiếng Việt.",
            "japanese": "日本語で答えてください.",
            "thai": "กรุณาตอบเป็นภาษาไทย"
        }
        return language_prompts.get(user_language.lower(), "한국어로 답변하세요.")
    
    def _create_rag_chain_with_prompt(self, custom_prompt: Optional[str] = None, user_language: str = "korean"):
        """RAG 체인 동적 생성"""
        if not hasattr(self, 'history_aware_retriever') or not self.history_aware_retriever:
            return None
            
        language_instruction = self._get_language_prompt(user_language)
        
        if custom_prompt:
            # 커스텀 프롬프트에 {{context}} 변수가 있는지 확인 (이중 중괄호)
            if "{{context}}" not in custom_prompt:
                prompt_text = f"{custom_prompt}\n\n참고 문서: {{context}}\n\n{language_instruction}"
            else:
                # {{context}}를 {context}로 변환하여 LangChain이 인식할 수 있도록 함
                # 계약서 데이터의 JSON 키들이 변수로 인식되지 않도록 이스케이프 처리
                prompt_text = custom_prompt.replace("{{context}}", "{context}")
                prompt_text = f"{prompt_text}\n\n{language_instruction}"
        else:
            # 기본 프롬프트에 context 변수 확실히 포함
            prompt_text = f"""대답 시, 언어에 맞게 공손한 말투로 답변해라. 질문에 검색된 문서 내용을 바탕으로 답변하세요. 답을 모르면 모른다고 하세요. 답변은 20자 이내로 간결하고 명확하게 작성하세요. 법률과 관련된 질문에만 답변하세요.
            관련되지 않을 경우 법률과 관련된 질문을 할 수 있도록 유도하는 말을 해주세요.

참고 문서: {{context}}

{language_instruction}"""
        
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_text),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        question_answer_chain = create_stuff_documents_chain(self.chat_llm, qa_prompt)
        return create_retrieval_chain(self.history_aware_retriever, question_answer_chain)
    
    async def process_message(
        self, 
        message: str, 
        session_id: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        user_language: Optional[str] = "korean"
    ) -> Tuple[str, List[ChatMessage]]:
        """메시지 처리 (스레드 안전)"""
        
        # 세션 생성/가져오기
        session_id = self._get_or_create_session(session_id)
        
        # 커스텀 프롬프트 사용 여부 확인 및 자동 복귀 처리
        with self._session_lock:
            session_data = self._sessions[session_id]
            
            # 이전에 커스텀 프롬프트를 사용했고 현재는 커스텀 프롬프트가 없다면
            if session_data.used_custom_prompt and not custom_prompt:
                print(f"🔄 세션 {session_id[:8]}... 기본 프롬프트로 자동 복귀")
                session_data.used_custom_prompt = False
            
            # 새로운 커스텀 프롬프트가 제공된 경우
            if custom_prompt:
                print(f"🎯 세션 {session_id[:8]}... 커스텀 프롬프트 적용: {custom_prompt[:50]}...")
                session_data.used_custom_prompt = True
                # 커스텀 프롬프트 시 세션 초기화
                session_data.messages = []
        
        # 사용자 메시지 추가
        user_message = ChatMessage(
            role="user",
            content=message
        )
        self._add_message_to_session(session_id, user_message)
        
        # 대화 히스토리 가져오기
        chat_history = [] if custom_prompt else self._get_chat_history(session_id)
        
        try:
            # RAG 체인으로 응답 생성
            if custom_prompt:
                # custom_prompt가 있으면 RAG 체인을 사용하지 않고 직접 LLM 호출
                if self.chat_llm:
                    # contract_parser에서 온 프롬프트는 이미 완성형이므로 message를 합쳐서 전달
                    final_prompt = f"{custom_prompt}\n\n사용자 질문: {message}"
                    response = self.chat_llm.invoke(final_prompt)
                    response_text = response.content
                else:
                    response_text = "죄송합니다. 현재 시스템에 문제가 있어 답변을 제공할 수 없습니다."
            else:
                # custom_prompt가 없으면 기존 RAG 체인 사용
                rag_chain = self._create_rag_chain_with_prompt(user_language=user_language)
                if rag_chain:
                    result = rag_chain.invoke({
                        "input": message,
                        "chat_history": chat_history
                    })
                    response_text = result["answer"]
                elif self.chat_llm:
                    language_instruction = self._get_language_prompt(user_language)
                    prompt = f"법률 상담 질문에 답변해주세요: {message}\n\n{language_instruction}"
                    response = self.chat_llm.invoke(prompt)
                    response_text = response.content
                else:
                    response_text = "죄송합니다. 현재 시스템에 문제가 있어 답변을 제공할 수 없습니다."
                
        except Exception as e:
            response_text = f"답변 생성 중 오류가 발생했습니다: {str(e)}"
        
        # AI 응답 메시지 추가
        assistant_message = ChatMessage(
            role="assistant",
            content=response_text
        )
        self._add_message_to_session(session_id, assistant_message)
        
        # 현재 세션의 메시지 반환
        with self._session_lock:
            current_messages = list(self._sessions[session_id].messages)
        
        return response_text, current_messages
    
    async def get_chat_history(self, session_id: str) -> List[ChatMessage]:
        """채팅 히스토리 조회"""
        with self._session_lock:
            if session_id in self._sessions:
                return list(self._sessions[session_id].messages)
            return []
    
    async def clear_chat_history(self, session_id: str) -> bool:
        """채팅 히스토리 삭제"""
        with self._session_lock:
            if session_id in self._sessions:
                self._sessions[session_id].messages = []
                return True
            return False
    
    async def create_new_session(self) -> str:
        """새 세션 생성"""
        return self._get_or_create_session()
    
    def get_session_stats(self) -> Dict:
        """세션 통계 정보"""
        with self._session_lock:
            total_sessions = len(self._sessions)
            total_messages = sum(len(session.messages) for session in self._sessions.values())
            
            return {
                "total_sessions": total_sessions,
                "total_messages": total_messages,
                "max_sessions": self.MAX_SESSIONS,
                "session_timeout_hours": self.SESSION_TIMEOUT.total_seconds() / 3600
            } 