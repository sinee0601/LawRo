"""
Support Center Service
법률 지원 기관 검색 및 관리 서비스
"""

import logging
from math import atan2, cos, radians, sin, sqrt
from typing import List, Optional

from ..database import get_firebase
from ..models.support_center import (
    EmergencyContact,
    SupportCenter,
    SupportCenterQuery,
    SupportCenterResponse,
)

logger = logging.getLogger(__name__)


class SupportCenterService:
    """지원 기관 서비스"""

    def __init__(self):
        self.db = get_firebase().db
        self.collection_name = "support_centers"

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Haversine 공식을 사용한 두 지점 간 거리 계산 (km)
        """
        R = 6371  # 지구 반경 (km)

        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)

        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return round(distance, 2)

    async def search_centers(self, query: SupportCenterQuery) -> SupportCenterResponse:
        """
        지원 기관 검색
        """
        try:
            # Firestore에서 모든 활성화된 지원 기관 가져오기
            centers_ref = self.db.collection(self.collection_name)
            query_ref = centers_ref.where("is_active", "==", True)

            # 기관 유형 필터
            if query.center_type:
                query_ref = query_ref.where("type", "==", query.center_type.value)

            docs = query_ref.limit(query.limit).stream()

            centers = []
            for doc in docs:
                data = doc.to_dict()
                center = SupportCenter(**data)

                # 거리 계산 (사용자 위치가 제공된 경우)
                if query.latitude and query.longitude:
                    distance = self.calculate_distance(
                        query.latitude,
                        query.longitude,
                        center.location.latitude,
                        center.location.longitude
                    )
                    center.distance = distance

                    # 반경 필터
                    if distance > query.radius_km:
                        continue

                centers.append(center)

            # 거리순 정렬 (거리 정보가 있는 경우)
            if query.latitude and query.longitude:
                centers.sort(key=lambda x: x.distance or float('inf'))

            # 긴급 연락처 가져오기
            emergency_contacts = self._get_emergency_contacts()

            return SupportCenterResponse(
                centers=centers,
                total=len(centers),
                emergency_contacts=emergency_contacts
            )

        except Exception as e:
            logger.error(f"지원 기관 검색 오류: {e}")
            raise

    async def get_center_by_id(self, center_id: str) -> Optional[SupportCenter]:
        """
        ID로 지원 기관 조회
        """
        try:
            doc_ref = self.db.collection(self.collection_name).document(center_id)
            doc = doc_ref.get()

            if not doc.exists:
                return None

            data = doc.to_dict()
            return SupportCenter(**data)

        except Exception as e:
            logger.error(f"지원 기관 조회 오류: {e}")
            raise

    async def add_center(self, center: SupportCenter) -> str:
        """
        새 지원 기관 추가 (관리자 기능)
        """
        try:
            doc_ref = self.db.collection(self.collection_name).document(center.id)
            doc_ref.set(center.model_dump(exclude_none=True))
            logger.info(f"지원 기관 추가 완료: {center.id}")
            return center.id

        except Exception as e:
            logger.error(f"지원 기관 추가 오류: {e}")
            raise

    def _get_emergency_contacts(self) -> List[EmergencyContact]:
        """
        긴급 연락처 목록 반환
        """
        return [
            EmergencyContact(
                name="고용노동부 고용센터 상담",
                phone="1350",
                description="근로계약, 임금체불, 부당해고 등 노동 관련 상담",
                available_hours="평일 09:00-18:00",
                languages=["한국어", "영어", "중국어", "베트남어", "태국어"]
            ),
            EmergencyContact(
                name="외국인력상담센터",
                phone="1577-0071",
                description="외국인 노동자 전문 상담 (임금, 산재, 귀국 지원)",
                available_hours="평일 09:00-18:00",
                languages=["한국어", "영어", "중국어", "베트남어", "태국어", "캄보디아어", "인도네시아어"]
            ),
            EmergencyContact(
                name="대한법률구조공단",
                phone="132",
                description="무료 법률 상담 및 소송 지원",
                available_hours="평일 09:00-18:00 (점심시간 12:00-13:00)",
                languages=["한국어", "영어"]
            ),
            EmergencyContact(
                name="근로복지공단 산재보험 콜센터",
                phone="1588-0075",
                description="산재 신청, 요양급여, 보험급여 상담",
                available_hours="평일 09:00-18:00",
                languages=["한국어"]
            ),
            EmergencyContact(
                name="다누리콜센터 (다문화가족지원)",
                phone="1577-1366",
                description="결혼이민자 및 다문화가족 종합 상담",
                available_hours="365일 24시간",
                languages=["한국어", "영어", "중국어", "베트남어", "태국어", "필리핀어", "캄보디아어", "몽골어", "러시아어", "네팔어"]
            ),
            EmergencyContact(
                name="외국인종합안내센터 (HIKOREA)",
                phone="1345",
                description="비자, 체류, 귀화 등 출입국 관련 종합 안내",
                available_hours="평일 09:00-18:00",
                languages=["한국어", "영어", "중국어", "베트남어", "태국어"]
            ),
        ]

    def get_health_status(self) -> dict:
        """
        서비스 상태 확인
        """
        try:
            # Firestore 연결 확인
            self.db.collection(self.collection_name).limit(1).get()
            return {
                "firestore": "healthy",
                "collection": self.collection_name
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "firestore": "unhealthy",
                "error": str(e)
            }
