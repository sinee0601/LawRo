from fastapi import APIRouter, HTTPException
import os

router = APIRouter()

@router.get("/get-analysis-template")
def get_analysis_template():
    """분석 요청 템플릿 반환"""
    try:
        template_path = "prompts/analysis_request_template.txt"
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        else:
            # 기본 템플릿
            template_content = """사용자의 질문은 json 형식으로 된 법률 분석 자료입니다. 양식에 맞게 항목 별로 위반 여부를 분석하고 등급화해 주세요.  
최저임금 정보는 다음과 같습니다 년 : 원
2023: 9620,
2024: 9860,
2025: 10030
당신은 노동법 전문가입니다. 아래는 OCR로 추출된 근로계약서 항목입니다.
이를 바탕으로 "전체 분석 결과(총점 포함)", "하이라이트 항목", "법률 해석" 세 가지 섹션을 반드시 순수 텍스트로 구분하여 출력해 주세요.

{language_instruction}

📍 출처 문서: {context}"""
        
        return {
            "success": True,
            "template": template_content
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"템플릿 로드 실패: {str(e)}") 