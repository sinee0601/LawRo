"""
Contract Service
Handles contract analysis with OCR, GPT parsing, and chatbot integration
"""

import os
import json
import logging
import tempfile
import shutil
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import httpx

from ..config import settings
from ..database import get_firebase, Collections
from ..utils.local_storage import get_local_storage

logger = logging.getLogger(__name__)


class ContractService:
    """Contract analysis service"""

    def __init__(self):
        self.upstage_api_key = settings.UPSTAGE_API_KEY

        # Local storage
        self.storage = get_local_storage()
        logger.info("Using local file storage for contract files")

        # Temporary data storage (in production, use Redis)
        self.temp_storage = {}

        # Firebase
        self.use_firestore = True
        try:
            self.firebase = get_firebase()
            self.db = self.firebase.db
        except Exception as e:
            logger.warning(f"Firestore initialization failed: {e}")
            self.use_firestore = False

    def upload_contract_files(
        self,
        files: List,
        user_id: str,
        language: str = "korean"
    ) -> Tuple[str, List[str], List[str]]:
        """
        Upload contract files to local storage

        Returns:
            (contract_id, uploaded_files, file_urls)
        """
        import uuid

        contract_id = str(uuid.uuid4())
        uploaded_files = []
        file_urls = []

        logger.info(f"Uploading {len(files)} files for contract {contract_id}")

        for file in files:
            try:
                # Upload to local storage
                file_path = self.storage.upload_file(
                    file=file,
                    user_id=user_id,
                    contract_id=contract_id
                )

                uploaded_files.append(file.filename)
                file_url = f"local://{file_path}"
                file_urls.append(file_url)

            except Exception as e:
                logger.error(f"Failed to upload {file.filename}: {e}")
                raise

        # Store temporary data
        self._store_temp_data(contract_id, language)

        logger.info(f"Contract upload complete: {contract_id}")
        return contract_id, uploaded_files, file_urls

    async def analyze_contract_with_chatbot(
        self,
        user_id: str,
        contract_id: str,
        use_chatbot: bool = True,
        user_language: Optional[str] = None,
        use_saved_data: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze contract with OCR, GPT parsing, and optional chatbot analysis

        This is the main workflow for contract analysis
        """
        logger.info(f"Analyzing contract {contract_id} for user {user_id}")

        # Check for saved data in Firestore
        if use_saved_data and self.use_firestore:
            saved_data = self._get_saved_analysis(user_id, contract_id)
            if saved_data:
                logger.info(f"Using saved analysis data for {contract_id}")
                return {
                    "message": "계약서 분석 완료 (저장된 데이터 사용)",
                    "structured_result": saved_data.get("analysis_result", {}),
                    "chatbot_analysis": saved_data.get("chatbot_analysis"),
                    "data_source": "saved_db",
                    "processing_info": {
                        "source": "firestore",
                        "timestamp": saved_data.get("created_at")
                    }
                }

        # Get language from temp storage
        if not user_language:
            temp_data = self._get_temp_data(contract_id)
            user_language = temp_data.get("language", "korean") if temp_data else "korean"

        # Step 1: Get local files
        file_paths = self._list_contract_files(user_id, contract_id)
        if not file_paths:
            raise Exception("계약서 이미지를 찾을 수 없습니다.")

        logger.info(f"Found {len(file_paths)} contract images")

        # Step 2: Process OCR
        ocr_result = self._process_ocr(file_paths)

        # Step 3: Parse with Solar Pro 2
        structured_result = self._parse_with_solar(ocr_result)

        # Step 4: Chatbot analysis (if enabled)
        chatbot_analysis = None
        session_id = None

        if use_chatbot:
            chatbot_analysis, session_id = await self._analyze_with_chatbot(
                structured_result,
                user_language
            )

        # Save to Firestore
        if self.use_firestore:
            self._save_analysis(
                user_id,
                contract_id,
                structured_result,
                chatbot_analysis,
                user_language
            )

        return {
            "message": "계약서 분석 및 법률 상담 완료",
            "structured_result": structured_result,
            "chatbot_analysis": chatbot_analysis,
            "session_id": session_id,
            "data_source": "fresh_ocr",
            "processing_info": {
                "pages_processed": len(file_paths),
                "language": user_language,
                "timestamp": datetime.now().isoformat()
            }
        }

    def _list_contract_files(self, user_id: str, contract_id: str) -> List[str]:
        """List contract files in local storage"""
        return self.storage.list_files(user_id, contract_id)

    def _process_ocr(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Process OCR on contract images
        Simplified version using Upstage API
        """
        logger.info(f"Processing OCR for {len(file_paths)} images")

        # Download files to temp directory
        temp_dir = tempfile.mkdtemp()
        try:
            local_paths = self.storage.download_files(file_paths, temp_dir)

            # Process each image with Upstage OCR
            pages = []
            full_text = ""

            for idx, path in enumerate(local_paths):
                try:
                    # Call Upstage OCR API
                    text = self._call_upstage_ocr(path)
                    pages.append({
                        "page": idx + 1,
                        "text": text,
                        "file_name": os.path.basename(path)
                    })
                    full_text += f"\n\n--- Page {idx + 1} ---\n\n{text}"

                except Exception as e:
                    logger.error(f"OCR failed for page {idx + 1}: {e}")
                    pages.append({
                        "page": idx + 1,
                        "text": "",
                        "error": str(e)
                    })

            return {
                "pages": pages,
                "full_text": full_text,
                "total_pages": len(file_paths)
            }

        finally:
            # Cleanup
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def _call_upstage_ocr(self, image_path: str) -> str:
        """
        Call Upstage Document OCR API
        """
        if not self.upstage_api_key:
            raise Exception("Upstage API key not configured")

        url = "https://api.upstage.ai/v1/document-ai/ocr"

        with open(image_path, "rb") as f:
            files = {"document": f}
            headers = {"Authorization": f"Bearer {self.upstage_api_key}"}

            response = httpx.post(url, files=files, headers=headers, timeout=60.0)

            if response.status_code == 200:
                result = response.json()
                # Extract text from response
                if "content" in result and "text" in result["content"]:
                    return result["content"]["text"]
                elif "text" in result:
                    return result["text"]
                else:
                    return str(result)
            else:
                raise Exception(f"Upstage OCR failed: {response.status_code} - {response.text}")

    def _parse_with_solar(self, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse contract with Upstage Solar Pro 2
        Uses Solar Pro 2 for detailed contract analysis
        """
        logger.info("Parsing contract with Upstage Solar Pro 2")

        full_text = ocr_result.get("full_text", "")

        if not self.upstage_api_key:
            logger.warning("Upstage API key not configured, returning basic structure")
            return self._get_basic_structure(full_text, ocr_result)

        try:
            # Prepare analysis prompt
            analysis_prompt = f"""다음 계약서를 분석하여 JSON 형식으로 답변해주세요.

계약서 내용:
{full_text}

다음 정보를 추출하여 JSON 형식으로 반환하세요:
{{
  "contract_type": "계약서 유형 (예: 근로계약서, 임대차계약서, 매매계약서 등)",
  "parties": {{
    "party_a": "갑 당사자 (이름 또는 회사명)",
    "party_b": "을 당사자 (이름 또는 회사명)"
  }},
  "effective_date": "계약 시작일 (YYYY-MM-DD 형식 또는 '명시되지 않음')",
  "termination_date": "계약 종료일 (YYYY-MM-DD 형식 또는 '명시되지 않음')",
  "key_terms": [
    "주요 계약 조건 1",
    "주요 계약 조건 2",
    "주요 계약 조건 3"
  ],
  "payment_terms": "대금 지급 조건 (있는 경우)",
  "special_conditions": [
    "특약 사항 1",
    "특약 사항 2"
  ],
  "risks": [
    "주의해야 할 법률적 위험 요소 1",
    "주의해야 할 법률적 위험 요소 2"
  ]
}}

계약서에 명시되지 않은 정보는 "명시되지 않음"으로 표시하세요."""

            # Call Upstage Solar Pro 2 API
            url = "https://api.upstage.ai/v1/solar/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.upstage_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "solar-pro",
                "messages": [
                    {
                        "role": "system",
                        "content": "당신은 법률 전문가입니다. 계약서를 분석하여 정확하고 구조화된 정보를 제공합니다."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                "temperature": 0.3,  # 낮은 temperature로 일관성 있는 분석
                "max_tokens": 2000
            }

            response = httpx.post(url, headers=headers, json=payload, timeout=60.0)

            if response.status_code == 200:
                result = response.json()
                assistant_message = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                # Extract JSON from response
                parsed_data = self._extract_json_from_response(assistant_message)

                if parsed_data:
                    # Add extracted text and total pages
                    parsed_data["extracted_text"] = full_text[:1000] + "..." if len(full_text) > 1000 else full_text
                    parsed_data["total_pages"] = ocr_result.get("total_pages", 0)
                    logger.info("Contract successfully parsed with Solar Pro 2")
                    return parsed_data
                else:
                    logger.warning("Failed to extract JSON from Solar response, using basic structure")
                    return self._get_basic_structure(full_text, ocr_result)
            else:
                logger.error(f"Solar API failed: {response.status_code} - {response.text}")
                return self._get_basic_structure(full_text, ocr_result)

        except Exception as e:
            logger.error(f"Error parsing with Solar Pro 2: {e}", exc_info=True)
            return self._get_basic_structure(full_text, ocr_result)

    def _extract_json_from_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from Solar Pro 2 response"""
        try:
            # Try to find JSON in code blocks
            import re

            # Look for JSON in ```json blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Look for JSON in ``` blocks
                json_match = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Try to find JSON object directly
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                    else:
                        return None

            # Parse JSON
            parsed = json.loads(json_str)
            return parsed

        except Exception as e:
            logger.error(f"Failed to extract JSON: {e}")
            return None

    def _get_basic_structure(self, full_text: str, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """Return basic contract structure when AI parsing fails"""
        return {
            "contract_type": "일반 계약서",
            "parties": {
                "party_a": "갑(분석 필요)",
                "party_b": "을(분석 필요)"
            },
            "effective_date": "명시되지 않음",
            "termination_date": "명시되지 않음",
            "key_terms": [
                "계약서 내용을 확인하여 주요 조건을 파악하세요."
            ],
            "payment_terms": "명시되지 않음",
            "special_conditions": [],
            "risks": [
                "계약서 전문을 검토하시기 바랍니다."
            ],
            "extracted_text": full_text[:1000] + "..." if len(full_text) > 1000 else full_text,
            "total_pages": ocr_result.get("total_pages", 0)
        }

    async def _analyze_with_chatbot(
        self,
        structured_result: Dict[str, Any],
        user_language: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Analyze contract with chatbot service using analysis template
        """
        logger.info("Analyzing contract with chatbot")

        try:
            # Import chatbot service
            from .chat_service import ChatService

            chat_service = ChatService()

            # Load analysis template (try multiple paths)
            template_paths = [
                "backend/prompts/analysis_request_template.txt",
                "prompts/analysis_request_template.txt",
                "contract_parser/prompts/analysis_request_template.txt"
            ]

            template_prompt = None
            for template_path in template_paths:
                try:
                    with open(template_path, "r", encoding="utf-8") as f:
                        template_prompt = f.read()
                    logger.info(f"Analysis template loaded from {template_path}")
                    break
                except FileNotFoundError:
                    continue

            if not template_prompt:
                logger.warning("Template not found in any paths, using default prompt")
                template_prompt = self._get_default_prompt()

            # Prepare contract data for analysis
            contract_text = json.dumps(structured_result, ensure_ascii=False, indent=2)

            # Get language instruction
            language_instructions = {
                "korean": "이 분석을 한국어로 작성하십시오.",
                "english": "Provide this analysis in English.",
                "chinese": "请用中文进行此分析。",
                "vietnamese": "Vui lòng cung cấp phân tích này bằng tiếng Việt.",
                "japanese": "この分析を日本語で提供してください。",
                "thai": "โปรดให้การวิเคราะห์นี้เป็นภาษาไทย"
            }
            language_instruction = language_instructions.get(user_language.lower(), language_instructions["korean"])

            # Replace placeholders in template
            custom_prompt = template_prompt.replace(
                "{{language_instruction}}",
                language_instruction
            ).replace(
                "{{context}}",
                f"계약서 분석 데이터:\n{contract_text}\n\n"
            )

            logger.info(f"Prepared custom prompt for chatbot analysis (length: {len(custom_prompt)})")

            # Send to chatbot
            response_text, chat_history, session_id = await chat_service.process_message(
                message="계약서를 법률적으로 분석해주세요.",
                custom_prompt=custom_prompt,
                user_language=user_language
            )

            return {
                "analysis": response_text,
                "session_id": session_id
            }, session_id

        except Exception as e:
            logger.error(f"Chatbot analysis failed: {e}", exc_info=True)
            return None, None

    def _get_default_prompt(self) -> str:
        """
        Default analysis prompt if template file is not found
        """
        return """사용자의 질문은 json 형식으로 된 계약서 자료입니다. 법률적 관점에서 분석해주세요.

당신은 법률 전문가입니다. 아래는 분석된 계약서 항목입니다.
이를 바탕으로 상세한 법률 분석을 제공해주세요.

분석 내용:
- 주요 계약 조건 검토
- 법률적 위험 요소 식별
- 권리와 의무 분석
- 준수해야 할 법률 기준

{{language_instruction}}

출처 문서: {{context}}"""

    def _store_temp_data(self, contract_id: str, language: str):
        """Store temporary data (24 hour retention)"""
        expires_at = datetime.now() + timedelta(hours=24)
        self.temp_storage[contract_id] = {
            "language": language,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat()
        }
        logger.info(f"Temporary data stored: {contract_id}")

    def _get_temp_data(self, contract_id: str) -> Optional[Dict]:
        """Get temporary data"""
        self._clean_expired_data()
        return self.temp_storage.get(contract_id)

    def _clean_expired_data(self):
        """Clean expired temporary data"""
        current_time = datetime.now()
        expired_keys = []

        for key, data in self.temp_storage.items():
            expires_at = datetime.fromisoformat(data.get("expires_at", ""))
            if current_time > expires_at:
                expired_keys.append(key)

        for key in expired_keys:
            del self.temp_storage[key]

    def _get_saved_analysis(self, user_id: str, contract_id: str) -> Optional[Dict]:
        """Get saved analysis from Firestore"""
        if not self.use_firestore:
            return None

        try:
            doc_ref = self.db.collection(Collections.CONTRACT_ANALYSIS).where(
                "user_id", "==", user_id
            ).where(
                "contract_id", "==", contract_id
            ).limit(1).stream()

            for doc in doc_ref:
                return doc.to_dict()

            return None

        except Exception as e:
            logger.error(f"Failed to get saved analysis: {e}")
            return None

    def _save_analysis(
        self,
        user_id: str,
        contract_id: str,
        structured_result: Dict[str, Any],
        chatbot_analysis: Optional[Dict],
        language: str
    ):
        """Save analysis to Firestore"""
        if not self.use_firestore:
            return

        try:
            doc_ref = self.db.collection(Collections.CONTRACT_ANALYSIS).document()

            doc_ref.set({
                "user_id": user_id,
                "contract_id": contract_id,
                "analysis_result": structured_result,
                "chatbot_analysis": chatbot_analysis,
                "language": language,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })

            logger.info(f"Analysis saved to Firestore: {contract_id}")

        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")

    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        storage_healthy = False
        try:
            stats = self.storage.get_storage_stats()
            storage_healthy = "error" not in stats
        except Exception:
            storage_healthy = False

        return {
            "local_storage": "healthy" if storage_healthy else "unavailable",
            "upstage_api": "healthy" if self.upstage_api_key else "not_configured",
            "firestore": "healthy" if self.use_firestore else "unavailable"
        }
