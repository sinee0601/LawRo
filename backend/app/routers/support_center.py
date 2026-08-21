"""
Support Center Router
법률 지원 기관 API 엔드포인트
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from ..models.support_center import CenterType, SupportCenter, SupportCenterQuery, SupportCenterResponse
from ..services.support_center_service import SupportCenterService

router = APIRouter()

# Service instance
_support_center_service: Optional[SupportCenterService] = None


def get_support_center_service() -> SupportCenterService:
    """Get or create SupportCenterService singleton"""
    global _support_center_service
    if _support_center_service is None:
        _support_center_service = SupportCenterService()
    return _support_center_service


@router.post("/api/search", response_model=SupportCenterResponse)
async def search_support_centers(query: SupportCenterQuery):
    """
    지원 기관 검색

    - **latitude**: 현재 위치 위도 (선택)
    - **longitude**: 현재 위치 경도 (선택)
    - **radius_km**: 검색 반경 (기본 20km)
    - **center_type**: 기관 유형 필터 (선택)
    - **limit**: 최대 결과 수 (기본 50)
    """
    try:
        service = get_support_center_service()
        result = await service.search_centers(query)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"지원 기관 검색 오류: {str(e)}"
        )


@router.get("/api/centers/{center_id}", response_model=SupportCenter)
async def get_center(center_id: str):
    """
    특정 지원 기관 상세 조회

    - **center_id**: 지원 기관 ID
    """
    try:
        service = get_support_center_service()
        center = await service.get_center_by_id(center_id)

        if not center:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="지원 기관을 찾을 수 없습니다"
            )

        return center
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"지원 기관 조회 오류: {str(e)}"
        )


@router.get("/api/nearby")
async def get_nearby_centers(
    latitude: float = Query(..., description="현재 위치 위도"),
    longitude: float = Query(..., description="현재 위치 경도"),
    radius_km: float = Query(default=20.0, description="검색 반경 (km)"),
    center_type: Optional[CenterType] = Query(None, description="기관 유형 필터")
):
    """
    현재 위치 기준 가까운 지원 기관 검색

    - **latitude**: 현재 위치 위도 (필수)
    - **longitude**: 현재 위치 경도 (필수)
    - **radius_km**: 검색 반경 (기본 20km)
    - **center_type**: 기관 유형 필터 (선택)
    """
    query = SupportCenterQuery(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        center_type=center_type
    )

    service = None
    try:
        service = get_support_center_service()
        result = await service.search_centers(query)
        return result
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"❌ 지원 기관 검색 오류: {str(e)}")
        logger.error(traceback.format_exc())

        # 에러 발생 시 빈 결과 반환 (500 에러 대신)
        from ..models.support_center import SupportCenterResponse

        # 긴급 연락처는 service 없이도 제공 가능
        emergency_contacts = []
        if service:
            try:
                emergency_contacts = service._get_emergency_contacts()
            except Exception as contacts_error:
                logger.warning(f"긴급 연락처 조회 실패: {contacts_error}")

        return SupportCenterResponse(
            centers=[],
            total=0,
            emergency_contacts=emergency_contacts
        )


@router.post("/api/centers", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_center(center: SupportCenter):
    """
    새 지원 기관 추가 (관리자 전용)

    - **center**: 지원 기관 정보
    """
    try:
        service = get_support_center_service()
        center_id = await service.add_center(center)
        return {"id": center_id, "message": "지원 기관이 추가되었습니다"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"지원 기관 추가 오류: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    지원 기관 서비스 상태 확인
    """
    try:
        service = get_support_center_service()
        health_status = service.get_health_status()

        if health_status.get("firestore") == "healthy":
            return {"status": "healthy", "details": health_status}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_status
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )
