#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LawRo 계약서 분석 완전한 플로우 테스트
- 회원가입/로그인
- 계약서 업로드
- 기본 분석
- 수정된 데이터 저장
- 저장된 데이터 조회
- 챗봇 통합 분석 (저장된 데이터 사용)
- 히스토리 조회
"""

import requests
import json
import time
import os
from typing import Dict, Any, Optional

class LawRoAPITester:
    def __init__(self, base_url: str = "http://16.176.26.197:8000"):
        self.base_url = base_url
        self.access_token = None
        self.user_id = None
        self.contract_id = None
        
    def print_step(self, step: str, description: str):
        """단계별 출력"""
        print(f"\n{'='*60}")
        print(f"🚀 {step}: {description}")
        print('='*60)
    
    def print_result(self, success: bool, data: Any, elapsed_time: float = None):
        """결과 출력"""
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{status}")
        if elapsed_time:
            print(f"⏱️ 소요시간: {elapsed_time:.2f}초")
        
        if isinstance(data, dict):
            print(f"📋 응답: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"📋 응답: {data}")
    
    def signup_user(self, email: str, password: str, full_name: str) -> bool:
        """사용자 회원가입"""
        self.print_step("1단계", "사용자 회원가입")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/auth/signup",
                json={
                    "email": email,
                    "password": password,
                    "full_name": full_name
                },
                timeout=30
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.user_id = data.get("user_id")
                    self.print_result(True, data, elapsed_time)
                    return True
                else:
                    self.print_result(False, data, elapsed_time)
                    return False
            else:
                self.print_result(False, f"HTTP {response.status_code}: {response.text}", elapsed_time)
                return False
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.print_result(False, f"예외 발생: {str(e)}", elapsed_time)
            return False
    
    def login_user(self, email: str, password: str) -> bool:
        """사용자 로그인"""
        self.print_step("2단계", "사용자 로그인")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={
                    "email": email,
                    "password": password
                },
                timeout=30
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.access_token = data.get("access_token")
                    self.user_id = data.get("user_info", {}).get("user_id")
                    self.print_result(True, data, elapsed_time)
                    return True
                else:
                    self.print_result(False, data, elapsed_time)
                    return False
            else:
                self.print_result(False, f"HTTP {response.status_code}: {response.text}", elapsed_time)
                return False
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.print_result(False, f"예외 발생: {str(e)}", elapsed_time)
            return False
    
    def upload_contract(self, image_path: str, language: str = "korean") -> bool:
        """계약서 이미지 업로드"""
        self.print_step("3단계", "계약서 이미지 업로드")
        
        if not os.path.exists(image_path):
            self.print_result(False, f"이미지 파일이 존재하지 않습니다: {image_path}")
            return False
        
        start_time = time.time()
        try:
            with open(image_path, 'rb') as f:
                files = {'files': f}
                data = {
                    'user_id': self.user_id,
                    'language': language
                }
                
                response = requests.post(
                    f"{self.base_url}/contract/api/upload",
                    files=files,
                    data=data,
                    timeout=120
                )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.contract_id = result.get("contract_id")
                self.print_result(True, result, elapsed_time)
                return True
            else:
                self.print_result(False, f"HTTP {response.status_code}: {response.text}", elapsed_time)
                return False
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.print_result(False, f"예외 발생: {str(e)}", elapsed_time)
            return False
    
    def analyze_contract_basic(self) -> Optional[Dict[str, Any]]:
        """계약서 기본 분석"""
        self.print_step("4단계", "계약서 기본 분석")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/contract/api/analyze",
                json={
                    "user_id": self.user_id,
                    "contract_id": self.contract_id
                },
                timeout=180
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.print_result(True, data, elapsed_time)
                return data.get("structured_result")
            else:
                self.print_result(False, f"HTTP {response.status_code}: {response.text}", elapsed_time)
                return None
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.print_result(False, f"예외 발생: {str(e)}", elapsed_time)
            return None
    
    def save_corrected_analysis(self, corrected_data: Dict[str, Any], language: str = "korean") -> bool:
        """수정된 계약서 분석 결과 저장"""
        self.print_step("5단계", "수정된 계약서 분석 결과 저장")
        
        start_time = time.time()
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/contract/save-analysis",
                json={
                    "user_id": self.user_id,
                    "contract_id": self.contract_id,
                    "analysis_result": corrected_data,
                    "language": language
                },
                headers=headers,
                timeout=30
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.print_result(True, data, elapsed_time)
                return data.get("success", False)
            else:
                self.print_result(False, f"HTTP {response.status_code}: {response.text}", elapsed_time)
                return False
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.print_result(False, f"예외 발생: {str(e)}", elapsed_time)
            return False
    
    def get_saved_analysis(self) -> Optional[Dict[str, Any]]:
        """저장된 계약서 분석 결과 조회"""
        self.print_step("6단계", "저장된 계약서 분석 결과 조회")
        
        start_time = time.time()
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            response = requests.get(
                f"{self.base_url}/contract/analysis/{self.contract_id}",
                headers=headers,
                timeout=30
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.print_result(True, data, elapsed_time)
                return data.get("analysis_result")
            else:
                self.print_result(False, f"HTTP {response.status_code}: {response.text}", elapsed_time)
                return None
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.print_result(False, f"예외 발생: {str(e)}", elapsed_time)
            return None
    
    def analyze_with_chatbot(self, use_saved_data: bool = True) -> Optional[Dict[str, Any]]:
        """챗봇 통합 분석 (저장된 데이터 사용)"""
        self.print_step("7단계", f"챗봇 통합 분석 (저장된 데이터 사용: {use_saved_data})")
        
        start_time = time.time()
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            # 인증 토큰이 있으면 Authorization 헤더 추가
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            response = requests.post(
                f"{self.base_url}/contract/api/analyze-with-chatbot",
                json={
                    "user_id": self.user_id,
                    "contract_id": self.contract_id,
                    "use_chatbot": True,
                    "user_language": "vietnamese",
                    "use_saved_data": use_saved_data
                },
                headers=headers,
                timeout=300
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.print_result(True, data, elapsed_time)
                return data
            else:
                self.print_result(False, f"HTTP {response.status_code}: {response.text}", elapsed_time)
                return None
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.print_result(False, f"예외 발생: {str(e)}", elapsed_time)
            return None
    
    def get_contract_history(self) -> Optional[Dict[str, Any]]:
        """계약서 히스토리 조회"""
        self.print_step("8단계", "계약서 히스토리 조회")
        
        start_time = time.time()
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            response = requests.get(
                f"{self.base_url}/contract/history",
                headers=headers,
                timeout=30
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.print_result(True, data, elapsed_time)
                return data
            else:
                self.print_result(False, f"HTTP {response.status_code}: {response.text}", elapsed_time)
                return None
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.print_result(False, f"예외 발생: {str(e)}", elapsed_time)
            return None
    
    def run_complete_flow(self, email: str, password: str, full_name: str, image_path: str):
        """완전한 플로우 실행"""
        print("🎯 LawRo 계약서 분석 완전한 플로우 테스트 시작")
        print(f"📧 이메일: {email}")
        print(f"🖼️ 이미지: {image_path}")
        
        total_start_time = time.time()
        
        # 1. 회원가입 (실패해도 계속 진행 - 이미 존재할 수 있음)
        signup_success = self.signup_user(email, password, full_name)
        
        # 2. 로그인
        if not self.login_user(email, password):
            print("❌ 로그인 실패로 테스트 중단")
            return False
        
        # 3. 계약서 업로드
        if not self.upload_contract(image_path):
            print("❌ 계약서 업로드 실패로 테스트 중단")
            return False
        
        # 4. 기본 분석
        basic_analysis = self.analyze_contract_basic()
        
        # 5. OCR 분석 결과를 그대로 저장
        if basic_analysis:
            print("📋 OCR 분석 결과를 사용하여 저장합니다.")
            if not self.save_corrected_analysis(basic_analysis):
                print("⚠️ OCR 분석 결과 저장 실패, 계속 진행")
        else:
            print("⚠️ 기본 분석 결과가 없어 저장을 건너뜁니다.")
        
        # 6. 저장된 데이터 조회
        saved_analysis = self.get_saved_analysis()
        
        # 7. 챗봇 통합 분석 (저장된 데이터 사용)
        chatbot_result = self.analyze_with_chatbot(use_saved_data=True)
        
        # 8. 히스토리 조회
        history = self.get_contract_history()
        
        # 전체 결과 요약
        total_elapsed_time = time.time() - total_start_time
        
        print(f"\n{'='*60}")
        print("🎉 전체 플로우 테스트 완료")
        print('='*60)
        print(f"⏱️ 총 소요시간: {total_elapsed_time:.2f}초")
        print(f"👤 사용자 ID: {self.user_id}")
        print(f"📄 계약서 ID: {self.contract_id}")
        print(f"🔑 토큰 존재: {'✅' if self.access_token else '❌'}")
        
        # 각 단계별 성공 여부
        results = {
            "회원가입": signup_success,
            "로그인": bool(self.access_token),
            "계약서 업로드": bool(self.contract_id),
            "기본 분석": basic_analysis is not None,
            "OCR 결과 저장": saved_analysis is not None,
            "저장 데이터 조회": saved_analysis is not None,
            "챗봇 통합 분석": chatbot_result is not None,
            "히스토리 조회": history is not None
        }
        
        print("\n📊 단계별 결과:")
        for step, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {step}")
        
        success_count = sum(results.values())
        total_count = len(results)
        print(f"\n🎯 성공률: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
        
        return success_count == total_count


def main():
    """메인 함수"""
    # 설정
    BASE_URL = "http://16.176.26.197:8000"
    EMAIL = f"flowtest_{int(time.time())}@example.com"  # 고유한 이메일
    PASSWORD = "testpass123"
    FULL_NAME = "플로우 테스트 사용자"
    IMAGE_PATH = "test/ex6.png"
    
    # 테스터 생성 및 실행
    tester = LawRoAPITester(BASE_URL)
    
    try:
        success = tester.run_complete_flow(EMAIL, PASSWORD, FULL_NAME, IMAGE_PATH)
        
        if success:
            print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
            exit(0)
        else:
            print("\n⚠️ 일부 테스트가 실패했습니다.")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 테스트가 중단되었습니다.")
        exit(1)
    except Exception as e:
        print(f"\n💥 예상치 못한 오류가 발생했습니다: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main() 