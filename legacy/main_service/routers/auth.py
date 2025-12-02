from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse
import requests
import os
from dotenv import load_dotenv

from models import (
    UserSignupRequest, UserSignupResponse, UserLoginRequest, UserLoginResponse,
    SocialLoginResponse, GoogleUserInfo, KakaoUserInfo, NaverUserInfo
)
from services.user_service import UserService

load_dotenv()

router = APIRouter()
security = HTTPBearer()
user_service = UserService()

# OAuth 설정
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_REDIRECT_URI = os.getenv("NAVER_REDIRECT_URI")

@router.post("/signup", response_model=UserSignupResponse)
async def user_signup(request: UserSignupRequest):
    """사용자 회원가입"""
    try:
        result = await user_service.create_user(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"회원가입 중 오류가 발생했습니다: {str(e)}")

@router.post("/login", response_model=UserLoginResponse)
async def user_login(request: UserLoginRequest):
    """사용자 로그인"""
    try:
        result = await user_service.authenticate_user(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로그인 중 오류가 발생했습니다: {str(e)}")

@router.get("/profile")
async def get_user_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """사용자 프로필 조회"""
    try:
        token = credentials.credentials
        user_data = await user_service.get_user_by_token(token)
        return {
            "success": True,
            "user": user_data
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로필 조회 중 오류가 발생했습니다: {str(e)}")

# 구글 로그인
@router.get("/google/login")
async def google_login():
    """구글 로그인 페이지로 리다이렉트"""
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid%20email%20profile"
    )
    return RedirectResponse(url)

@router.get("/google/callback", response_model=SocialLoginResponse)
async def google_callback(code: str):
    """구글 OAuth 콜백 처리"""
    try:
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        token_res = requests.post(token_url, data=data)
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Token exchange failed")

        access_token = token_res.json()["access_token"]

        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

        google_user = GoogleUserInfo(**user_info)
        
        user_data = await user_service.get_or_create_social_user(
            email=google_user.email,
            full_name=google_user.name or google_user.email.split("@")[0],
            social_type="google",
            social_id=user_info.get("id")
        )

        token = await user_service.create_access_token(user_data)

        return SocialLoginResponse(
            success=True,
            message="구글 로그인 성공",
            access_token=token,
            token_type="bearer",
            user_info=user_data
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"구글 로그인 처리 중 오류가 발생했습니다: {str(e)}"
        )

# 카카오 로그인
@router.get("/kakao/login")
async def kakao_login():
    """카카오 로그인 페이지로 리다이렉트"""
    url = (
        "https://kauth.kakao.com/oauth/authorize"
        f"?client_id={KAKAO_CLIENT_ID}"
        f"&redirect_uri={KAKAO_REDIRECT_URI}"
        "&response_type=code"
    )
    return RedirectResponse(url)

@router.get("/kakao/callback", response_model=SocialLoginResponse)
async def kakao_callback(code: str):
    """카카오 OAuth 콜백 처리"""
    try:
        token_url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": KAKAO_CLIENT_ID,
            "client_secret": KAKAO_CLIENT_SECRET,
            "redirect_uri": KAKAO_REDIRECT_URI,
            "code": code
        }
        token_res = requests.post(token_url, data=data)
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Token exchange failed")

        access_token = token_res.json()["access_token"]

        user_info = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

        kakao_user = KakaoUserInfo(
            id=user_info["id"],
            email=user_info.get("kakao_account", {}).get("email"),
            nickname=user_info.get("properties", {}).get("nickname"),
            profile_image=user_info.get("properties", {}).get("profile_image"),
            gender=user_info.get("kakao_account", {}).get("gender"),
            age_range=user_info.get("kakao_account", {}).get("age_range")
        )
        
        user_data = await user_service.get_or_create_social_user(
            email=kakao_user.email or f"kakao_{kakao_user.id}@kakao.com",
            full_name=kakao_user.nickname or f"카카오사용자_{kakao_user.id}",
            social_type="kakao",
            social_id=str(kakao_user.id)
        )

        token = await user_service.create_access_token(user_data)

        return SocialLoginResponse(
            success=True,
            message="카카오 로그인 성공",
            access_token=token,
            token_type="bearer",
            user_info=user_data
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"카카오 로그인 처리 중 오류가 발생했습니다: {str(e)}"
        )

# 네이버 로그인
@router.get("/naver/login")
async def naver_login():
    """네이버 로그인 페이지로 리다이렉트"""
    url = (
        "https://nid.naver.com/oauth2.0/authorize"
        f"?client_id={NAVER_CLIENT_ID}"
        f"&redirect_uri={NAVER_REDIRECT_URI}"
        "&response_type=code"
        "&state=naver_login"
    )
    return RedirectResponse(url)

@router.get("/naver/callback", response_model=SocialLoginResponse)
async def naver_callback(code: str, state: str):
    """네이버 OAuth 콜백 처리"""
    try:
        if state != "naver_login":
            raise HTTPException(status_code=400, detail="Invalid state parameter")

        token_url = "https://nid.naver.com/oauth2.0/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": NAVER_CLIENT_ID,
            "client_secret": NAVER_CLIENT_SECRET,
            "redirect_uri": NAVER_REDIRECT_URI,
            "code": code,
            "state": state
        }
        token_res = requests.post(token_url, data=data)
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Token exchange failed")

        access_token = token_res.json()["access_token"]

        user_info = requests.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

        if user_info.get("response"):
            user_info = user_info["response"]
        else:
            raise HTTPException(status_code=400, detail="Failed to get user info")

        naver_user = NaverUserInfo(
            id=user_info["id"],
            email=user_info["email"],
            name=user_info.get("name"),
            nickname=user_info.get("nickname"),
            profile_image=user_info.get("profile_image"),
            gender=user_info.get("gender"),
            age=user_info.get("age")
        )
        
        user_data = await user_service.get_or_create_social_user(
            email=naver_user.email,
            full_name=naver_user.name or naver_user.nickname or f"네이버사용자_{naver_user.id}",
            social_type="naver",
            social_id=naver_user.id
        )

        token = await user_service.create_access_token(user_data)

        return SocialLoginResponse(
            success=True,
            message="네이버 로그인 성공",
            access_token=token,
            token_type="bearer",
            user_info=user_data
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"네이버 로그인 처리 중 오류가 발생했습니다: {str(e)}"
        )