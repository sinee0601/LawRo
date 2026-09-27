"""
한국 전국 지원 기관 데이터 수집 스크립트
웹 스크래핑 + 수동 데이터 결합
"""

import json

# =============================================================================
# 1. 고용노동부 지방관서 (노동청)
# =============================================================================
LABOR_OFFICES = [
    # 서울/경기
    {"name": "서울지방고용노동청", "address": "서울특별시 중구 삼일대로 340", "phone": "02-2004-7777", "lat": 37.5640, "lng": 126.9962},
    {"name": "서울동부지청", "address": "서울특별시 광진구 자양로 167", "phone": "02-2204-7777", "lat": 37.5335, "lng": 127.0778},
    {"name": "서울남부지청", "address": "서울특별시 영등포구 당산로 41길 11", "phone": "02-2670-5800", "lat": 37.5264, "lng": 126.8982},
    {"name": "서울북부지청", "address": "서울특별시 노원구 노해로 437", "phone": "02-950-7400", "lat": 37.6545, "lng": 127.0617},
    {"name": "경기지방고용노동청", "address": "경기도 의정부시 청사로 1", "phone": "031-828-8114", "lat": 37.7386, "lng": 127.0347},
    {"name": "부천지청", "address": "경기도 부천시 원미구 송내대로 28", "phone": "032-320-1400", "lat": 37.4867, "lng": 126.7832},
    {"name": "안양지청", "address": "경기도 안양시 동안구 관평로 182", "phone": "031-380-8500", "lat": 37.3817, "lng": 126.9513},
    {"name": "성남지청", "address": "경기도 성남시 중원구 사기막골로 124", "phone": "031-735-8200", "lat": 37.4206, "lng": 127.1401},

    # 부산/경남
    {"name": "부산지방고용노동청", "address": "부산광역시 부산진구 중앙대로 1017", "phone": "051-860-1000", "lat": 35.1635, "lng": 129.0586},
    {"name": "부산동부지청", "address": "부산광역시 해운대구 재반로 143", "phone": "051-760-7500", "lat": 35.1783, "lng": 129.1758},
    {"name": "경남지방고용노동청", "address": "경상남도 창원시 의창구 중앙대로 291", "phone": "055-213-4301", "lat": 35.2403, "lng": 128.6789},

    # 대구/경북
    {"name": "대구지방고용노동청", "address": "대구광역시 북구 연암로 140", "phone": "053-350-3000", "lat": 35.8960, "lng": 128.6177},
    {"name": "경북지방고용노동청", "address": "경상북도 포항시 남구 상도로 120", "phone": "054-270-8114", "lat": 36.0087, "lng": 129.3678},

    # 인천
    {"name": "인천지방고용노동청", "address": "인천광역시 남동구 정각로 29", "phone": "032-470-6114", "lat": 37.4489, "lng": 126.7315},

    # 광주/전남
    {"name": "광주지방고용노동청", "address": "광주광역시 동구 금남로 245", "phone": "062-230-1114", "lat": 35.1457, "lng": 126.9227},
    {"name": "전남지방고용노동청", "address": "전라남도 무안군 삼향읍 후광대로 242", "phone": "061-280-5000", "lat": 34.8167, "lng": 126.4628},

    # 대전/충청
    {"name": "대전지방고용노동청", "address": "대전광역시 서구 둔산로 212", "phone": "042-480-4114", "lat": 36.3504, "lng": 127.3845},
    {"name": "충북지방고용노동청", "address": "충청북도 청주시 흥덕구 강내로 254", "phone": "043-240-3114", "lat": 36.6318, "lng": 127.4574},
    {"name": "충남지방고용노동청", "address": "충청남도 천안시 서북구 불당21로 272", "phone": "041-560-1400", "lat": 36.8077, "lng": 127.1538},

    # 전북
    {"name": "전북지방고용노동청", "address": "전북특별자치도 전주시 덕진구 백제대로 708", "phone": "063-230-1500", "lat": 35.8490, "lng": 127.1291},

    # 강원
    {"name": "강원지방고용노동청", "address": "강원특별자치도 춘천시 중앙로 7", "phone": "033-260-3114", "lat": 37.8813, "lng": 127.7298},

    # 제주
    {"name": "제주지방고용노동청", "address": "제주특별자치도 제주시 연삼로 473", "phone": "064-724-8114", "lat": 33.4996, "lng": 126.5312},
]


# =============================================================================
# 2. 법률구조공단 지부
# =============================================================================
LEGAL_AID_OFFICES = [
    {"name": "서울중앙지부", "address": "서울특별시 서초구 법원로3길 30", "phone": "02-2183-4700", "lat": 37.4781, "lng": 127.0022},
    {"name": "인천지부", "address": "인천광역시 남동구 정각로 29", "phone": "032-509-2400", "lat": 37.4489, "lng": 126.7315},
    {"name": "수원지부", "address": "경기도 수원시 영통구 광교중앙로 140", "phone": "031-219-2500", "lat": 37.2840, "lng": 127.0440},
    {"name": "부산지부", "address": "부산광역시 연제구 중앙대로 1000", "phone": "051-507-0500", "lat": 35.1916, "lng": 129.0787},
    {"name": "대구지부", "address": "대구광역시 수성구 동대구로 390", "phone": "053-755-9915", "lat": 35.8714, "lng": 128.6014},
    {"name": "광주지부", "address": "광주광역시 동구 서석로 33", "phone": "062-232-3436", "lat": 35.1509, "lng": 126.9169},
    {"name": "대전지부", "address": "대전광역시 서구 둔산로 121", "phone": "042-480-6500", "lat": 36.3504, "lng": 127.3845},
    {"name": "울산지부", "address": "울산광역시 남구 삼산로 249", "phone": "052-260-2525", "lat": 35.5384, "lng": 129.3114},
    {"name": "춘천지부", "address": "강원특별자치도 춘천시 중앙로 64", "phone": "033-254-1414", "lat": 37.8813, "lng": 127.7298},
    {"name": "청주지부", "address": "충청북도 청주시 상당구 상당로 69", "phone": "043-257-9911", "lat": 36.6357, "lng": 127.4913},
    {"name": "전주지부", "address": "전북특별자치도 전주시 완산구 기린대로 250", "phone": "063-230-2200", "lat": 35.8242, "lng": 127.1480},
    {"name": "제주지부", "address": "제주특별자치도 제주시 문연로 26", "phone": "064-720-4700", "lat": 33.5097, "lng": 126.5219},
]


# =============================================================================
# 3. 외국인력지원센터
# =============================================================================
FOREIGN_SUPPORT_CENTERS = [
    {"name": "서울외국인노동자센터", "address": "서울특별시 광진구 천호대로 585", "phone": "02-3437-8891", "lat": 37.5468, "lng": 127.0844},
    {"name": "경기외국인노동자지원센터", "address": "경기도 안산시 단원구 화정로 26", "phone": "031-492-9347", "lat": 37.3217, "lng": 126.8308},
    {"name": "인천외국인노동자지원센터", "address": "인천광역시 남동구 논현로 32번길 29", "phone": "032-431-9441", "lat": 37.4327, "lng": 126.7013},
    {"name": "부산외국인노동자지원센터", "address": "부산광역시 사상구 학장로 260", "phone": "051-317-9177", "lat": 35.1494, "lng": 128.9910},
    {"name": "대구외국인노동자지원센터", "address": "대구광역시 북구 산격동 1475", "phone": "053-959-9977", "lat": 35.8959, "lng": 128.6176},
    {"name": "광주외국인노동자지원센터", "address": "광주광역시 북구 중흥동 684-1", "phone": "062-266-0035", "lat": 35.1726, "lng": 126.9119},
]


# =============================================================================
# 4. 근로복지공단 지역본부
# =============================================================================
WELFARE_OFFICES = [
    {"name": "서울업무상질병판정위원회", "address": "서울특별시 마포구 마포대로 135", "phone": "1588-0075", "lat": 37.5442, "lng": 126.9493},
    {"name": "서울강남지사", "address": "서울특별시 강남구 테헤란로 125", "phone": "02-569-7700", "lat": 37.5019, "lng": 127.0398},
    {"name": "인천지역본부", "address": "인천광역시 남동구 정각로 9", "phone": "032-460-9000", "lat": 37.4489, "lng": 126.7315},
    {"name": "부산지역본부", "address": "부산광역시 연제구 중앙대로 1001", "phone": "051-520-0400", "lat": 35.1916, "lng": 129.0787},
    {"name": "대구지역본부", "address": "대구광역시 북구 연암로 140", "phone": "053-350-0300", "lat": 35.8960, "lng": 128.6177},
    {"name": "광주지역본부", "address": "광주광역시 서구 상무중앙로 38", "phone": "062-360-6000", "lat": 35.1522, "lng": 126.8805},
    {"name": "대전지역본부", "address": "대전광역시 서구 둔산로 123", "phone": "042-480-7700", "lat": 36.3504, "lng": 127.3845},
]


# =============================================================================
# 데이터 통합 및 Firestore 형식 변환
# =============================================================================
def generate_support_centers():
    """모든 지원 기관 데이터를 생성"""

    all_centers = []

    # 노동청
    for idx, office in enumerate(LABOR_OFFICES, 1):
        all_centers.append({
            "id": f"labor_{idx:03d}",
            "name": office["name"],
            "type": "labor_office",
            "address": office["address"],
            "phone": office["phone"],
            "location": {"latitude": office["lat"], "longitude": office["lng"]},
            "hours": {"weekday": "09:00-18:00", "lunch": "12:00-13:00", "weekend": "휴무"},
            "services": ["근로계약 상담", "임금체불 신고", "부당해고 구제", "산재 접수"],
            "languages": ["한국어"],
            "is_active": True
        })

    # 법률구조공단
    for idx, office in enumerate(LEGAL_AID_OFFICES, 1):
        all_centers.append({
            "id": f"legal_{idx:03d}",
            "name": f"대한법률구조공단 {office['name']}",
            "type": "legal_aid",
            "address": office["address"],
            "phone": office["phone"],
            "location": {"latitude": office["lat"], "longitude": office["lng"]},
            "hours": {"weekday": "09:00-18:00", "lunch": "12:00-13:00", "weekend": "휴무"},
            "services": ["무료 법률 상담", "소송 대리", "법률 문서 작성", "외국인 근로자 지원"],
            "languages": ["한국어", "영어"],
            "website": "https://www.klac.or.kr",
            "is_active": True
        })

    # 외국인력지원센터
    for idx, center in enumerate(FOREIGN_SUPPORT_CENTERS, 1):
        all_centers.append({
            "id": f"foreign_{idx:03d}",
            "name": center["name"],
            "type": "foreign_support",
            "address": center["address"],
            "phone": center["phone"],
            "location": {"latitude": center["lat"], "longitude": center["lng"]},
            "hours": {"weekday": "09:00-18:00", "lunch": "12:00-13:00", "weekend": "일요일만 휴무"},
            "services": ["통역 지원", "법률 상담", "의료 지원", "긴급 구조", "귀국 지원"],
            "languages": ["한국어", "영어", "중국어", "베트남어", "태국어"],
            "is_active": True
        })

    # 근로복지공단
    for idx, office in enumerate(WELFARE_OFFICES, 1):
        all_centers.append({
            "id": f"welfare_{idx:03d}",
            "name": f"근로복지공단 {office['name']}",
            "type": "welfare",
            "address": office["address"],
            "phone": office["phone"],
            "location": {"latitude": office["lat"], "longitude": office["lng"]},
            "hours": {"weekday": "09:00-18:00", "lunch": "12:00-13:00", "weekend": "휴무"},
            "services": ["산재 신청", "요양급여", "보험급여 상담", "재활 지원"],
            "languages": ["한국어"],
            "website": "https://www.kcomwel.or.kr",
            "is_active": True
        })

    return all_centers


# =============================================================================
# JSON 파일로 저장
# =============================================================================
if __name__ == "__main__":
    centers = generate_support_centers()

    # JSON 파일로 저장
    with open("support_centers_data.json", "w", encoding="utf-8") as f:
        json.dump(centers, f, ensure_ascii=False, indent=2)

    print(f"✅ 총 {len(centers)}개 지원 기관 데이터 생성 완료!")
    print(f"   - 노동청: {len(LABOR_OFFICES)}개")
    print(f"   - 법률구조공단: {len(LEGAL_AID_OFFICES)}개")
    print(f"   - 외국인력지원센터: {len(FOREIGN_SUPPORT_CENTERS)}개")
    print(f"   - 근로복지공단: {len(WELFARE_OFFICES)}개")
    print()
    print("📁 저장 위치: support_centers_data.json")
    print()
    print("다음 단계:")
    print("1. 이 JSON 파일을 확인하여 데이터 검토")
    print("2. init_support_centers.py 스크립트를 수정하여 이 데이터 사용")
    print("3. python -m app.scripts.init_support_centers 실행")
