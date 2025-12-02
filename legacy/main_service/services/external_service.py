import httpx
import asyncio
import time
from typing import Dict, Any, Optional
import os
from models import (
    ChatRequest, ChatResponse, ContractAnalyzeRequest, ContractAnalyzeResponse,
    ContractUploadExtractResponse, ContractAnalyzeCorrectedRequest, ContractAnalyzeCorrectedResponse
)
from config import Config

class ExternalService:
    """외부 서비스와의 통신을 담당하는 서비스"""
    
    def __init__(self):
        # 통일된 설정 사용
        self.chatbot_base_url = Config.CHATBOT_SERVICE_URL
        self.contract_base_url = Config.CONTRACT_SERVICE_URL
        
        # 통일된 HTTP 설정
        self.timeout = httpx.Timeout(Config.REQUEST_TIMEOUT)
        self.limits = httpx.Limits(
            max_keepalive_connections=Config.MAX_KEEPALIVE_CONNECTIONS,
            max_connections=Config.MAX_CONNECTIONS
        )
    
    async def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """HTTP 요청을 보내는 공통 메서드"""
        async with httpx.AsyncClient(timeout=self.timeout, limits=self.limits) as client:
            try:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise Exception(f"HTTP 오류 {e.response.status_code}: {e.response.text}")
            except httpx.RequestError as e:
                raise Exception(f"요청 오류: {str(e)}")
            except Exception as e:
                raise Exception(f"알 수 없는 오류: {str(e)}")
    
    # 헬스 체크 메서드들
    async def check_chatbot_health(self) -> Dict[str, Any]:
        """챗봇 서비스 헬스 체크"""
        try:
            start_time = time.time()
            response = await self._make_request("GET", f"{self.chatbot_base_url}/health")
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "details": response
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": None
            }
    
    async def check_contract_health(self) -> Dict[str, Any]:
        """계약서 분석 서비스 헬스 체크"""
        try:
            start_time = time.time()
            response = await self._make_request("GET", f"{self.contract_base_url}/health")
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "details": response
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": None
            }
    
    # 챗봇 서비스 관련 메서드들
    async def send_chat_message(self, request: ChatRequest) -> ChatResponse:
        """챗봇에 메시지 전송"""
        try:
            url = f"{self.chatbot_base_url}/chat/send"
            payload = {
                "message": request.message,
                "session_id": request.session_id,
                "context": request.context,
                "custom_prompt": request.custom_prompt,
                "user_language": request.user_language
            }
            
            response_data = await self._make_request("POST", url, json=payload)
            
            return ChatResponse(
                success=response_data.get("success", True),
                message=response_data.get("message", ""),
                chat_history=response_data.get("chat_history", []),
                processing_time=response_data.get("processing_time", 0.0)
            )
            
        except Exception as e:
            return ChatResponse(
                success=False,
                message=f"챗봇 서비스 오류: {str(e)}",
                chat_history=[],
                processing_time=0.0
            )
    
    async def create_chat_session(self) -> Dict[str, Any]:
        """새로운 채팅 세션 생성"""
        try:
            url = f"{self.chatbot_base_url}/chat/new-session"
            response_data = await self._make_request("POST", url)
            return response_data
            
        except Exception as e:
            return {
                "success": False,
                "message": f"세션 생성 실패: {str(e)}",
                "session_id": None
            }
    
    async def get_chat_history(self, session_id: str) -> Dict[str, Any]:
        """채팅 히스토리 조회"""
        try:
            url = f"{self.chatbot_base_url}/chat/history/{session_id}"
            response_data = await self._make_request("GET", url)
            return response_data
            
        except Exception as e:
            return {
                "success": False,
                "message": f"히스토리 조회 실패: {str(e)}",
                "chat_history": []
            }
    
    async def clear_chat_history(self, session_id: str) -> Dict[str, Any]:
        """채팅 히스토리 삭제"""
        try:
            url = f"{self.chatbot_base_url}/chat/history/{session_id}"
            response_data = await self._make_request("DELETE", url)
            return response_data
            
        except Exception as e:
            return {
                "success": False,
                "message": f"히스토리 삭제 실패: {str(e)}"
            }
    
    async def get_chatbot_stats(self) -> Dict[str, Any]:
        """챗봇 서비스 통계 조회"""
        try:
            url = f"{self.chatbot_base_url}/stats"
            response_data = await self._make_request("GET", url)
            return response_data.get("stats", {})
            
        except Exception as e:
            return {
                "error": f"통계 조회 실패: {str(e)}"
            }
    
    # 계약서 분석 서비스 관련 메서드들
    async def analyze_contract(self, request: ContractAnalyzeRequest) -> ContractAnalyzeResponse:
        """계약서 분석"""
        try:
            url = f"{self.contract_base_url}/api/analyze"
            payload = {
                "file_path": request.file_path,
                "file_url": request.file_url,
                "analysis_type": request.analysis_type,
                "custom_prompt": request.custom_prompt
            }
            
            # None 값 제거
            payload = {k: v for k, v in payload.items() if v is not None}
            
            response_data = await self._make_request("POST", url, json=payload)
            
            return ContractAnalyzeResponse(
                success=response_data.get("success", True),
                message=response_data.get("message", "분석이 완료되었습니다"),
                analysis_result=response_data.get("analysis_result"),
                processing_time=response_data.get("processing_time", 0.0),
                analysis_id=response_data.get("analysis_id")
            )
            
        except Exception as e:
            return ContractAnalyzeResponse(
                success=False,
                message=f"계약서 분석 서비스 오류: {str(e)}",
                analysis_result=None,
                processing_time=0.0,
                analysis_id=None
            )
    
    async def upload_contract(self) -> Dict[str, Any]:
        """계약서 업로드"""
        try:
            url = f"{self.contract_base_url}/api/upload"
            response_data = await self._make_request("POST", url)
            return response_data
            
        except Exception as e:
            return {
                "success": False,
                "message": f"업로드 실패: {str(e)}",
                "file_id": None
            }
    
    async def upload_and_extract_contract(self, files: list) -> Dict[str, Any]:
        """계약서 업로드 및 OCR 추출"""
        import uuid
        
        try:
            start_time = time.time()
            contract_id = str(uuid.uuid4())
            user_id = "anonymous"  # 기본 사용자 ID
            
            # 1단계: 파일 업로드
            url = f"{self.contract_base_url}/api/upload"
            
            # multipart/form-data로 파일 전송 (requests 스타일로 변경)
            import aiofiles
            import tempfile
            import os
            
            # 임시 파일로 저장 후 전송
            temp_files = []
            files_for_upload = []
            
            try:
                for i, file in enumerate(files):
                    # 파일 포인터를 처음으로 되감기
                    file.file.seek(0)
                    file_content = await file.read()
                    
                    # 임시 파일 생성
                    temp_fd, temp_path = tempfile.mkstemp(suffix=f"_{file.filename}")
                    temp_files.append(temp_path)
                    
                    # 임시 파일에 내용 쓰기
                    with open(temp_path, 'wb') as temp_file:
                        temp_file.write(file_content)
                    
                    # httpx 파일 업로드 형식
                    files_for_upload.append(
                        ('files', (file.filename, open(temp_path, 'rb'), file.content_type))
                    )
                
                # httpx로 multipart 데이터 전송
                async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
                    response = await client.post(
                        url,
                        data={
                            'user_id': user_id,
                            'contract_id': contract_id
                        },
                        files=files_for_upload
                    )
                
                # 파일 핸들 닫기
                for _, (_, file_handle, _) in files_for_upload:
                    file_handle.close()
                    
            finally:
                # 임시 파일 정리
                for temp_path in temp_files:
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                response.raise_for_status()
                upload_result = response.json()
            
            if not upload_result.get("s3_keys"):
                raise Exception("파일 업로드 실패: S3 키가 반환되지 않았습니다")
            
            # 2단계: OCR 및 구조화 분석
            analyze_url = f"{self.contract_base_url}/api/analyze"
            analyze_payload = {
                "contract_id": contract_id,
                "user_id": user_id
            }
            
            analyze_result = await self._make_request("POST", analyze_url, json=analyze_payload)
            
            processing_time = time.time() - start_time
            
            # 성공 응답 형식으로 반환
            return {
                "success": True,
                "message": "계약서 업로드 및 OCR 추출이 완료되었습니다",
                "contract_id": contract_id,
                "extracted_data": analyze_result.get("structured_result", {}),
                "page_summaries": analyze_result.get("page_summaries", []),
                "processing_time": processing_time
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"계약서 처리 중 오류: {str(e)}",
                "contract_id": None,
                "extracted_data": None,
                "page_summaries": None,
                "processing_time": 0.0
            }
    
    async def analyze_corrected_contract(self, corrected_data: Dict[str, Any]) -> Dict[str, Any]:
        """수정된 계약서 데이터를 contract_analyzer로 직접 전송하여 분석"""
        try:
            # contract_analyzer의 분석 엔드포인트로 직접 전송
            url = f"{self.contract_base_url}/api/analyze-corrected"
            
            response_data = await self._make_request("POST", url, json=corrected_data)
            
            # contract_analyzer에서 받은 JSON 형식 그대로 반환
            return response_data
            
        except Exception as e:
            return {
                "error": f"계약서 분석 중 오류: {str(e)}"
            }
    
    async def _get_analysis_template(self) -> str:
        """분석 요청 템플릿 가져오기"""
        try:
            # contract_analyzer에서 템플릿 가져오기
            url = f"{self.contract_base_url}/api/get-analysis-template"
            response = await self._make_request("GET", url)
            return response.get("template", "")
        except Exception as e:
            # 기본 템플릿 반환
            return """사용자의 질문은 json 형식으로 된 법률 분석 자료입니다. 양식에 맞게 항목 별로 위반 여부를 분석하고 등급화해 주세요.
최저임금 정보는 다음과 같습니다 년 : 원
2023: 9620, 2024: 9860, 2025: 10030

당신은 노동법 전문가입니다. 아래는 OCR로 추출된 근로계약서 항목입니다.
이를 바탕으로 "전체 분석 결과(총점 포함)", "하이라이트 항목", "법률 해석" 세 가지 섹션을 반드시 순수 텍스트로 구분하여 출력해 주세요.

{language_instruction}

📍 출처 문서: {context}"""
    
    def _convert_contract_data_to_context(self, contract_data: Dict[str, Any]) -> str:
        """계약서 데이터를 챗봇 컨텍스트 문자열로 변환"""
        context_parts = []
        
        for key, value in contract_data.items():
            if value:
                context_parts.append(f"{key}: {value}")
        
        return "\n".join(context_parts)
    
    # 종합 헬스 체크
    async def check_all_services_health(self) -> Dict[str, Any]:
        """모든 외부 서비스의 헬스 상태 확인"""
        # 병렬로 헬스 체크 실행
        chatbot_task = asyncio.create_task(self.check_chatbot_health())
        contract_task = asyncio.create_task(self.check_contract_health())
        
        chatbot_health = await chatbot_task
        contract_health = await contract_task
        
        # 전체 시스템 상태 판단
        all_healthy = (
            chatbot_health["status"] == "healthy" and 
            contract_health["status"] == "healthy"
        )
        
        return {
            "overall_status": "healthy" if all_healthy else "degraded",
            "services": {
                "chatbot": chatbot_health,
                "contract_analyzer": contract_health
            },
            "check_time": time.time()
        }
    
    # 서비스 간 통합 기능들
    async def analyze_contract_with_chat_context(
        self, 
        request: ContractAnalyzeRequest, 
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """계약서 분석 후 결과를 채팅 컨텍스트로 활용"""
        try:
            # 1. 계약서 분석 실행
            analysis_response = await self.analyze_contract(request)
            
            if not analysis_response.success:
                return {
                    "success": False,
                    "message": "계약서 분석에 실패했습니다",
                    "analysis_result": None,
                    "chat_context": None
                }
            
            # 2. 분석 결과를 채팅 컨텍스트로 변환
            analysis_summary = self._create_chat_context_from_analysis(analysis_response.analysis_result)
            
            # 3. 세션이 있으면 컨텍스트 업데이트를 위한 정보 반환
            result = {
                "success": True,
                "message": "계약서 분석이 완료되었습니다",
                "analysis_result": analysis_response.analysis_result,
                "chat_context": analysis_summary,
                "processing_time": analysis_response.processing_time,
                "analysis_id": analysis_response.analysis_id
            }
            
            if session_id:
                result["session_id"] = session_id
                result["context_message"] = "분석된 계약서 내용을 바탕으로 질문해주세요."
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"통합 분석 처리 중 오류: {str(e)}",
                "analysis_result": None,
                "chat_context": None
            }
    
    def _create_chat_context_from_analysis(self, analysis_result: Optional[Dict[str, Any]]) -> str:
        """분석 결과를 채팅 컨텍스트 문자열로 변환"""
        if not analysis_result:
            return "계약서 분석 결과가 없습니다."
        
        # 분석 결과의 주요 내용을 요약하여 컨텍스트 생성
        context_parts = []
        
        if "summary" in analysis_result:
            context_parts.append(f"계약서 요약: {analysis_result['summary']}")
        
        if "key_points" in analysis_result:
            key_points = analysis_result['key_points']
            if isinstance(key_points, list):
                context_parts.append(f"주요 사항: {', '.join(key_points)}")
            else:
                context_parts.append(f"주요 사항: {key_points}")
        
        if "risks" in analysis_result:
            risks = analysis_result['risks']
            if isinstance(risks, list):
                context_parts.append(f"위험 요소: {', '.join(risks)}")
            else:
                context_parts.append(f"위험 요소: {risks}")
        
        return " | ".join(context_parts) if context_parts else "계약서가 분석되었습니다." 