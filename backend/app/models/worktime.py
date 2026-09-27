"""
Work Time Models
Request and response models for work time tracking
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Workplace Location Models
class WorkplaceLocation(BaseModel):
    """Workplace location data"""
    latitude: float = Field(..., description="Latitude of workplace")
    longitude: float = Field(..., description="Longitude of workplace")
    address: Optional[str] = Field(None, description="Address of workplace")
    radius_meters: int = Field(default=500, description="Allowed working radius in meters")


class SaveWorkplaceRequest(BaseModel):
    """Request to save workplace location"""
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    address: Optional[str] = Field(None, description="Workplace address")
    radius_meters: int = Field(default=500, description="Allowed working radius in meters")


class WorkplaceResponse(BaseModel):
    """Workplace response"""
    id: str
    user_id: str
    latitude: float
    longitude: float
    address: Optional[str]
    radius_meters: int
    created_at: datetime
    updated_at: datetime


# Work Record Models
class LocationData(BaseModel):
    """Location data for work record"""
    latitude: float
    longitude: float
    address: Optional[str] = None


class WorkRecord(BaseModel):
    """Work record data"""
    start_time: datetime = Field(..., description="Start time of work")
    end_time: Optional[datetime] = Field(None, description="End time of work")
    duration_seconds: int = Field(..., description="Work duration in seconds")
    location: LocationData = Field(..., description="Work location")
    date: str = Field(..., description="Work date (YYYY-MM-DD)")


class SaveWorkRecordRequest(BaseModel):
    """Request to save work record"""
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: int
    location: LocationData
    date: str


class WorkRecordResponse(BaseModel):
    """Work record response"""
    id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: int
    duration_formatted: str  # "HH:MM:SS" format
    location: LocationData
    date: str
    created_at: datetime


class WorkRecordsListResponse(BaseModel):
    """List of work records response"""
    records: List[WorkRecordResponse]
    total_count: int
    total_hours: float


# Status Check Models
class LocationStatusRequest(BaseModel):
    """Request to check if current location is within workplace"""
    current_latitude: float
    current_longitude: float


class LocationStatusResponse(BaseModel):
    """Response for location status check"""
    is_within_workplace: bool
    distance_meters: float
    workplace: Optional[WorkplaceLocation] = None
    message: str
