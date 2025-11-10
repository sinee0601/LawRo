import openai
import json
from pathlib import Path
from config.settings import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def load_prompt_template(name: str) -> str:
    prompt_path = Path(__file__).parent.parent / "prompts" / name
    return prompt_path.read_text(encoding="utf-8")

def call_gpt_api(prompt: str, model="gpt-4", temperature=0.0) -> str:
    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response.choices[0].message.content.strip()

def extract_contract_items_from_summary(json_file_path: str) -> dict:
    """
    OCR 결과 JSON 파일을 받아 표준근로계약서 항목별 JSON 반환.
    프롬프트 템플릿 파일명: "contract_parsing_template.txt"
    """
    try:
        # OCR 결과 파일 읽기
        with open(json_file_path, "r", encoding="utf-8") as f:
            ocr_data = json.load(f)
        
        # 디버깅: OCR 데이터 구조 확인
        print(f"🔍 OCR 데이터 키들: {list(ocr_data.keys())}")
        if "pages" in ocr_data:
            print(f"🔍 페이지 수: {len(ocr_data['pages'])}")
            if ocr_data["pages"]:
                print(f"🔍 첫 번째 페이지 키들: {list(ocr_data['pages'][0].keys())}")
        
        # OCR 텍스트 추출 (여러 페이지의 텍스트 합치기)
        combined_text = ""
        if "pages" in ocr_data:
            for i, page in enumerate(ocr_data["pages"], 1):
                # OCR 결과는 "html" 필드에 저장됨
                page_text = page.get("html", "") or page.get("text", "")
                print(f"🔍 페이지 {i} 텍스트 길이: {len(page_text)} 문자")
                if page_text.strip():
                    combined_text += f"=== 페이지 {i} ===\n{page_text}\n\n"
        elif "full_html" in ocr_data:
            combined_text = ocr_data["full_html"]
            print(f"🔍 full_html 텍스트 길이: {len(combined_text)} 문자")
        elif "text" in ocr_data:
            combined_text = ocr_data["text"]
            print(f"🔍 text 텍스트 길이: {len(combined_text)} 문자")
        elif "full_text" in ocr_data:
            combined_text = ocr_data["full_text"]
            print(f"🔍 full_text 텍스트 길이: {len(combined_text)} 문자")
        else:
            # 다른 형식의 OCR 결과 처리
            combined_text = str(ocr_data)
            print(f"🔍 전체 데이터를 문자열로 변환: {len(combined_text)} 문자")
        
        print(f"🔍 최종 combined_text 길이: {len(combined_text)} 문자")
        if combined_text.strip():
            print(f"🔍 combined_text 미리보기: {combined_text[:200]}...")
        
        if not combined_text.strip():
            return {"raw_text": "OCR 텍스트를 찾을 수 없습니다."}
        
        # GPT 프롬프트 생성
        prompt_template = load_prompt_template("contract_parsing_template.txt")
        prompt = prompt_template.replace("{{html_content}}", combined_text)
        
        # GPT API 호출
        content = call_gpt_api(prompt)
        
        # JSON 파싱 시도
        try:
            # JSON 블록 추출 (```json ... ``` 형태인 경우)
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                if end != -1:
                    json_content = content[start:end].strip()
                else:
                    json_content = content[start:].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                if end != -1:
                    json_content = content[start:end].strip()
                else:
                    json_content = content[start:].strip()
            else:
                json_content = content.strip()
            
            return json.loads(json_content)
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 실패: {e}")
            print(f"GPT 응답: {content[:500]}...")
            # JSON 파싱 실패 시 raw_text 필드에 내용 전달
            return {"raw_text": content}
            
    except Exception as e:
        print(f"파일 처리 중 오류: {e}")
        return {"raw_text": f"파일 처리 중 오류가 발생했습니다: {str(e)}"}
