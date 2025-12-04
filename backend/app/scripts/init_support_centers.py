"""
Support Center Data Initialization Script
지원 기관 초기 데이터 세팅 (서울/경기 지역 중심)
"""

import sys
import os

# 프로젝트 루트를 Python path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import asyncio
from app.services.support_center_service import SupportCenterService
from app.models.support_center import SupportCenter, CenterType, Location, OperatingHours


# 지원 기관 초기 데이터
SUPPORT_CENTERS_DATA = [
    # 서울 지역 노동청
    {
        "id": "labor_seoul_01",
        "name": "서울지방고용노동청",
        "type": CenterType.LABOR_OFFICE,
        "address": "서울특별시 중구 삼일대로 340",
        "phone": "02-2004-7777",
        "location": Location(latitude=37.5640, longitude=126.9962),
        "hours": OperatingHours(weekday="09:00-18:00", lunch="12:00-13:00", weekend="휴무"),
        "services": ["근로계약 상담", "임금체불 신고", "부당해고 구제", "산재 접수"],
        "languages": ["한국어", "영어"],
        "website": "http://www.moel.go.kr/seoul",
        "is_active": True
    },
    {
        "id": "labor_seoul_02",
        "name": "서울동부지청",
        "type": CenterType.LABOR_OFFICE,
        "address": "서울특별시 광진구 자양로 167",
        "phone": "02-2204-7777",
        "location": Location(latitude=37.5335, longitude=127.0778),
        "hours": OperatingHours(weekday="09:00-18:00", lunch="12:00-13:00", weekend="휴무"),
        "services": ["근로계약 상담", "임금체불 신고", "부당해고 구제"],
        "languages": ["한국어"],
        "is_active": True
    },
    {
        "id": "labor_seoul_03",
        "name": "서울남부지청",
        "type": CenterType.LABOR_OFFICE,
        "address": "서울특별시 영등포구 당산로 41길 11",
        "phone": "02-2670-5800",
        "location": Location(latitude=37.5264, longitude=126.8982),
        "hours": OperatingHours(weekday="09:00-18:00", lunch="12:00-13:00", weekend="휴무"),
        "services": ["근로계약 상담", "임금체불 신고", "부당해고 구제"],
        "languages": ["한국어"],
        "is_active": True
    },

    # 경기 지역 노동청
    {
        "id": "labor_gyeonggi_01",
        "name": "경기지방고용노동청",
        "type": CenterType.LABOR_OFFICE,
        "address": "경기도 의정부시 청사로 1",
        "phone": "031-828-8114",
        "location": Location(latitude=37.7386, longitude=127.0347),
        "hours": OperatingHours(weekday="09:00-18:00", lunch="12:00-13:00", weekend="휴무"),
        "services": ["근로계약 상담", "임금체불 신고", "부당해고 구제", "산재 접수"],
        "languages": ["한국어"],
        "website": "http://www.moel.go.kr/gyeonggi",
        "is_active": True
    },
    {
        "id": "labor_gyeonggi_02",
        "name": "부천지청",
        "type": CenterType.LABOR_OFFICE,
        "address": "경기도 부천시 원미구 송내대로 28",
        "phone": "032-320-1400",
        "location": Location(latitude=37.4867, longitude=126.7832),
        "hours": OperatingHours(weekday="09:00-18:00", lunch="12:00-13:00", weekend="휴무"),
        "services": ["근로계약 상담", "임금체불 신고", "부당해고 구제"],
        "languages": ["한국어"],
        "is_active": True
    },
    {
        "id": "labor_gyeonggi_03",
        "name": "안양지청",
        "type": CenterType.LABOR_OFFICE,
        "address": "경기도 안양시 동안구 관평로 182",
        "phone": "031-380-8500",
        "location": Location(latitude=37.3817, longitude=126.9513),
        "hours": OperatingHours(weekday="09:00-18:00", lunch="12:00-13:00", weekend="휴무"),
        "services": ["근로계약 상담", "임금체불 신고", "부당해고 구제"],
        "languages": ["한국어"],
        "is_active": True
    },

    # 법률구조공단
    {
        "id": "legal_seoul_01",
        "name": "대한법률구조공단 서울중앙지부",
        "type": CenterType.LEGAL_AID,
        "address": "서울특별시 서초구 법원로3길 30",
        "phone": "02-2183-4700",
        "location": Location(latitude=37.4781, longitude=127.0022),
        "hours": OperatingHours(weekday="09:00-18:00", lunch="12:00-13:00", weekend="휴무"),
        "services": ["무료 법률 상담", "소송 대리", "법률 문서 작성", "외국인 근로자 지원"],
        "languages": ["한국어", "영어"],
        "website": "https://www.klac.or.kr",
        "is_active": True
    },
    {
        "id": "legal_incheon_01",
        "name": "대한법률구조공단 인천지부",
        "type": CenterType.LEGAL_AID,
        "address": "인천광역시 남동구 정각로 29",
        "phone": "032-509-2400",
        "location": Location(latitude=37.4489, longitude=126.7315),
        "hours": OperatingHours(weekday="09:00-18:00", lunch="12:00-13:00", weekend="휴무"),
        "services": ["무료 법률 상담", "소송 대리", "법률 문서 작성"],
        "languages": ["한국어"],
        "website": "https://www.klac.or.kr",
        "is_active": True
    },

    # 외국인력지원센터
    {
        "id": "foreign_seoul_01",
        "name": "서울외국인노동자센터",
        "type": CenterType.FOREIGN_SUPPORT,
        "address": "서울특별시 광진구 천호대로 585",
        "phone": "02-3437-8891",
        "location": Location(latitude=37.5468, longitude=127.0844),
        "hours": OperatingHours(weekday="10:00-18:00", lunch="12:00-13:00", weekend="일요일만 휴무"),
        "services": ["통역 지원", "법률 상담", "의료 지원", "긴급 구조", "귀국 지원"],
        "languages": ["한국어", "영어", "중국어", "베트남어", "태국어", "필리핀어", "인도네시아어"],
        "website": "http://www.migrant114.org",
        "is_active": True
    },
    {
        "id": "foreign_gyeonggi_01",
        "name": "경기외국인노동자지원센터",
        "type": CenterType.FOREIGN_SUPPORT,
        "address": "경기도 안산시 단원구 화정로 26",
        "phone": "031-492-9347",
        "location": Location(latitude=37.3217, longitude=126.8308),
        "hours": OperatingHours(weekday="09:00-18:00", lunch="12:00-13:00", weekend="휴무"),
        "services": ["통역 지원", "법률 상담", "의료 지원", "문화 교육", "귀국 지원"],
        "languages": ["한국어", "영어", "중국어", "베트남어", "태국어", "캄보디아어"],
        "website": "http://www.migrantcenter.or.kr",
        "is_active": True
    },
    {
        "id": "foreign_incheon_01",
        "name": "인천외국인노동자지원센터",
        "type": CenterType.FOREIGN_SUPPORT,
        "address": "인천광역시 남동구 논현로 32번길 29",
        "phone": "032-431-9441",
        "location": Location(latitude=37.4327, longitude=126.7013),
        "hours": OperatingHours(weekday="10:00-18:00", lunch="12:00-13:00", weekend="일요일만 휴무"),
        "services": ["통역 지원", "법률 상담", "의료 지원", "긴급 구조"],
        "languages": ["한국어", "영어", "중국어", "베트남어"],
        "is_active": True
    },

    # 근로복지공단
    {
        "id": "welfare_seoul_01",
        "name": "근로복지공단 서울업무상질병판정위원회",
        "type": CenterType.WELFARE,
        "address": "서울특별시 마포구 마포대로 135",
        "phone": "1588-0075",
        "location": Location(latitude=37.5442, longitude=126.9493),
        "hours": OperatingHours(weekday="09:00-18:00", lunch="12:00-13:00", weekend="휴무"),
        "services": ["산재 신청", "요양급여", "보험급여 상담", "재활 지원"],
        "languages": ["한국어"],
        "website": "https://www.kcomwel.or.kr",
        "is_active": True
    },
    {
        "id": "welfare_seoul_02",
        "name": "근로복지공단 서울강남지사",
        "type": CenterType.WELFARE,
        "address": "서울특별시 강남구 테헤란로 125",
        "phone": "02-569-7700",
        "location": Location(latitude=37.5019, longitude=127.0398),
        "hours": OperatingHours(weekday="09:00-18:00", lunch="12:00-13:00", weekend="휴무"),
        "services": ["산재 신청", "요양급여", "보험급여 상담"],
        "languages": ["한국어"],
        "is_active": True
    },
    {
        "id": "welfare_incheon_01",
        "name": "근로복지공단 인천지역본부",
        "type": CenterType.WELFARE,
        "address": "인천광역시 남동구 정각로 9",
        "phone": "032-460-9000",
        "location": Location(latitude=37.4489, longitude=126.7315),
        "hours": OperatingHours(weekday="09:00-18:00", lunch="12:00-13:00", weekend="휴무"),
        "services": ["산재 신청", "요양급여", "보험급여 상담", "재활 지원"],
        "languages": ["한국어"],
        "is_active": True
    }
]


async def init_support_centers():
    """지원 기관 데이터 초기화"""
    print("🚀 지원 기관 데이터 초기화 시작...")

    service = SupportCenterService()

    success_count = 0
    error_count = 0

    for center_data in SUPPORT_CENTERS_DATA:
        try:
            center = SupportCenter(**center_data)
            await service.add_center(center)
            print(f"✅ {center.name} 추가 완료")
            success_count += 1
        except Exception as e:
            print(f"❌ {center_data['name']} 추가 실패: {e}")
            error_count += 1

    print(f"\n✨ 초기화 완료: 성공 {success_count}개, 실패 {error_count}개")


if __name__ == "__main__":
    asyncio.run(init_support_centers())
