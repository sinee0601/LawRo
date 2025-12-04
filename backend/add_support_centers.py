"""
Quick script to add support center data to Firestore
Firebase Admin SDK 없이 Firestore REST API 사용
"""

import requests
import json

# Firebase 프로젝트 설정
FIREBASE_PROJECT_ID = "lawro-d72cd"  # 실제 프로젝트 ID로 변경하세요
FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"

# 지원 기관 데이터
support_centers = [
    {
        "id": "labor_seoul_01",
        "name": "서울지방고용노동청",
        "type": "labor_office",
        "address": "서울특별시 중구 삼일대로 340",
        "phone": "02-2004-7777",
        "location": {"latitude": 37.5640, "longitude": 126.9962},
        "hours": {"weekday": "09:00-18:00", "lunch": "12:00-13:00", "weekend": "휴무"},
        "services": ["근로계약 상담", "임금체불 신고", "부당해고 구제", "산재 접수"],
        "languages": ["한국어", "영어"],
        "website": "http://www.moel.go.kr/seoul",
        "is_active": True
    },
    {
        "id": "labor_seoul_02",
        "name": "서울동부지청",
        "type": "labor_office",
        "address": "서울특별시 광진구 자양로 167",
        "phone": "02-2204-7777",
        "location": {"latitude": 37.5335, "longitude": 127.0778},
        "hours": {"weekday": "09:00-18:00", "lunch": "12:00-13:00", "weekend": "휴무"},
        "services": ["근로계약 상담", "임금체불 신고", "부당해고 구제"],
        "languages": ["한국어"],
        "is_active": True
    },
    {
        "id": "legal_seoul_01",
        "name": "대한법률구조공단 서울중앙지부",
        "type": "legal_aid",
        "address": "서울특별시 서초구 법원로3길 30",
        "phone": "02-2183-4700",
        "location": {"latitude": 37.4781, "longitude": 127.0022},
        "hours": {"weekday": "09:00-18:00", "lunch": "12:00-13:00", "weekend": "휴무"},
        "services": ["무료 법률 상담", "소송 대리", "법률 문서 작성", "외국인 근로자 지원"],
        "languages": ["한국어", "영어"],
        "website": "https://www.klac.or.kr",
        "is_active": True
    },
    {
        "id": "foreign_seoul_01",
        "name": "서울외국인노동자센터",
        "type": "foreign_support",
        "address": "서울특별시 광진구 천호대로 585",
        "phone": "02-3437-8891",
        "location": {"latitude": 37.5468, "longitude": 127.0844},
        "hours": {"weekday": "10:00-18:00", "lunch": "12:00-13:00", "weekend": "일요일만 휴무"},
        "services": ["통역 지원", "법률 상담", "의료 지원", "긴급 구조", "귀국 지원"],
        "languages": ["한국어", "영어", "중국어", "베트남어", "태국어", "필리핀어", "인도네시아어"],
        "website": "http://www.migrant114.org",
        "is_active": True
    },
    {
        "id": "welfare_seoul_01",
        "name": "근로복지공단 서울업무상질병판정위원회",
        "type": "welfare",
        "address": "서울특별시 마포구 마포대로 135",
        "phone": "1588-0075",
        "location": {"latitude": 37.5442, "longitude": 126.9493},
        "hours": {"weekday": "09:00-18:00", "lunch": "12:00-13:00", "weekend": "휴무"},
        "services": ["산재 신청", "요양급여", "보험급여 상담", "재활 지원"],
        "languages": ["한국어"],
        "website": "https://www.kcomwel.or.kr",
        "is_active": True
    }
]


def convert_to_firestore_format(data):
    """Python dict를 Firestore REST API 형식으로 변환"""

    def convert_value(val):
        if isinstance(val, bool):
            return {"booleanValue": val}
        elif isinstance(val, int):
            return {"integerValue": str(val)}
        elif isinstance(val, float):
            return {"doubleValue": val}
        elif isinstance(val, str):
            return {"stringValue": val}
        elif isinstance(val, list):
            return {"arrayValue": {"values": [convert_value(v) for v in val]}}
        elif isinstance(val, dict):
            return {"mapValue": {"fields": {k: convert_value(v) for k, v in val.items()}}}
        else:
            return {"stringValue": str(val)}

    return {"fields": {k: convert_value(v) for k, v in data.items()}}


print("📍 Firestore에 지원 기관 데이터 추가 중...")
print(f"프로젝트 ID: {FIREBASE_PROJECT_ID}")
print()

for center in support_centers:
    doc_id = center["id"]
    doc_path = f"{FIRESTORE_URL}/support_centers/{doc_id}"

    # Firestore 형식으로 변환
    firestore_data = convert_to_firestore_format(center)

    print(f"추가 중: {center['name']} ({doc_id})")
    print(f"  → {doc_path}")

    # 여기에 실제 API 키가 필요합니다
    # Firebase Console에서 API 키를 가져와서 사용하세요

    # 아래 코드는 주석 처리합니다 (API 키 필요)
    # response = requests.patch(
    #     f"{doc_path}?key=YOUR_API_KEY",
    #     json=firestore_data,
    #     headers={"Content-Type": "application/json"}
    # )

    # if response.status_code == 200:
    #     print(f"  ✅ 성공")
    # else:
    #     print(f"  ❌ 실패: {response.text}")

print()
print("=" * 60)
print("⚠️  이 스크립트는 Firebase REST API 키가 필요합니다.")
print()
print("대신 Firebase Console을 사용하여 수동으로 데이터를 추가하세요:")
print(f"1. https://console.firebase.google.com/project/{FIREBASE_PROJECT_ID}/firestore")
print("2. 'support_centers' 컬렉션 생성")
print("3. 위 데이터를 문서로 추가")
print()
print("또는 Firebase Admin SDK를 설치한 후 init_support_centers.py를 실행하세요:")
print("  pip install firebase-admin")
print("  python -m app.scripts.init_support_centers")
