"""
Database and Firebase Initialization
Manages Firebase Admin SDK and Firestore connections
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth
from functools import lru_cache
from typing import Optional
import os
import logging

from .config import settings

logger = logging.getLogger(__name__)


class FirebaseManager:
    """Manages Firebase Admin SDK initialization and connections"""

    _instance: Optional['FirebaseManager'] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.initialize()

    def initialize(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if already initialized
            if firebase_admin._apps:
                logger.info("Firebase already initialized")
                self._initialized = True
                return

            # Load credentials from file
            cred_path = settings.FIREBASE_CREDENTIALS_PATH

            if not os.path.exists(cred_path):
                logger.warning(f"Firebase credentials not found at {cred_path}")
                logger.warning("Firebase features will be disabled")
                return

            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

            logger.info("Firebase Admin SDK initialized successfully")
            self._initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise

    @property
    def db(self):
        """Get Firestore client"""
        if not self._initialized:
            raise RuntimeError("Firebase not initialized")
        return firestore.client()

    @property
    def auth(self):
        """Get Firebase Auth client"""
        if not self._initialized:
            raise RuntimeError("Firebase not initialized")
        return auth

    def is_initialized(self) -> bool:
        """Check if Firebase is initialized"""
        return self._initialized


@lru_cache()
def get_firebase() -> FirebaseManager:
    """Get Firebase manager singleton"""
    return FirebaseManager()


# Collections helper
class Collections:
    """Firestore collection names"""
    USERS = "users"
    CHAT_SESSIONS = "chat_sessions"
    CHAT_MESSAGES = "chat_messages"
    CONTRACT_SESSIONS = "contract_sessions"
    CONTRACT_ANALYSIS = "contract_analysis"
    WORKPLACE = "workplace_locations"
    WORK_RECORDS = "work_records"


def get_db():
    """Dependency for getting Firestore database"""
    firebase = get_firebase()
    if not firebase.is_initialized():
        raise RuntimeError("Firebase is not initialized. Check credentials.")
    return firebase.db
