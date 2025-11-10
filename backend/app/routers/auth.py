"""
Authentication Router
Handles user authentication with Firebase Authentication
Compatible with existing frontend endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends
from firebase_admin import auth
import requests
import logging

from ..models.auth import (
    SignupRequest,
    LoginRequest,
    SocialAuthRequest,
    AuthResponse,
    UserResponse,
    MessageResponse,
)
from ..dependencies import get_current_user, get_firestore_db
from ..database import Collections
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


# Firebase REST API endpoints
FIREBASE_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts"
FIREBASE_TOKEN_URL = "https://securetoken.googleapis.com/v1/token"


def _get_user_response(user_record, firestore_user=None) -> UserResponse:
    """Convert Firebase user record to UserResponse"""
    return UserResponse(
        uid=user_record.uid,
        email=user_record.email,
        email_verified=user_record.email_verified,
        full_name=firestore_user.get("full_name") if firestore_user else user_record.display_name,
        picture=user_record.photo_url,
        provider=user_record.provider_data[0].provider_id if user_record.provider_data else None,
        created_at=firestore_user.get("created_at") if firestore_user else None,
    )


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db=Depends(get_firestore_db)):
    """
    Register a new user with email and password

    Compatible with: POST /auth/signup
    """
    try:
        # Create user in Firebase Authentication
        user = auth.create_user(
            email=request.email,
            password=request.password,
            display_name=request.full_name,
        )

        # Create custom token for immediate login
        custom_token = auth.create_custom_token(user.uid)

        # Exchange custom token for ID token using Firebase REST API
        response = requests.post(
            f"{FIREBASE_AUTH_URL}:signInWithCustomToken",
            params={"key": settings.FIREBASE_API_KEY},
            json={"token": custom_token.decode(), "returnSecureToken": True}
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate authentication token"
            )

        token_data = response.json()

        # Store user profile in Firestore
        from datetime import datetime
        user_data = {
            "uid": user.uid,
            "email": request.email,
            "full_name": request.full_name,
            "email_verified": False,
            "provider": "password",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        db.collection(Collections.USERS).document(user.uid).set(user_data)

        # Get fresh user record
        user_record = auth.get_user(user.uid)

        return AuthResponse(
            user=_get_user_response(user_record, user_data),
            id_token=token_data["idToken"],
            refresh_token=token_data["refreshToken"],
            expires_in=int(token_data["expiresIn"]),
        )

    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db=Depends(get_firestore_db)):
    """
    Login with email and password

    Compatible with: POST /auth/login
    """
    try:
        logger.info(f"Login attempt for email: {request.email}")

        # Sign in using Firebase REST API
        response = requests.post(
            f"{FIREBASE_AUTH_URL}:signInWithPassword",
            params={"key": settings.FIREBASE_API_KEY},
            json={
                "email": request.email,
                "password": request.password,
                "returnSecureToken": True,
            }
        )

        logger.info(f"Firebase response status: {response.status_code}")

        if response.status_code != 200:
            error_data = response.json()
            logger.error(f"Firebase login error: {error_data}")
            error_message = error_data.get("error", {}).get("message", "Invalid credentials")

            if "INVALID_PASSWORD" in error_message or "EMAIL_NOT_FOUND" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

        token_data = response.json()
        user_uid = token_data["localId"]

        # Get user record
        user_record = auth.get_user(user_uid)

        # Get user from Firestore
        user_doc = db.collection(Collections.USERS).document(user_uid).get()
        firestore_user = user_doc.to_dict() if user_doc.exists else None

        return AuthResponse(
            user=_get_user_response(user_record, firestore_user),
            id_token=token_data["idToken"],
            refresh_token=token_data["refreshToken"],
            expires_in=int(token_data["expiresIn"]),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_firestore_db)
):
    """
    Get current user profile

    Compatible with: GET /auth/profile
    Requires: Bearer token in Authorization header
    """
    try:
        # Get user from Firestore
        user_doc = db.collection(Collections.USERS).document(current_user["uid"]).get()

        if not user_doc.exists:
            # Get from Firebase Auth
            user_record = auth.get_user(current_user["uid"])
            return _get_user_response(user_record)

        firestore_user = user_doc.to_dict()
        user_record = auth.get_user(current_user["uid"])

        return _get_user_response(user_record, firestore_user)

    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile"
        )


# Social Authentication Endpoints
@router.get("/google/login")
async def google_login():
    """
    Initiate Google OAuth login

    Compatible with: GET /auth/google/login
    Note: With Firebase, this is typically handled on the client side
    """
    return {
        "message": "Use Firebase client SDK for Google authentication",
        "provider": "google.com",
        "instructions": "Call firebase.auth().signInWithPopup(googleProvider) on the client"
    }


@router.post("/google/callback", response_model=AuthResponse)
async def google_callback(request: SocialAuthRequest, db=Depends(get_firestore_db)):
    """
    Handle Google OAuth callback

    Compatible with: POST /auth/google/callback (modified from GET to POST)
    Client should send Firebase ID token after successful Google sign-in
    """
    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(request.id_token)
        user_uid = decoded_token["uid"]

        # Get user record
        user_record = auth.get_user(user_uid)

        # Check if user exists in Firestore, create if not
        user_ref = db.collection(Collections.USERS).document(user_uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            from datetime import datetime
            user_data = {
                "uid": user_uid,
                "email": user_record.email,
                "full_name": user_record.display_name,
                "email_verified": user_record.email_verified,
                "provider": "google.com",
                "picture": user_record.photo_url,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            user_ref.set(user_data)
        else:
            user_data = user_doc.to_dict()

        # Return user info (client already has tokens)
        return AuthResponse(
            user=_get_user_response(user_record, user_data),
            id_token=request.id_token,
            refresh_token="",  # Client handles refresh
            expires_in=3600,
        )

    except Exception as e:
        logger.error(f"Google callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID token"
        )


@router.get("/kakao/login")
async def kakao_login():
    """
    Initiate Kakao OAuth login

    Compatible with: GET /auth/kakao/login
    Note: Kakao requires custom provider setup in Firebase
    """
    return {
        "message": "Use Firebase custom authentication for Kakao",
        "provider": "kakao.com",
        "instructions": "Implement Kakao login on client, then send custom token to backend"
    }


@router.post("/kakao/callback", response_model=AuthResponse)
async def kakao_callback(request: SocialAuthRequest, db=Depends(get_firestore_db)):
    """
    Handle Kakao OAuth callback

    Compatible with: POST /auth/kakao/callback
    """
    # Similar to Google callback
    return await google_callback(request, db)


@router.get("/naver/login")
async def naver_login():
    """
    Initiate Naver OAuth login

    Compatible with: GET /auth/naver/login
    Note: Naver requires custom provider setup in Firebase
    """
    return {
        "message": "Use Firebase custom authentication for Naver",
        "provider": "naver.com",
        "instructions": "Implement Naver login on client, then send custom token to backend"
    }


@router.post("/naver/callback", response_model=AuthResponse)
async def naver_callback(request: SocialAuthRequest, db=Depends(get_firestore_db)):
    """
    Handle Naver OAuth callback

    Compatible with: POST /auth/naver/callback
    """
    # Similar to Google callback
    return await google_callback(request, db)


# Settings Endpoints
@router.put("/profile", response_model=MessageResponse)
async def update_profile(
    request: dict,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_firestore_db)
):
    """
    Update user profile information (name, language, theme)

    Compatible with: PUT /auth/profile
    Accepts:
    - full_name: 사용자 이름
    - preferred_language: 선호 언어 (korean, english, chinese, vietnamese, japanese, thai)
    - theme_preference: 테마 (light, dark)
    """
    try:
        user_uid = current_user["uid"]
        user_ref = db.collection(Collections.USERS).document(user_uid)

        # Prepare update data
        update_data = {}

        # Update full_name
        if "full_name" in request:
            full_name = request["full_name"]
            if not full_name or not isinstance(full_name, str) or len(full_name.strip()) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이름은 비어있을 수 없습니다."
                )
            update_data["full_name"] = full_name.strip()
            # Also update Firebase display name
            try:
                auth.update_user(user_uid, display_name=full_name.strip())
            except Exception as e:
                logger.warning(f"Failed to update Firebase display name: {e}")

        # Update language
        if "preferred_language" in request:
            language = request["preferred_language"]
            valid_languages = ["korean", "english", "chinese", "vietnamese", "japanese", "thai"]
            if language not in valid_languages:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"지원하지 않는 언어입니다. 지원 언어: {', '.join(valid_languages)}"
                )
            update_data["preferred_language"] = language

        # Update theme
        if "theme_preference" in request:
            theme = request["theme_preference"]
            valid_themes = ["light", "dark"]
            if theme not in valid_themes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"지원하지 않는 테마입니다. 지원 테마: {', '.join(valid_themes)}"
                )
            update_data["theme_preference"] = theme

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="업데이트할 정보가 없습니다."
            )

        # Update Firestore
        from datetime import datetime
        update_data["updated_at"] = datetime.utcnow()
        user_ref.update(update_data)

        logger.info(f"User profile updated: {user_uid}")
        return MessageResponse(message="사용자 정보가 업데이트되었습니다.")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로필 업데이트에 실패했습니다."
        )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: dict,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_firestore_db)
):
    """
    Change user password

    Compatible with: POST /auth/change-password
    Requires:
    - email: 사용자 이메일
    - current_password: 현재 비밀번호
    - new_password: 새 비밀번호
    """
    try:
        email = request.get("email")
        current_password = request.get("current_password")
        new_password = request.get("new_password")

        # Validate input
        if not all([email, current_password, new_password]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이메일, 현재 비밀번호, 새 비밀번호는 필수입니다."
            )

        if not isinstance(new_password, str) or len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="새 비밀번호는 8자 이상이어야 합니다."
            )

        if current_password == new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="새 비밀번호는 현재 비밀번호와 달라야 합니다."
            )

        # Verify current password using Firebase REST API
        try:
            verify_response = requests.post(
                f"{FIREBASE_AUTH_URL}:signInWithPassword",
                params={"key": settings.FIREBASE_API_KEY},
                json={
                    "email": email,
                    "password": current_password,
                    "returnSecureToken": True,
                }
            )

            if verify_response.status_code != 200:
                error_data = verify_response.json()
                logger.warning(f"Password verification failed for user: {email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="현재 비밀번호가 올바르지 않습니다."
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="현재 비밀번호 확인에 실패했습니다."
            )

        user_uid = current_user["uid"]

        # Update password in Firebase
        try:
            auth.update_user(user_uid, password=new_password)
        except Exception as e:
            logger.error(f"Failed to update password in Firebase: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호 변경에 실패했습니다."
            )

        # Update last password change timestamp
        from datetime import datetime
        user_ref = db.collection(Collections.USERS).document(user_uid)
        user_ref.update({
            "password_changed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        })

        logger.info(f"Password changed for user: {user_uid}")
        return MessageResponse(message="비밀번호가 성공적으로 변경되었습니다.")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="비밀번호 변경 중 오류가 발생했습니다."
        )
