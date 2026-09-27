"""
프롬프트 템플릿 계약(contract) 테스트.

계약서 파싱 스키마와 위험도 가중치는 산출물의 데이터 구조를 결정한다.
템플릿을 수정할 때 필드나 배점이 조용히 사라지는 것을 막는다.
"""

import re
from pathlib import Path

import pytest

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"
PARSING = PROMPT_DIR / "contract_parsing_template.txt"
ANALYSIS = PROMPT_DIR / "analysis_request_template.txt"

TOP_LEVEL_GROUPS = [
    "employer",
    "employee",
    "contract_period",
    "workplace",
    "job_details",
    "working_hours",
    "daily_break_minutes",
    "holidays_and_leaves",
    "wages",
    "wage_payment",
    "accommodation_meals",
    "four_major_insurances",
    "contract_and_rules_compliance",
    "other_terms",
    "signature_date",
]

OUTPUT_SECTIONS = [
    "totalScore",
    "aware",
    "summary",
    "highlights",
    "legalInterpretation",
    "deepAnalysis",
]

EXPECTED_WEIGHTS = {
    "최저임금 미달": 3.0,
    "수습기간 중 감액": 2.0,
    "휴일 미기재": 2.0,
    "숙소제공 미기재(외국인)": 2.0,
    "4대보험 미가입": 1.5,
    "임금지급일/지급방식 불명확": 1.0,
    "기타 조항 누락": 0.5,
}


@pytest.fixture(scope="module")
def parsing_text():
    return PARSING.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def analysis_text():
    return ANALYSIS.read_text(encoding="utf-8")


def parse_weights(text: str) -> dict:
    """'각 위반 항목별 가중치는 아래와 같습니다:' 이후의 배점표를 파싱한다."""
    marker = "각 위반 항목별 가중치는 아래와 같습니다:"
    assert marker in text, "가중치 표 머리말이 사라졌다"
    table = text.split(marker, 1)[1]
    return {m.group(1).strip(): float(m.group(2)) for m in re.finditer(r"^-\s*(.+?):\s*([\d.]+)점", table, re.M)}


# --- 계약서 파싱 스키마 -------------------------------------------------


def test_parsing_template_has_all_top_level_groups(parsing_text):
    for group in TOP_LEVEL_GROUPS:
        assert f'"{group}"' in parsing_text, f"최상위 그룹 누락: {group}"


def test_parsing_template_group_count(parsing_text):
    schema = parsing_text[parsing_text.index('{\n  "employer"') :]
    groups = re.findall(r'^  "([a-z_]+)"', schema, re.M)
    assert len(groups) == 15


def test_parsing_template_has_ocr_placeholder(parsing_text):
    assert "{{html_content}}" in parsing_text


def test_parsing_template_declares_missing_value_convention(parsing_text):
    """읽히지 않은 필드는 버리지 않고 '미기재'로 남겨 감점 대상으로 넘긴다."""
    assert "미기재" in parsing_text


# --- 위험도 스코어링 ----------------------------------------------------


def test_weight_table_matches_spec(analysis_text):
    assert parse_weights(analysis_text) == EXPECTED_WEIGHTS


def test_weight_table_total(analysis_text):
    assert sum(parse_weights(analysis_text).values()) == pytest.approx(12.0)


def test_minimum_wage_reference_years(analysis_text):
    for year, wage in (("2023", "9620"), ("2024", "9860"), ("2025", "10030")):
        assert year in analysis_text
        assert wage in analysis_text


def test_monthly_working_hours_basis(analysis_text):
    """월 소정근로시간 209시간 - 월급을 시급으로 환산하는 분모."""
    assert "209" in analysis_text


def test_analysis_output_sections(analysis_text):
    for section in OUTPUT_SECTIONS:
        assert section in analysis_text, f"출력 섹션 누락: {section}"


def test_analysis_template_has_language_placeholder(analysis_text):
    assert "{{language_instruction}}" in analysis_text
