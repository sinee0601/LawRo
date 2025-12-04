"""
Work Time Service
Handles work time tracking and workplace management
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import math
from ..database import get_firebase, Collections
from ..models.worktime import WorkplaceLocation, LocationData, WorkRecord

logger = logging.getLogger(__name__)


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in meters
    """
    R = 6371000  # Earth radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


class WorkTimeService:
    """Work time tracking service"""

    def __init__(self):
        try:
            self.firebase = get_firebase()
            self.db = self.firebase.db
            self.use_firestore = True
            logger.info("✓ Firestore initialized for WorkTime service")
        except Exception as e:
            logger.warning(f"✗ Firestore initialization failed for WorkTime: {e}")
            self.use_firestore = False

    # ==================== Workplace Management ====================

    def get_workplace(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's workplace location from Firestore"""
        if not self.use_firestore:
            return None

        try:
            docs = self.db.collection(Collections.WORKPLACE).where(
                "user_id", "==", user_id
            ).limit(1).stream()

            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                return data

            return None
        except Exception as e:
            logger.error(f"Failed to get workplace: {e}")
            return None

    def save_workplace(self, user_id: str, latitude: float, longitude: float,
                      address: Optional[str] = None, radius_meters: int = 500) -> bool:
        """Save or update user's workplace location"""
        if not self.use_firestore:
            logger.warning("Firestore not initialized - workplace will not be saved")
            return False

        try:
            # Check if workplace already exists
            existing = self.get_workplace(user_id)

            workplace_data = {
                "user_id": user_id,
                "latitude": latitude,
                "longitude": longitude,
                "address": address,
                "radius_meters": radius_meters,
                "updated_at": datetime.now(),
            }

            if existing:
                # Update existing
                self.db.collection(Collections.WORKPLACE).document(existing["id"]).update(
                    workplace_data
                )
                logger.info(f"✓ Workplace updated for user {user_id}")
            else:
                # Create new
                workplace_data["created_at"] = datetime.now()
                self.db.collection(Collections.WORKPLACE).document().set(workplace_data)
                logger.info(f"✓ Workplace created for user {user_id}")

            return True
        except Exception as e:
            logger.error(f"Failed to save workplace: {e}")
            return False

    def delete_workplace(self, user_id: str) -> bool:
        """Delete user's workplace location"""
        if not self.use_firestore:
            return False

        try:
            workplace = self.get_workplace(user_id)
            if workplace:
                self.db.collection(Collections.WORKPLACE).document(workplace["id"]).delete()
                logger.info(f"✓ Workplace deleted for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete workplace: {e}")
            return False

    # ==================== Location Status ====================

    def check_location_status(self, user_id: str, current_lat: float, current_lon: float) -> Dict[str, Any]:
        """
        Check if current location is within workplace radius

        Returns:
            {
                "is_within_workplace": bool,
                "distance_meters": float,
                "workplace": {...},
                "message": str
            }
        """
        workplace = self.get_workplace(user_id)

        if not workplace:
            return {
                "is_within_workplace": False,
                "distance_meters": 0,
                "workplace": None,
                "message": "근무지가 등록되지 않았습니다."
            }

        distance = calculate_distance(
            current_lat, current_lon,
            workplace["latitude"], workplace["longitude"]
        )

        is_within = distance <= workplace.get("radius_meters", 500)

        return {
            "is_within_workplace": is_within,
            "distance_meters": round(distance, 2),
            "workplace": {
                "latitude": workplace["latitude"],
                "longitude": workplace["longitude"],
                "address": workplace.get("address"),
                "radius_meters": workplace.get("radius_meters", 500)
            },
            "message": f"근무지로부터 {distance:.0f}m {'이내' if is_within else '초과'}"
        }

    # ==================== Work Records ====================

    def save_work_record(self, user_id: str, start_time: datetime, end_time: datetime,
                        location: Dict[str, Any], date: str) -> bool:
        """Save work record to Firestore"""
        if not self.use_firestore:
            logger.warning("Firestore not initialized - work record will not be saved")
            return False

        try:
            # Calculate duration
            duration = end_time - start_time
            duration_seconds = int(duration.total_seconds())

            record_data = {
                "user_id": user_id,
                "start_time": start_time,
                "end_time": end_time,
                "duration_seconds": duration_seconds,
                "location": {
                    "latitude": location.get("latitude"),
                    "longitude": location.get("longitude"),
                    "address": location.get("address")
                },
                "date": date,
                "created_at": datetime.now()
            }

            self.db.collection(Collections.WORK_RECORDS).document().set(record_data)
            logger.info(f"✓ Work record saved for user {user_id}: {duration_seconds}s")
            return True
        except Exception as e:
            logger.error(f"Failed to save work record: {e}")
            return False

    def get_work_records(self, user_id: str, limit: int = 100, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user's work records from Firestore"""
        if not self.use_firestore:
            return []

        try:
            # Simple query: only filter by user_id to avoid composite index
            # Sorting and date filtering done in memory
            docs = self.db.collection(Collections.WORK_RECORDS).where(
                "user_id", "==", user_id
            ).stream()

            records = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id

                # Apply date filter in memory if specified
                if date and data.get("date") != date:
                    continue

                records.append(data)

            # Sort by created_at in memory (descending)
            records.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)

            # Return limited results
            return records[:limit]
        except Exception as e:
            logger.error(f"Failed to get work records: {e}")
            return []

    def delete_work_record(self, record_id: str, user_id: str) -> bool:
        """Delete a work record"""
        if not self.use_firestore:
            return False

        try:
            self.db.collection(Collections.WORK_RECORDS).document(record_id).delete()
            logger.info(f"✓ Work record deleted: {record_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete work record: {e}")
            return False

    def get_work_summary(self, user_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get work summary for a date range

        Returns total hours, records count, etc.
        """
        if not self.use_firestore:
            return {
                "total_seconds": 0,
                "total_hours": 0,
                "record_count": 0,
                "records": []
            }

        try:
            # Build simple query without date range filters to avoid composite index
            docs = self.db.collection(Collections.WORK_RECORDS).where(
                "user_id", "==", user_id
            ).stream()

            records = []
            total_seconds = 0

            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id

                # Apply date range filter in memory
                record_date = data.get("date")
                if record_date and start_date <= record_date <= end_date:
                    records.append(data)
                    total_seconds += data.get("duration_seconds", 0)

            total_hours = total_seconds / 3600

            return {
                "total_seconds": total_seconds,
                "total_hours": round(total_hours, 2),
                "record_count": len(records),
                "records": records
            }
        except Exception as e:
            logger.error(f"Failed to get work summary: {e}")
            return {
                "total_seconds": 0,
                "total_hours": 0,
                "record_count": 0,
                "records": []
            }
