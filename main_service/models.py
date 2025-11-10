from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# 챗봇 관련 모델 (기존 chatbot-docker에서 가져옴)
class ChatMessage(BaseModel):
    """채팅 메시지 모델"""
    role: str = Field(..., description="메시지 역할 (user, assistant)")
    content: str = Field(..., description="메시지 내용")
    timestamp: datetime = Field(default_factory=datetime.now, description="메시지 시간")

class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    message: str = Field(..., description="사용자 메시지", min_length=1)
    session_id: Optional[str] = Field(None, description="세션 ID")
    context: Optional[str] = Field(None, description="문맥 정보 (계약서 내용)")
    custom_prompt: Optional[str] = Field(None, description="커스텀 QA 프롬프트")
    user_language: Optional[str] = Field("korean", description="사용자 언어 (korean, english, chinese, vietnamese, etc.)")

class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    success: bool = Field(..., description="처리 성공 여부")
    message: str = Field(..., description="응답 메시지")
    chat_history: List[ChatMessage] = Field(..., description="대화 히스토리")
    processing_time: float = Field(..., description="처리 시간(초)")

# 사용자 관리 모델
class UserSignupRequest(BaseModel):
    """사용자 회원가입 요청 모델"""
    email: EmailStr = Field(..., description="이메일 주소")
    password: str = Field(..., description="비밀번호", min_length=6)
    full_name: str = Field(..., description="사용자 이름", min_length=1)

class UserSignupResponse(BaseModel):
    """사용자 회원가입 응답 모델"""
    success: bool = Field(..., description="회원가입 성공 여부")
    message: str = Field(..., description="응답 메시지")
    user_id: Optional[str] = Field(None, description="생성된 사용자 ID")

class UserLoginRequest(BaseModel):
    """사용자 로그인 요청 모델"""
    email: EmailStr = Field(..., description="이메일 주소")
    password: str = Field(..., description="비밀번호")

class UserLoginResponse(BaseModel):
    """사용자 로그인 응답 모델"""
    success: bool = Field(..., description="로그인 성공 여부")
    message: str = Field(..., description="응답 메시지")
    access_token: Optional[str] = Field(None, description="JWT 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    user_info: Optional[Dict[str, Any]] = Field(None, description="사용자 정보")

class UserProfile(BaseModel):
    """사용자 프로필 모델"""
    user_id: str = Field(..., description="사용자 ID")
    email: str = Field(..., description="이메일")
    full_name: Optional[str] = Field(None, description="이름")
    created_at: datetime = Field(..., description="가입일시")
    last_login: Optional[datetime] = Field(None, description="마지막 로그인")

# 소셜 로그인 관련 모델 (main-docker2에서 추가)
class SocialLoginResponse(BaseModel):
    """소셜 로그인 응답 모델"""
    success: bool = Field(..., description="로그인 성공 여부")
    message: str = Field(..., description="응답 메시지")
    access_token: Optional[str] = Field(None, description="JWT 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    user_info: Optional[Dict[str, Any]] = Field(None, description="사용자 정보")

class GoogleUserInfo(BaseModel):
    """구글 사용자 정보 모델"""
    email: str = Field(..., description="이메일")
    name: Optional[str] = Field(None, description="이름")
    picture: Optional[str] = Field(None, description="프로필 사진 URL")
    given_name: Optional[str] = Field(None, description="이름")
    family_name: Optional[str] = Field(None, description="성")
    locale: Optional[str] = Field(None, description="지역 설정")

class KakaoUserInfo(BaseModel):
    """카카오 사용자 정보 모델"""
    id: int = Field(..., description="카카오 사용자 ID")
    email: Optional[str] = Field(None, description="이메일")
    nickname: Optional[str] = Field(None, description="닉네임")
    profile_image: Optional[str] = Field(None, description="프로필 사진 URL")
    gender: Optional[str] = Field(None, description="성별")
    age_range: Optional[str] = Field(None, description="연령대")

class NaverUserInfo(BaseModel):
    """네이버 사용자 정보 모델"""
    id: str = Field(..., description="네이버 사용자 ID")
    email: str = Field(..., description="이메일")
    name: Optional[str] = Field(None, description="이름")
    nickname: Optional[str] = Field(None, description="닉네임")
    profile_image: Optional[str] = Field(None, description="프로필 사진 URL")
    gender: Optional[str] = Field(None, description="성별")
    age: Optional[str] = Field(None, description="연령대")

# 계약서 분석 관련 모델
class ContractAnalyzeRequest(BaseModel):
    """계약서 분석 요청 모델"""
    user_id: str = Field(..., description="사용자 ID")
    contract_id: str = Field(..., description="계약서 ID")
    file_path: Optional[str] = Field(None, description="계약서 파일 경로")
    file_url: Optional[str] = Field(None, description="계약서 파일 URL")
    analysis_type: Optional[str] = Field("full", description="분석 타입 (full, summary, risk)")
    custom_prompt: Optional[str] = Field(None, description="커스텀 분석 프롬프트")

class ContractUploadExtractRequest(BaseModel):
    """계약서 업로드 및 OCR 추출 요청 모델"""
    user_id: str = Field(..., description="사용자 ID")
    language: str = Field("korean", description="사용자 언어")

class ContractUploadExtractResponse(BaseModel):
    """계약서 업로드 및 OCR 추출 응답 모델"""
    success: bool = Field(..., description="처리 성공 여부")
    message: str = Field(..., description="응답 메시지")
    contract_id: Optional[str] = Field(None, description="계약서 ID")
    extracted_data: Optional[Dict[str, Any]] = Field(None, description="OCR 추출된 데이터 (JSON)")
    page_summaries: Optional[List[str]] = Field(None, description="페이지별 요약")
    processing_time: float = Field(..., description="처리 시간(초)")

class ContractAnalyzeCorrectedRequest(BaseModel):
    """수정된 계약서 데이터 분석 요청 모델"""
    user_id: str = Field(..., description="사용자 ID")
    language: str = Field("korean", description="사용자 언어")
    corrected_data: Dict[str, Any] = Field(..., description="사용자가 수정한 계약서 데이터")
    contract_id: Optional[str] = Field(None, description="계약서 ID")

class ContractAnalyzeCorrectedResponse(BaseModel):
    """수정된 계약서 데이터 분석 응답 모델"""
    success: bool = Field(..., description="분석 성공 여부")
    message: str = Field(..., description="응답 메시지")
    legal_analysis: Optional[str] = Field(None, description="법률 분석 결과")
    session_id: Optional[str] = Field(None, description="챗봇 세션 ID")
    processing_time: float = Field(..., description="처리 시간(초)")

class ContractAnalyzeResponse(BaseModel):
    """계약서 분석 응답 모델"""
    success: bool = Field(..., description="분석 성공 여부")
    message: str = Field(..., description="응답 메시지")
    analysis_result: Optional[Dict[str, Any]] = Field(None, description="분석 결과")
    processing_time: float = Field(..., description="처리 시간(초)")
    analysis_id: Optional[str] = Field(None, description="분석 ID")

class ContractUploadRequest(BaseModel):
    """계약서 업로드 요청 모델"""
    file_name: str = Field(..., description="파일명")
    file_type: str = Field(..., description="파일 타입")
    file_size: int = Field(..., description="파일 크기")

class ContractUploadResponse(BaseModel):
    """계약서 업로드 응답 모델"""
    success: bool = Field(..., description="업로드 성공 여부")
    message: str = Field(..., description="응답 메시지")
    file_id: Optional[str] = Field(None, description="업로드된 파일 ID")
    upload_url: Optional[str] = Field(None, description="업로드 URL")

# 분석 히스토리 모델
class ContractAnalysisHistory(BaseModel):
    """계약서 분석 히스토리 모델"""
    analysis_id: str = Field(..., description="분석 ID")
    user_id: str = Field(..., description="사용자 ID")
    file_name: str = Field(..., description="파일명")
    analysis_type: str = Field(..., description="분석 타입")
    analysis_result: Dict[str, Any] = Field(..., description="분석 결과")
    created_at: datetime = Field(..., description="분석 일시")
    processing_time: float = Field(..., description="처리 시간")

# 서비스 상태 모델
class ServiceStatus(BaseModel):
    """서비스 상태 모델"""
    service_name: str = Field(..., description="서비스명")
    status: str = Field(..., description="상태 (healthy, unhealthy)")
    response_time: Optional[float] = Field(None, description="응답 시간")
    last_check: datetime = Field(default_factory=datetime.now, description="마지막 체크 시간")

class ServerStats(BaseModel):
    """서버 통계 모델"""
    total_users: int = Field(..., description="총 사용자 수")
    active_sessions: int = Field(..., description="활성 세션 수")
    total_contracts_analyzed: int = Field(..., description="총 분석된 계약서 수")
    uptime: float = Field(..., description="서버 가동 시간")
    timestamp: datetime = Field(default_factory=datetime.now, description="통계 시간")

# 계약서 분석 저장 관련 모델 (main-docker에서 유지)
class ContractAnalysisSaveRequest(BaseModel):
    """수정된 계약서 분석 결과 저장 요청 모델"""
    user_id: str = Field(..., description="사용자 ID")
    contract_id: str = Field(..., description="계약서 ID")
    analysis_result: Dict[str, Any] = Field(..., description="수정된 분석 결과 데이터")
    language: Optional[str] = Field("korean", description="사용자 언어")

class ContractAnalysisSaveResponse(BaseModel):
    """계약서 분석 결과 저장 응답 모델"""
    success: bool = Field(..., description="저장 성공 여부")
    message: str = Field(..., description="응답 메시지")
    contract_id: str = Field(..., description="계약서 ID")
    saved_at: datetime = Field(default_factory=datetime.now, description="저장 시간")

class ContractAnalysisData(BaseModel):
    """저장된 계약서 분석 데이터 모델"""
    id: int = Field(..., description="분석 데이터 ID")
    user_id: str = Field(..., description="사용자 ID")
    contract_id: str = Field(..., description="계약서 ID")
    analysis_result: Dict[str, Any] = Field(..., description="분석 결과 JSON")
    language: str = Field(..., description="사용자 언어")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간") 