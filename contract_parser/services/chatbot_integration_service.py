import requests
import json
import os
import time
from typing import Dict, Optional, Any
import uuid
from datetime import datetime
from config.chatbot_config import chatbot_config, get_chatbot_endpoints


class ChatbotIntegrationService:
    """ChatBot Docker와의 통합 서비스 (서버 간 HTTP 통신)"""
    
    def __init__(self, chatbot_base_url: Optional[str] = None):
        """
        ChatBot 통합 서비스 초기화
        
        Args:
            chatbot_base_url: ChatBot Docker 서버 URL (없으면 설정에서 자동 로드)
        """
        # 설정에서 ChatBot 서버 정보 로드
        self.config = chatbot_config.get_connection_config()
        self.chatbot_base_url = chatbot_base_url or self.config["base_url"]
        self.timeout = self.config["timeout"]
        self.max_retries = self.config["max_retries"]
        self.retry_delay = self.config["retry_delay"]
        self.endpoints = get_chatbot_endpoints()
        
        # 커스텀 프롬프트 템플릿 로드
        self.custom_prompt_template = self._load_analysis_template()
        
        print(f"🔗 ChatBot 통합 서비스 초기화")
        print(f"   서버: {self.chatbot_base_url}")
        print(f"   환경: {self.config['environment']}")
        print(f"   타임아웃: {self.timeout}초")
        print(f"   최대 재시도: {self.max_retries}회")
    
    def _load_analysis_template(self) -> str:
        """분석 요청 템플릿 로드"""
        try:
            template_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'prompts', 
                'analysis_request_template.txt'
            )
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            print(f"✅ 커스텀 프롬프트 템플릿 로드 완료: {len(template)}자")
            return template
            
        except Exception as e:
            print(f"❌ 커스텀 프롬프트 템플릿 로드 실패: {str(e)}")
            # 기본 템플릿 사용
            return """
            사용자의 질문은 json 형식으로 된 법률 분석 자료입니다. 
            양식에 맞게 항목 별로 위반 여부를 분석하고 등급화해 주세요.
            노동법 전문가로서 상세한 분석을 제공해주세요.
            """
    
    def _make_http_request(self, method: str, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """재시도 로직이 포함된 HTTP 요청"""
        for attempt in range(self.max_retries + 1):
            try:
                if method.upper() == "GET":
                    response = requests.get(endpoint, timeout=self.timeout, **kwargs)
                elif method.upper() == "POST":
                    response = requests.post(endpoint, timeout=self.timeout, **kwargs)
                else:
                    raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
                
                # 성공적인 응답
                if response.status_code in [200, 201]:
                    return response
                    
                # 서버 오류인 경우 재시도
                elif response.status_code >= 500 and attempt < self.max_retries:
                    print(f"⚠️ 서버 오류 (HTTP {response.status_code}), {self.retry_delay}초 후 재시도... ({attempt + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    print(f"❌ HTTP 요청 실패: {response.status_code}")
                    return response
                    
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    print(f"⏰ 타임아웃, {self.retry_delay}초 후 재시도... ({attempt + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    print(f"❌ 최종 타임아웃: {endpoint}")
                    return None
                    
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries:
                    print(f"🔌 연결 오류, {self.retry_delay}초 후 재시도... ({attempt + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    print(f"❌ 최종 연결 실패: {endpoint}")
                    return None
                    
            except Exception as e:
                print(f"❌ 예상치 못한 오류: {str(e)}")
                return None
        
        return None

    def _format_contract_data_as_text(self, contract_data: Dict[str, Any]) -> str:
        """계약서 JSON 데이터를 읽기 쉬운 텍스트 형태로 변환"""
        try:
            text_parts = []
            
            # 사용자 정보
            if "employer" in contract_data:
                employer = contract_data["employer"]
                text_parts.append("=== 사용자(회사) 정보 ===")
                text_parts.append(f"회사명: {employer.get('company_name', '미기재')}")
                text_parts.append(f"전화번호: {employer.get('phone_number', '미기재')}")
                text_parts.append(f"주소: {employer.get('address', '미기재')}")
                text_parts.append(f"대표자명: {employer.get('representative_name', '미기재')}")
                text_parts.append("")
            
            # 근로자 정보
            if "employee" in contract_data:
                employee = contract_data["employee"]
                text_parts.append("=== 근로자 정보 ===")
                text_parts.append(f"이름: {employee.get('name', '미기재')}")
                text_parts.append(f"생년월일: {employee.get('date_of_birth', '미기재')}")
                text_parts.append(f"본국 주소: {employee.get('home_country_address', '미기재')}")
                text_parts.append("")
            
            # 계약 기간
            if "contract_period" in contract_data:
                period = contract_data["contract_period"]
                text_parts.append("=== 계약 기간 ===")
                text_parts.append(f"계약 기간: {period.get('new_contract_months', '미기재')}")
                if "probation_period" in period:
                    prob = period["probation_period"]
                    text_parts.append(f"수습 기간: {'있음' if prob.get('is_used') else '없음'} ({prob.get('months', '미기재')})")
                text_parts.append("")
            
            # 근무지
            if "workplace" in contract_data:
                text_parts.append("=== 근무지 ===")
                text_parts.append(f"근무지: {contract_data['workplace']}")
                text_parts.append("")
            
            # 업무 내용
            if "job_details" in contract_data:
                job = contract_data["job_details"]
                text_parts.append("=== 업무 내용 ===")
                text_parts.append(f"업종: {job.get('industry', '미기재')}")
                text_parts.append(f"사업 내용: {job.get('business_content', '미기재')}")
                text_parts.append(f"직무 설명: {job.get('job_description', '미기재')}")
                text_parts.append("")
            
            # 근무 시간
            if "working_hours" in contract_data:
                hours = contract_data["working_hours"]
                text_parts.append("=== 근무 시간 ===")
                text_parts.append(f"시작 시간: {hours.get('start_time', '미기재')}")
                text_parts.append(f"종료 시간: {hours.get('end_time', '미기재')}")
                text_parts.append(f"연장 근무: {hours.get('overtime_hours', '미기재')}")
                text_parts.append("")
            
            # 휴게 시간
            if "daily_break_minutes" in contract_data:
                text_parts.append("=== 휴게 시간 ===")
                text_parts.append(f"휴게 시간: {contract_data['daily_break_minutes']}")
                text_parts.append("")
            
            # 임금
            if "wages" in contract_data:
                wages = contract_data["wages"]
                text_parts.append("=== 임금 정보 ===")
                text_parts.append(f"월 총 임금: {wages.get('monthly_total_wage', '미기재')}")
                text_parts.append(f"기본급: {wages.get('base_pay', '미기재')}")
                if "allowances" in wages and wages["allowances"]:
                    text_parts.append("수당:")
                    for allowance in wages["allowances"]:
                        text_parts.append(f"  - {allowance.get('item', '미기재')}: {allowance.get('amount', '미기재')}")
                text_parts.append(f"상여금: {wages.get('bonus', '미기재')}")
                text_parts.append("")
            
            # 임금 지급
            if "wage_payment" in contract_data:
                payment = contract_data["wage_payment"]
                text_parts.append("=== 임금 지급 ===")
                text_parts.append(f"지급일: {payment.get('payment_date', '미기재')}")
                text_parts.append(f"지급 방법: {payment.get('payment_method', '미기재')}")
                text_parts.append("")
            
            # 4대 보험
            if "four_major_insurances" in contract_data:
                insurance = contract_data["four_major_insurances"]
                text_parts.append("=== 4대 보험 ===")
                text_parts.append(f"건강보험: {insurance.get('health_insurance', '미기재')}")
                text_parts.append(f"국민연금: {insurance.get('national_pension', '미기재')}")
                text_parts.append(f"고용보험: {insurance.get('employment_insurance', '미기재')}")
                text_parts.append(f"산재보험: {insurance.get('industrial_accident_insurance', '미기재')}")
                text_parts.append("")
            
            return "\n".join(text_parts)
            
        except Exception as e:
            print(f"❌ 계약서 데이터 텍스트 변환 오류: {str(e)}")
            # 실패 시 JSON 문자열로 대체
            return json.dumps(contract_data, ensure_ascii=False, indent=2)

    def create_user_session(self, user_id: Optional[str] = None) -> Optional[str]:
        """사용자별 새 세션 생성 (재시도 로직 포함)"""
        print(f"📝 세션 생성 요청: {user_id or 'Anonymous'}")
        
        response = self._make_http_request("POST", self.endpoints["create_session"])
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                session_id = data.get('session_id')
                
                print(f"✅ 새 세션 생성 성공: {session_id[:8]}... (사용자: {user_id or 'Anonymous'})")
                return session_id
            except json.JSONDecodeError:
                print(f"❌ 세션 응답 JSON 파싱 실패")
                return None
        else:
            print(f"❌ 세션 생성 실패")
            return None
    
    def analyze_contract_with_chatbot(
        self,
        parsed_contract_data: Dict[str, Any],
        user_id: Optional[str] = None,
        user_language: str = "korean"
    ) -> Dict[str, Any]:
        """
        파싱된 계약서 데이터를 ChatBot으로 분석 요청
        
        Args:
            parsed_contract_data: AI로 파싱된 계약서 JSON 데이터
            user_id: 사용자 ID (세션 관리용)
            user_language: 응답 언어
            
        Returns:
            분석 결과 딕셔너리
        """
        # 0. 챗봇 서버 연결 상태 확인
        print(f"🔍 챗봇 서버 연결 테스트: {self.chatbot_base_url}")
        try:
            health_response = self._make_http_request("GET", self.endpoints["health"])
            if health_response and health_response.status_code == 200:
                print(f"✅ 챗봇 서버 연결 정상")
            else:
                print(f"⚠️ 챗봇 서버 연결 문제: {health_response.status_code if health_response else 'No response'}")
        except Exception as e:
            print(f"❌ 챗봇 서버 연결 테스트 실패: {str(e)}")
        
        # 1. 사용자별 세션 생성
        session_id = self.create_user_session(user_id)
        if not session_id:
            return {
                "success": False,
                "error": "세션 생성에 실패했습니다.",
                "session_id": None,
                "analysis": None
            }
        
        # 2. 계약서 데이터를 읽기 쉬운 텍스트로 변환 (JSON 대신)
        contract_text = self._format_contract_data_as_text(parsed_contract_data)
        
        # 계약서 텍스트에서 중괄호 이스케이프 처리 (LangChain 변수 인식 방지)
        contract_text = contract_text.replace("{", "{{").replace("}", "}}")
        
        # 3. 커스텀 프롬프트 템플릿에 실제 데이터 삽입
        # 언어별 지시사항 설정
        language_instructions = {
            "korean": "모든 응답은 한국어로 작성해주세요.",
            "english": "Please provide all responses in English.",
            "chinese": "请用中文回答所有问题。",
            "vietnamese": "Vui lòng trả lời tất cả bằng tiếng Việt.",
            "thai": "กรุณาตอบทุกคำถามเป็นภาษาไทย"
        }
        
        language_instruction = language_instructions.get(user_language, language_instructions["korean"])
        
        # 템플릿의 플레이스홀더 대체
        custom_prompt = self.custom_prompt_template.replace("{{context}}", contract_text)
        custom_prompt = custom_prompt.replace("{{language_instruction}}", language_instruction)
        
        # 현재 연도 기준 최저임금 정보 업데이트
        current_year = datetime.now().year
        if current_year == 2025:
            custom_prompt = custom_prompt.replace("%%년", "2025").replace("%%원", "10030")
        elif current_year == 2024:
            custom_prompt = custom_prompt.replace("%%년", "2024").replace("%%원", "9860")
        else:
            custom_prompt = custom_prompt.replace("%%년", str(current_year)).replace("%%원", "10030")  # 기본값
        
        # 4. 분석 요청 메시지 구성 (간단하게)
        analysis_message = "위 계약서 데이터를 분석해주세요."
        
        # 5. ChatBot에 분석 요청 (재시도 로직 포함)
        payload = {
            "message": analysis_message,
            "session_id": session_id,
            "custom_prompt": custom_prompt,
            "user_language": user_language
        }
        
        print(f"📤 ChatBot에 계약서 분석 요청 전송...")
        print(f"   서버: {self.chatbot_base_url}")
        print(f"   세션: {session_id[:8]}...")
        print(f"   데이터 크기: {len(contract_text)}자")
        print(f"   언어: {user_language}")
        print(f"   커스텀 프롬프트 크기: {len(custom_prompt)}자")
        print(f"   프롬프트 미리보기: {custom_prompt[:200]}...")
        
        response = self._make_http_request("POST", self.endpoints["chat"], json=payload)
        
        # 디버깅: 응답 상세 정보 출력
        if response:
            print(f"🔍 ChatBot 응답 상태: {response.status_code}")
            print(f"🔍 응답 헤더: {dict(response.headers)}")
            try:
                response_data = response.json()
                print(f"🔍 응답 데이터 키들: {list(response_data.keys())}")
                print(f"🔍 응답 데이터 미리보기: {str(response_data)[:500]}...")
            except:
                print(f"🔍 응답 텍스트: {response.text[:500]}...")
        else:
            print("🔍 ChatBot 응답 없음 (None)")
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                
                analysis_result = {
                    "success": True,
                    "session_id": session_id,
                    "user_id": user_id,
                    "analysis": data.get('message', ''),  # 'response' → 'message'로 수정
                    "processing_time": data.get('processing_time', 0),
                    "chat_history": data.get('chat_history', []),
                    "original_data": parsed_contract_data,
                    "timestamp": datetime.now().isoformat(),
                    "server_info": {
                        "chatbot_url": self.chatbot_base_url,
                        "environment": self.config["environment"]
                    }
                }
                
                print(f"✅ 계약서 분석 완료 (처리시간: {analysis_result['processing_time']:.2f}초)")
                print(f"   분석 결과 길이: {len(analysis_result['analysis'])}자")
                
                return analysis_result
                
            except json.JSONDecodeError as e:
                error_msg = f"ChatBot 응답 JSON 파싱 실패: {str(e)}"
                print(f"❌ {error_msg}")
                
                return {
                    "success": False,
                    "error": error_msg,
                    "session_id": session_id,
                    "analysis": None
                }
        else:
            error_msg = f"ChatBot 서버 통신 실패 ({self.chatbot_base_url})"
            if response:
                error_msg += f": HTTP {response.status_code}"
                try:
                    error_details = response.text
                    if error_details:
                        error_msg += f" - {error_details[:200]}"
                except:
                    pass
            
            print(f"❌ {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "session_id": session_id,
                "analysis": None
            }
    
    def get_analysis_history(self, session_id: str) -> Dict[str, Any]:
        """분석 히스토리 조회"""
        try:
            response = requests.get(
                f"{self.chatbot_base_url}/chat/history/{session_id}",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "history": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def health_check(self) -> Dict[str, Any]:
        """ChatBot 서버 상태 확인 (재시도 없이 빠른 체크)"""
        try:
            # 빠른 헬스체크는 재시도 없이 진행
            response = requests.get(self.endpoints["health"], timeout=10)
            
            if response.status_code == 200:
                server_data = response.json() if response.content else {}
                return {
                    "success": True,
                    "status": "healthy",
                    "server_url": self.chatbot_base_url,
                    "environment": self.config["environment"],
                    "data": server_data
                }
            else:
                return {
                    "success": False,
                    "status": "unhealthy",
                    "server_url": self.chatbot_base_url,
                    "error": f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "status": "timeout",
                "server_url": self.chatbot_base_url,
                "error": "서버 응답 시간 초과"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "status": "connection_error",
                "server_url": self.chatbot_base_url,
                "error": "서버 연결 실패"
            }
        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "server_url": self.chatbot_base_url,
                "error": str(e)
            }
    
    def batch_analyze_contracts(
        self,
        contract_data_list: list,
        user_id: Optional[str] = None,
        user_language: str = "korean"
    ) -> list:
        """여러 계약서 일괄 분석"""
        results = []
        
        print(f"📋 {len(contract_data_list)}개 계약서 일괄 분석 시작...")
        
        for i, contract_data in enumerate(contract_data_list, 1):
            print(f"[{i}/{len(contract_data_list)}] 계약서 분석 중...")
            
            result = self.analyze_contract_with_chatbot(
                parsed_contract_data=contract_data,
                user_id=f"{user_id}_batch_{i}" if user_id else f"batch_{i}",
                user_language=user_language
            )
            
            results.append(result)
            
            # 서버 부하 방지를 위한 간격
            if i < len(contract_data_list):
                import time
                time.sleep(1)
        
        successful = [r for r in results if r["success"]]
        print(f"✅ 일괄 분석 완료: {len(successful)}/{len(contract_data_list)} 성공")
        
        return results

# 편의 함수들
def quick_contract_analysis(contract_data: Dict[str, Any], user_id: str = None) -> str:
    """빠른 계약서 분석"""
    service = ChatbotIntegrationService()
    result = service.analyze_contract_with_chatbot(contract_data, user_id)
    
    if result["success"]:
        return result["analysis"]
    else:
        return f"분석 실패: {result['error']}"

def check_chatbot_connection() -> bool:
    """ChatBot 연결 상태 확인"""
    service = ChatbotIntegrationService()
    health = service.health_check()
    return health["success"]

# 사용 예제
if __name__ == "__main__":
    # 테스트용 샘플 데이터
    sample_contract_data = {
        "contract_info": {
            "employer": "주식회사 예시",
            "employee": "김○○",
            "position": "일반직",
            "work_location": "서울시 강남구",
            "start_date": "2024-01-01"
        },
        "work_conditions": {
            "working_hours": "주 5일, 일 8시간",
            "salary": {
                "type": "월급",
                "amount": 2500000,
                "currency": "KRW"
            },
            "overtime_rate": "1.5배"
        },
        "benefits": {
            "insurance": ["국민연금", "건강보험", "고용보험", "산재보험"],
            "vacation": "연차 15일",
            "other": ["식대지원", "교통비지원"]
        }
    }
    
    # ChatBot 통합 서비스 테스트
    service = ChatbotIntegrationService()
    
    # 1. 서버 상태 확인
    health = service.health_check()
    print(f"ChatBot 서버 상태: {health}")
    
    if health["success"]:
        # 2. 계약서 분석 테스트
        result = service.analyze_contract_with_chatbot(
            parsed_contract_data=sample_contract_data,
            user_id="test_user_001",
            user_language="korean"
        )
        
        print("\n" + "="*50)
        print("📋 계약서 분석 결과:")
        print("="*50)
        
        if result["success"]:
            print(f"세션 ID: {result['session_id']}")
            print(f"처리 시간: {result['processing_time']:.2f}초")
            print(f"\n분석 내용:\n{result['analysis']}")
        else:
            print(f"분석 실패: {result['error']}")
    else:
        print("❌ ChatBot 서버에 연결할 수 없습니다.") 