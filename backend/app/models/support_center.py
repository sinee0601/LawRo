"""
Support Center Models
법률 지원 기관 관련 Pydantic 모델
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class CenterType(str, Enum):
    """지원 기관 유형"""
    LABOR_OFFICE = "labor_office"  # 노동청
    LEGAL_AID = "legal_aid"  # 법률구조공단
    FOREIGN_SUPPORT = "foreign_support"  # 외국인력지원센터
    WELFARE = "welfare"  # 근로복지공단


class Location(BaseModel):
    """위치 정보"""
    latitude: float = Field(..., description="위도")
    longitude: float = Field(..., description="경도")


class OperatingHours(BaseModel):
    """운영 시간"""
    weekday: str = Field(..., description="평일 운영시간", example="09:00-18:00")
    lunch: Optional[str] = Field(None, description="점심시간", example="12:00-13:00")
    weekend: str = Field(default="휴무", description="주말 운영시간")


class SupportCenter(BaseModel):
    """지원 기관 정보"""
    id: str = Field(..., description="기관 ID")
    name: str = Field(..., description="기관명")
    type: CenterType = Field(..., description="기관 유형")
    address: str = Field(..., description="주소")
    phone: str = Field(..., description="연락처")
    location: Location = Field(..., description="위치 좌표")
    hours: OperatingHours = Field(..., description="운영시간")
    services: List[str] = Field(default_factory=list, description="제공 서비스")
    languages: List[str] = Field(default_factory=list, description="지원 언어")
    website: Optional[str] = Field(None, description="웹사이트 URL")
    is_active: bool = Field(default=True, description="운영 중 여부")
    distance: Optional[float] = Field(None, description="현재 위치로부터 거리 (km)")


class EmergencyContact(BaseModel):
    """긴급 연락처"""
    name: str = Field(..., description="서비스명")
    phone: str = Field(..., description="전화번호")
    description: str = Field(..., description="설명")
    available_hours: str = Field(..., description="이용 가능 시간")
    languages: List[str] = Field(default_factory=list, description="지원 언어")


class SupportCenterQuery(BaseModel):
    """지원 기관 검색 쿼리"""
    latitude: Optional[float] = Field(None, description="현재 위치 위도")
    longitude: Optional[float] = Field(None, description="현재 위치 경도")
    radius_km: float = Field(default=20.0, description="검색 반경 (km)")
    center_type: Optional[CenterType] = Field(None, description="기관 유형 필터")
    limit: int = Field(default=50, description="최대 결과 수")


class SupportCenterResponse(BaseModel):
    """지원 기관 검색 응답"""
    centers: List[SupportCenter] = Field(..., description="지원 기관 목록")
    total: int = Field(..., description="총 개수")
    emergency_contacts: List[EmergencyContact] = Field(..., description="긴급 연락처")
