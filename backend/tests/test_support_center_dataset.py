"""
지원기관 데이터셋 무결성 테스트.

47건 레코드는 4개 출처를 공통 스키마로 정규화한 결과물이다.
적재 전에 스키마·좌표·분류값이 깨지지 않았는지 검증한다.
"""

import json
import re
from pathlib import Path

import pytest

DATA_PATH = Path(__file__).resolve().parent.parent / "scripts" / "support_centers_data.json"

REQUIRED_KEYS = {"id", "name", "type", "address", "phone", "location", "hours", "services", "languages", "is_active"}
ALLOWED_TYPES = {"labor_office", "legal_aid", "foreign_support", "welfare"}

# 대한민국 영토 범위 (제주 ~ 강원, 서해 ~ 독도 제외 본토·제주)
LAT_RANGE = (33.0, 38.7)
LNG_RANGE = (124.5, 132.0)

# 지역번호 형식(02-1234-5678)과 전국대표번호 형식(1588-0075) 두 가지를 허용한다
PHONE_PATTERN = re.compile(r"^(?:0\d{1,2}-\d{3,4}-\d{4}|1[3-9]\d{2}-\d{4})$")


@pytest.fixture(scope="module")
def centers():
    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def test_record_count(centers):
    assert len(centers) == 47


def test_ids_are_unique(centers):
    ids = [c["id"] for c in centers]
    assert len(set(ids)) == len(ids)


def test_every_record_has_required_keys(centers):
    for c in centers:
        missing = REQUIRED_KEYS - c.keys()
        assert not missing, f"{c['id']}: 누락 필드 {missing}"


def test_types_are_within_taxonomy(centers):
    assert {c["type"] for c in centers} == ALLOWED_TYPES


def test_type_distribution(centers):
    counts = {t: sum(1 for c in centers if c["type"] == t) for t in ALLOWED_TYPES}
    assert counts == {"labor_office": 22, "legal_aid": 12, "welfare": 7, "foreign_support": 6}


def test_all_coordinates_present_and_inside_korea(centers):
    for c in centers:
        lat = c["location"]["latitude"]
        lng = c["location"]["longitude"]
        assert LAT_RANGE[0] <= lat <= LAT_RANGE[1], f"{c['id']}: 위도 이상치 {lat}"
        assert LNG_RANGE[0] <= lng <= LNG_RANGE[1], f"{c['id']}: 경도 이상치 {lng}"


def test_phone_numbers_are_normalized(centers):
    for c in centers:
        assert PHONE_PATTERN.match(c["phone"]), f"{c['id']}: 전화번호 형식 이상 {c['phone']}"


def test_representative_number_format_is_expected(centers):
    """전국대표번호(15xx/16xx/18xx)는 지역번호 형식과 자릿수가 다르다."""
    rep = [c for c in centers if c["phone"].startswith(("15", "16", "18"))]
    assert len(rep) == 1


def test_every_center_supports_korean(centers):
    for c in centers:
        assert c["languages"], f"{c['id']}: 지원 언어 없음"
        assert "한국어" in c["languages"], f"{c['id']}: 한국어 미지원"


def test_multilingual_coverage_is_tracked(centers):
    """모국어 상담 가능 기관 비중은 지도 언어 필터의 설계 근거다."""
    multilingual = [c for c in centers if len(c["languages"]) > 1]
    full_support = [c for c in centers if len(c["languages"]) >= 5]
    assert len(multilingual) == 18
    assert len(full_support) == 6


def test_services_are_not_empty(centers):
    for c in centers:
        assert len(c["services"]) >= 4, f"{c['id']}: 서비스 태그 부족"
