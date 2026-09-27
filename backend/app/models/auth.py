"""
Authentication Models
Request and response models for authentication endpoints
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# Request Models
class SignupRequest(BaseModel):
    """User signup request"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    preferred_language: str = "korean"  # Default language for new users (korean, english, chinese, vietnamese, japanese, thai)


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class SocialAuthRequest(BaseModel):
    """Social authentication request"""
    id_token: str  # Firebase ID token from client-side auth


class UpdateProfileRequest(BaseModel):
    """Update user profile request"""
    full_name: Optional[str] = None
    preferred_language: Optional[str] = None
    theme_preference: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    email: EmailStr
    current_password: str
    new_password: str = Field(..., min_length=8)


# Response Models
class UserResponse(BaseModel):
    """User information response"""
    uid: str
    email: Optional[str] = None
    email_verified: bool = False
    full_name: Optional[str] = None
    preferred_language: Optional[str] = None
    picture: Optional[str] = None
    provider: Optional[str] = None
    created_at: Optional[datetime] = None


class AuthResponse(BaseModel):
    """Authentication response with token"""
    user: UserResponse
    id_token: str
    refresh_token: str
    expires_in: int


class TokenResponse(BaseModel):
    """Token-only response"""
    id_token: str
    refresh_token: str
    expires_in: int


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    detail: Optional[str] = None
