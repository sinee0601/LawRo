#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
개선된 LawRo 워크플로우 테스트
- 새로운 통합 워크플로우 테스트
- 에러 처리 및 로깅 개선 확인
- ChatBot 상태 확인
- 성능 비교
"""

import requests
import json
import time
import os
from typing import Dict, Any, Optional

class ImprovedWorkflowTester:
    def __init__(self, base_url: str = "http://16.176.26.197:8000"):
        self.base_url = base_url
        self.results = {}
        
    def print_step(self, step: str, description: str):
        """단계별 출력"""
        print(f"\n{'='*70}")
        print(f"🚀 {step}: {description}")
        print('='*70)
    
    def print_result(self, success: bool, data: Any, elapsed_time: float = None):
        """결과 출력"""
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{status}")
        if elapsed_time:
            print(f"⏱️ 소요시간: {elapsed_time:.2f}초")
        
        # 결과를 간결하게 출력
        if isinstance(data, dict):
            if "message" in data:
                print(f"📋 메시지: {data['message']}")
            if "error" in data:
                print(f"⚠️ 오류: {data['error']}")
            if "processing_info" in data:
                info = data["processing_info"]
                print(f"📊 처리 정보: 총 {info.get('total_time', 0):.1f}초, OCR {info.get('ocr_time', 0):.1f}초, 이미지 {info.get('image_count', 0)}개")
        else:
            print(f"📋 응답: {str(data)[:200]}...")
    
    def test_chatbot_status(self) -> bool:
        """ChatBot 서버 상태 확인"""
        self.print_step("Step 1", "ChatBot 서버 상태 확인")
        
        start_time = time.time()
        try:
            response = requests.get(
                f"{self.base_url}/contract/api/chatbot-status",
                timeout=30
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                available = data.get("chatbot_available", False)
                self.results["chatbot_status"] = {
                    "success": True,
                    "available": available,
                    "elapsed_time": elapsed_time
                }
                self.print_result(True, data, elapsed_time)
                return available
            else:
                self.print_result(False, f"HTTP {response.status_code}: {response.text}", elapsed_time)
                return False
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.print_result(False, f"예외 발생: {str(e)}", elapsed_time)
            return False
    
    def test_integrated_workflow(self, image_path: str, user_id: str = "test_user_workflow") -> Optional[Dict]:
        """통합 워크플로우 테스트 (파일과 함께)"""
        self.print_step("Step 2", "통합 워크플로우 테스트 (analyze-with-chatbot)")
        
        if not os.path.exists(image_path):
            self.print_result(False, f"이미지 파일이 존재하지 않습니다: {image_path}")
            return None
        
        start_time = time.time()
        try:
            with open(image_path, 'rb') as f:
                files = {'files': f}
                data = {
                    'user_id': user_id,
                    'language': 'korean',
                    'contract_id': f'test_contract_{int(time.time())}'
                }
                
                response = requests.post(
                    f"{self.base_url}/contract/api/analyze-with-chatbot",
                    files=files,
                    data=data,
                    timeout=180
                )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.results["integrated_workflow"] = {
                    "success": True,
                    "contract_id": result.get("processing_info", {}).get("contract_id"),
                    "elapsed_time": elapsed_time,
                    "data_source": result.get("data_source"),
                    "has_chatbot_analysis": "chatbot_analysis" in result
                }
                self.print_result(True, result, elapsed_time)
                return result
            else:
                error_data = {"status_code": response.status_code, "response": response.text}
                self.results["integrated_workflow"] = {
                    "success": False,
                    "elapsed_time": elapsed_time,
                    "error": error_data
                }
                self.print_result(False, error_data, elapsed_time)
                return None
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.results["integrated_workflow"] = {
                "success": False,
                "elapsed_time": elapsed_time,
                "error": str(e)
            }
            self.print_result(False, f"예외 발생: {str(e)}", elapsed_time)
            return None
    
    def test_basic_workflow(self, contract_id: str, user_id: str = "test_user_workflow") -> Optional[Dict]:
        """기본 워크플로우 테스트 (ChatBot 없이)"""
        self.print_step("Step 3", "기본 워크플로우 테스트 (analyze only)")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/contract/api/analyze",
                json={
                    "user_id": user_id,
                    "contract_id": contract_id
                },
                timeout=120
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.results["basic_workflow"] = {
                    "success": True,
                    "elapsed_time": elapsed_time,
                    "has_structured_result": "structured_result" in result
                }
                self.print_result(True, result, elapsed_time)
                return result
            else:
                error_data = {"status_code": response.status_code, "response": response.text}
                self.results["basic_workflow"] = {
                    "success": False,
                    "elapsed_time": elapsed_time,
                    "error": error_data
                }
                self.print_result(False, error_data, elapsed_time)
                return None
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.results["basic_workflow"] = {
                "success": False,
                "elapsed_time": elapsed_time,
                "error": str(e)
            }
            self.print_result(False, f"예외 발생: {str(e)}", elapsed_time)
            return None
    
    def test_upload_only(self, image_path: str, user_id: str = "test_user_workflow") -> Optional[str]:
        """업로드만 테스트"""
        self.print_step("Step 4", "업로드 전용 테스트")
        
        if not os.path.exists(image_path):
            self.print_result(False, f"이미지 파일이 존재하지 않습니다: {image_path}")
            return None
        
        start_time = time.time()
        try:
            with open(image_path, 'rb') as f:
                files = {'files': f}
                data = {
                    'user_id': user_id,
                    'language': 'korean'
                }
                
                response = requests.post(
                    f"{self.base_url}/contract/api/upload",
                    files=files,
                    data=data,
                    timeout=60
                )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                contract_id = result.get("contract_id")
                self.results["upload_only"] = {
                    "success": True,
                    "contract_id": contract_id,
                    "elapsed_time": elapsed_time,
                    "file_count": result.get("file_count", 0)
                }
                self.print_result(True, result, elapsed_time)
                return contract_id
            else:
                error_data = {"status_code": response.status_code, "response": response.text}
                self.results["upload_only"] = {
                    "success": False,
                    "elapsed_time": elapsed_time,
                    "error": error_data
                }
                self.print_result(False, error_data, elapsed_time)
                return None
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.results["upload_only"] = {
                "success": False,
                "elapsed_time": elapsed_time,
                "error": str(e)
            }
            self.print_result(False, f"예외 발생: {str(e)}", elapsed_time)
            return None
    
    def test_error_handling(self) -> bool:
        """에러 처리 테스트"""
        self.print_step("Step 5", "에러 처리 및 로깅 개선 테스트")
        
        # 존재하지 않는 contract_id로 테스트
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/contract/api/analyze",
                json={
                    "user_id": "test_user",
                    "contract_id": "nonexistent_contract_12345"
                },
                timeout=30
            )
            elapsed_time = time.time() - start_time
            
            # 오류 응답이 개선된 형태로 오는지 확인
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    # 새로운 오류 형식 확인
                    has_improved_format = (
                        isinstance(error_data.get("detail"), dict) and
                        "message" in error_data["detail"] and
                        "error_type" in error_data["detail"]
                    )
                    
                    self.results["error_handling"] = {
                        "success": True,
                        "has_improved_format": has_improved_format,
                        "elapsed_time": elapsed_time,
                        "error_structure": error_data.get("detail", {})
                    }
                    self.print_result(has_improved_format, error_data, elapsed_time)
                    return has_improved_format
                except:
                    # JSON이 아닌 응답
                    self.results["error_handling"] = {
                        "success": False,
                        "has_improved_format": False,
                        "elapsed_time": elapsed_time,
                        "raw_response": response.text
                    }
                    self.print_result(False, f"비-JSON 응답: {response.text[:100]}...", elapsed_time)
                    return False
            else:
                self.print_result(False, "예상되지 않은 성공 응답", elapsed_time)
                return False
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.results["error_handling"] = {
                "success": False,
                "elapsed_time": elapsed_time,
                "error": str(e)
            }
            self.print_result(False, f"예외 발생: {str(e)}", elapsed_time)
            return False
    
    def run_all_tests(self, image_path: str):
        """모든 테스트 실행"""
        print("🎯 개선된 LawRo 워크플로우 테스트 시작")
        print(f"🖼️ 테스트 이미지: {image_path}")
        
        total_start_time = time.time()
        
        # 1. ChatBot 상태 확인
        chatbot_available = self.test_chatbot_status()
        
        # 2. 통합 워크플로우 테스트
        integrated_result = self.test_integrated_workflow(image_path)
        
        # 3. 업로드 전용 테스트
        uploaded_contract_id = self.test_upload_only(image_path)
        
        # 4. 기본 워크플로우 테스트 (업로드된 contract_id 사용)
        if uploaded_contract_id:
            basic_result = self.test_basic_workflow(uploaded_contract_id)
        else:
            print("⚠️ 업로드 실패로 기본 워크플로우 테스트를 건너뜁니다.")
            self.results["basic_workflow"] = {"success": False, "skipped": True}
        
        # 5. 에러 처리 테스트
        error_handling_improved = self.test_error_handling()
        
        # 전체 결과 요약
        total_elapsed_time = time.time() - total_start_time
        
        self.print_final_summary(total_elapsed_time)
        
        # 전체 성공 여부 판단
        critical_tests = ["integrated_workflow", "error_handling"]
        success = all(self.results.get(test, {}).get("success", False) for test in critical_tests)
        
        return success
    
    def print_final_summary(self, total_time: float):
        """최종 요약 출력"""
        print(f"\n{'='*70}")
        print("🎉 개선된 워크플로우 테스트 완료")
        print('='*70)
        print(f"⏱️ 총 소요시간: {total_time:.2f}초")
        
        print("\n📊 테스트 결과 요약:")
        test_names = {
            "chatbot_status": "ChatBot 상태 확인",
            "integrated_workflow": "통합 워크플로우",
            "upload_only": "업로드 전용",
            "basic_workflow": "기본 워크플로우",
            "error_handling": "에러 처리 개선"
        }
        
        success_count = 0
        for test_key, test_name in test_names.items():
            result = self.results.get(test_key, {})
            if result.get("skipped"):
                print(f"  ⏭️ {test_name}: 건너뜀")
            elif result.get("success"):
                print(f"  ✅ {test_name}: 성공 ({result.get('elapsed_time', 0):.1f}초)")
                success_count += 1
            else:
                print(f"  ❌ {test_name}: 실패")
        
        print(f"\n🎯 성공률: {success_count}/{len(test_names)} ({success_count/len(test_names)*100:.1f}%)")
        
        # 성능 비교
        print("\n⚡ 성능 비교:")
        integrated_time = self.results.get("integrated_workflow", {}).get("elapsed_time", 0)
        upload_time = self.results.get("upload_only", {}).get("elapsed_time", 0)
        basic_time = self.results.get("basic_workflow", {}).get("elapsed_time", 0)
        total_separate_time = upload_time + basic_time
        
        if integrated_time > 0 and total_separate_time > 0:
            efficiency = ((total_separate_time - integrated_time) / total_separate_time * 100)
            print(f"  • 통합 워크플로우: {integrated_time:.1f}초")
            print(f"  • 분리 워크플로우: {total_separate_time:.1f}초 (업로드 {upload_time:.1f}초 + 분석 {basic_time:.1f}초)")
            print(f"  • 효율성 개선: {efficiency:+.1f}%")
        
        # 개선사항 확인
        print("\n🔧 개선사항 확인:")
        
        # ChatBot 상태
        chatbot_status = self.results.get("chatbot_status", {})
        if chatbot_status.get("available"):
            print("  ✅ ChatBot 서비스 정상 작동")
        else:
            print("  ⚠️ ChatBot 서비스 연결 불안정")
        
        # 에러 처리 개선
        error_result = self.results.get("error_handling", {})
        if error_result.get("has_improved_format"):
            print("  ✅ 개선된 에러 응답 형식 적용")
        else:
            print("  ❌ 에러 응답 형식 개선 미적용")
        
        # 통합 워크플로우
        integrated_result = self.results.get("integrated_workflow", {})
        if integrated_result.get("success"):
            print(f"  ✅ 통합 워크플로우 정상 작동 (데이터 소스: {integrated_result.get('data_source', 'unknown')})")
            if integrated_result.get("has_chatbot_analysis"):
                print("  ✅ ChatBot 분석 통합 완료")
        else:
            print("  ❌ 통합 워크플로우 실패")


def main():
    """메인 함수"""
    # 설정
    BASE_URL = "http://16.176.26.197:8000"
    IMAGE_PATH = "test/ex6.png"
    
    # 이미지 파일 존재 확인
    if not os.path.exists(IMAGE_PATH):
        print(f"❌ 테스트 이미지 파일이 존재하지 않습니다: {IMAGE_PATH}")
        print("💡 test/ex6.png 파일을 준비해 주세요.")
        exit(1)
    
    # 테스터 생성 및 실행
    tester = ImprovedWorkflowTester(BASE_URL)
    
    try:
        success = tester.run_all_tests(IMAGE_PATH)
        
        if success:
            print("\n🎉 모든 핵심 테스트가 성공적으로 완료되었습니다!")
            exit(0)
        else:
            print("\n⚠️ 일부 핵심 테스트가 실패했습니다.")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 테스트가 중단되었습니다.")
        exit(1)
    except Exception as e:
        print(f"\n💥 예상치 못한 오류가 발생했습니다: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()