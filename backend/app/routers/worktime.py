"""
Work Time Router
Handles work time tracking and workplace management
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import get_current_user_optional
from ..models.worktime import (
    LocationStatusRequest,
    LocationStatusResponse,
    SaveWorkplaceRequest,
    SaveWorkRecordRequest,
)
from ..services.worktime_service import WorkTimeService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/worktime", tags=["worktime"])

# Global service instance
_worktime_service: WorkTimeService = None


def get_worktime_service() -> WorkTimeService:
    """Get work time service instance"""
    global _worktime_service
    if _worktime_service is None:
        _worktime_service = WorkTimeService()
    return _worktime_service


# ==================== Workplace Endpoints ====================

@router.post("/workplace", response_model=dict)
async def save_workplace(
    request: SaveWorkplaceRequest,
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Save or update user's workplace location

    The workplace location is used to verify work sessions
    """
    try:
        user_id = current_user.get("uid") if current_user else "default_user"

        service = get_worktime_service()
        success = service.save_workplace(
            user_id=user_id,
            latitude=request.latitude,
            longitude=request.longitude,
            address=request.address,
            radius_meters=request.radius_meters
        )

        if success:
            return {
                "message": "근무지가 저장되었습니다",
                "workplace": {
                    "latitude": request.latitude,
                    "longitude": request.longitude,
                    "address": request.address,
                    "radius_meters": request.radius_meters
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="근무지 저장에 실패했습니다"
            )
    except Exception as e:
        logger.error(f"Failed to save workplace: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"근무지 저장 실패: {str(e)}"
        )


@router.get("/workplace", response_model=dict)
async def get_workplace(
    current_user: dict = Depends(get_current_user_optional)
):
    """Get user's workplace location"""
    try:
        user_id = current_user.get("uid") if current_user else "default_user"

        service = get_worktime_service()
        workplace = service.get_workplace(user_id)

        if workplace:
            # Remove internal fields
            workplace.pop("user_id", None)
            workplace.pop("created_at", None)
            workplace.pop("updated_at", None)

            return {
                "message": "근무지 정보 조회 성공",
                "workplace": workplace
            }
        else:
            return {
                "message": "등록된 근무지가 없습니다",
                "workplace": None
            }
    except Exception as e:
        logger.error(f"Failed to get workplace: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"근무지 조회 실패: {str(e)}"
        )


@router.delete("/workplace")
async def delete_workplace(
    current_user: dict = Depends(get_current_user_optional)
):
    """Delete user's workplace location"""
    try:
        user_id = current_user.get("uid") if current_user else "default_user"

        service = get_worktime_service()
        success = service.delete_workplace(user_id)

        if success:
            return {"message": "근무지가 삭제되었습니다"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="삭제할 근무지가 없습니다"
            )
    except Exception as e:
        logger.error(f"Failed to delete workplace: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"근무지 삭제 실패: {str(e)}"
        )


# ==================== Location Status ====================

@router.post("/location-status", response_model=LocationStatusResponse)
async def check_location_status(
    request: LocationStatusRequest,
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Check if current location is within workplace radius

    This endpoint determines if the user can start/continue work tracking
    """
    try:
        user_id = current_user.get("uid") if current_user else "default_user"

        service = get_worktime_service()
        status_data = service.check_location_status(
            user_id=user_id,
            current_lat=request.current_latitude,
            current_lon=request.current_longitude
        )

        return LocationStatusResponse(**status_data)
    except Exception as e:
        logger.error(f"Failed to check location status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"위치 확인 실패: {str(e)}"
        )


# ==================== Work Records ====================

@router.post("/records", response_model=dict)
async def save_work_record(
    request: SaveWorkRecordRequest,
    current_user: dict = Depends(get_current_user_optional)
):
    """Save a work record"""
    try:
        user_id = current_user.get("uid") if current_user else "default_user"

        service = get_worktime_service()
        success = service.save_work_record(
            user_id=user_id,
            start_time=request.start_time,
            end_time=request.end_time,
            location=request.location.dict(),
            date=request.date
        )

        if success:
            # Calculate duration for response
            duration = request.end_time - request.start_time
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            seconds = int(duration.total_seconds() % 60)

            return {
                "message": "근무 기록이 저장되었습니다",
                "duration_formatted": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
                "duration_seconds": int(duration.total_seconds())
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="근무 기록 저장에 실패했습니다"
            )
    except Exception as e:
        logger.error(f"Failed to save work record: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"근무 기록 저장 실패: {str(e)}"
        )


@router.get("/records", response_model=dict)
async def get_work_records(
    date: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Get user's work records

    Optional date filter: YYYY-MM-DD format
    """
    try:
        user_id = current_user.get("uid") if current_user else "default_user"

        service = get_worktime_service()
        records = service.get_work_records(user_id, limit=limit, date=date)

        # Calculate total hours
        total_seconds = sum(r.get("duration_seconds", 0) for r in records)
        total_hours = total_seconds / 3600

        return {
            "message": "근무 기록 조회 성공",
            "records": records,
            "count": len(records),
            "total_hours": round(total_hours, 2),
            "total_seconds": total_seconds
        }
    except Exception as e:
        logger.error(f"Failed to get work records: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"근무 기록 조회 실패: {str(e)}"
        )


@router.delete("/records/{record_id}")
async def delete_work_record(
    record_id: str,
    current_user: dict = Depends(get_current_user_optional)
):
    """Delete a work record"""
    try:
        user_id = current_user.get("uid") if current_user else "default_user"

        service = get_worktime_service()
        success = service.delete_work_record(record_id, user_id)

        if success:
            return {"message": "근무 기록이 삭제되었습니다"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="삭제할 근무 기록이 없습니다"
            )
    except Exception as e:
        logger.error(f"Failed to delete work record: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"근무 기록 삭제 실패: {str(e)}"
        )


@router.get("/summary")
async def get_work_summary(
    start_date: str,
    end_date: str,
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Get work summary for a date range

    Date format: YYYY-MM-DD
    """
    try:
        user_id = current_user.get("uid") if current_user else "default_user"

        service = get_worktime_service()
        summary = service.get_work_summary(user_id, start_date, end_date)

        return {
            "message": "근무 요약 조회 성공",
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Failed to get work summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"근무 요약 조회 실패: {str(e)}"
        )


@router.get("/health")
async def worktime_health_check():
    """Work time service health check"""
    try:
        service = get_worktime_service()
        return {
            "status": "healthy",
            "firestore": "available" if service.use_firestore else "unavailable"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
