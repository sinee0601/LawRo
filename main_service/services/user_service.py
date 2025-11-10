import os
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import json

from database import get_db, User, ChatSession, ContractSession, hash_password, verify_password, create_tables
from models import UserSignupRequest, UserSignupResponse, UserLoginRequest, UserLoginResponse, ContractAnalyzeResponse

class UserService:
    """MySQL을 사용한 사용자 관리 서비스"""
    
    def __init__(self):
        # JWT 설정
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "lawro-secret-key-change-in-production")
        self.jwt_algorithm = "HS256"
        self.jwt_expiration_hours = 24
        
        # 테이블 생성
        try:
            create_tables()
            print("✅ MySQL 테이블 초기화 완료")
        except Exception as e:
            print(f"❌ MySQL 테이블 초기화 실패: {e}")
    
    def _generate_jwt_token(self, user_id: str) -> str:
        """JWT 토큰 생성"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=self.jwt_expiration_hours),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("토큰이 만료되었습니다")
        except jwt.InvalidTokenError:
            raise ValueError("유효하지 않은 토큰입니다")
    
    async def create_user(self, request: UserSignupRequest) -> UserSignupResponse:
        """사용자 회원가입"""
        db = next(get_db())
        try:
            # 이메일 중복 확인
            existing_email = db.query(User).filter(User.email == request.email).first()
            if existing_email:
                return UserSignupResponse(
                    success=False,
                    message="이미 사용 중인 이메일입니다",
                    user_id=None
                )
            
            # 비밀번호 해시화
            hashed_password_value = hash_password(request.password)
            
            # 고유한 사용자 ID 생성 (UUID 기반)
            generated_user_id = str(uuid.uuid4())[:8]  # 8자리 짧은 ID
            
            # 새 사용자 생성
            new_user = User(
                user_id=generated_user_id,
                email=request.email,
                password_hash=hashed_password_value,
                full_name=request.full_name,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # 데이터베이스에 저장
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            return UserSignupResponse(
                success=True,
                message="회원가입이 완료되었습니다",
                user_id=generated_user_id
            )
            
        except IntegrityError as e:
            db.rollback()
            # 데이터베이스 에러 메시지에서 이메일 중복 여부 확인
            error_message = str(e)
            if "Duplicate entry" in error_message and "email" in error_message:
                return UserSignupResponse(
                    success=False,
                    message="이미 사용 중인 이메일입니다",
                    user_id=None
                )
            return UserSignupResponse(
                success=False,
                message="데이터베이스 제약 조건 위반입니다",
                user_id=None
            )
        except Exception as e:
            db.rollback()
            return UserSignupResponse(
                success=False,
                message=f"회원가입 중 오류가 발생했습니다: {str(e)}",
                user_id=None
            )
        finally:
            db.close()
    
    async def authenticate_user(self, request: UserLoginRequest) -> UserLoginResponse:
        """사용자 로그인 (이메일 기반)"""
        db = next(get_db())
        try:
            # 이메일로 사용자 조회
            user = db.query(User).filter(User.email == request.email).first()
            
            if not user:
                return UserLoginResponse(
                    success=False,
                    message="존재하지 않는 사용자입니다",
                    access_token=None,
                    user_info=None
                )
            
            # 비밀번호 확인
            if not verify_password(request.password, user.password_hash):
                return UserLoginResponse(
                    success=False,
                    message="비밀번호가 틀렸습니다",
                    access_token=None,
                    user_info=None
                )
            
            # 활성 사용자 확인
            if not user.is_active:
                return UserLoginResponse(
                    success=False,
                    message="비활성화된 계정입니다",
                    access_token=None,
                    user_info=None
                )
            
            # 마지막 로그인 시간 업데이트
            user.updated_at = datetime.utcnow()
            db.commit()
            
            # JWT 토큰 생성
            token = self._generate_jwt_token(user.user_id)
            
            # 사용자 정보 (user_id, email만 포함)
            user_info = {
                "user_id": user.user_id,
                "email": user.email
            }
            
            return UserLoginResponse(
                success=True,
                message="로그인 성공",
                access_token=token,
                token_type="bearer",
                user_info=user_info
            )
            
        except Exception as e:
            return UserLoginResponse(
                success=False,
                message=f"로그인 중 오류가 발생했습니다: {str(e)}",
                access_token=None,
                user_info=None
            )
        finally:
            db.close()
    
    async def get_user_by_token(self, token: str) -> Dict[str, Any]:
        """토큰으로 사용자 정보 조회"""
        db = next(get_db())
        try:
            # 토큰 검증
            payload = self._verify_jwt_token(token)
            user_id = payload.get("user_id")
            
            if not user_id:
                raise ValueError("토큰에서 user_id를 찾을 수 없습니다")
            
            # 사용자 조회
            user = db.query(User).filter(User.user_id == user_id).first()
            
            if not user:
                raise ValueError("존재하지 않는 사용자입니다")
            
            if not user.is_active:
                raise ValueError("비활성화된 계정입니다")
            
            # 사용자 정보 반환
            return {
                "user_id": user.user_id,
                "email": user.email,
                "full_name": user.full_name,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            
        except Exception as e:
            raise ValueError(f"사용자 조회 실패: {str(e)}")
        finally:
            db.close()
    
    async def save_contract_analysis(self, user_id: str, contract_id: str, language: str, 
                                   original_data: str = None, corrected_data: str = None, 
                                   analysis_result: str = None):
        """계약서 분석 결과 저장"""
        db = next(get_db())
        try:
            # 기존 세션 확인
            contract_session = db.query(ContractSession).filter(
                ContractSession.contract_id == contract_id
            ).first()
            
            if contract_session:
                # 기존 세션 업데이트
                if original_data:
                    contract_session.original_data = original_data
                if corrected_data:
                    contract_session.corrected_data = corrected_data
                if analysis_result:
                    contract_session.analysis_result = analysis_result
                contract_session.updated_at = datetime.utcnow()
            else:
                # 새 세션 생성
                contract_session = ContractSession(
                    contract_id=contract_id,
                    user_id=user_id,
                    language=language,
                    original_data=original_data,
                    corrected_data=corrected_data,
                    analysis_result=analysis_result,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(contract_session)
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            raise Exception(f"계약서 분석 저장 실패: {str(e)}")
        finally:
            db.close()
    
    async def get_contract_history(self, user_id: str) -> List[Dict[str, Any]]:
        """사용자의 계약서 분석 이력 조회"""
        db = next(get_db())
        try:
            contract_sessions = db.query(ContractSession).filter(
                ContractSession.user_id == user_id
            ).order_by(ContractSession.created_at.desc()).all()
            
            history = []
            for session in contract_sessions:
                history.append({
                    "contract_id": session.contract_id,
                    "language": session.language,
                    "has_analysis": bool(session.analysis_result),
                    "created_at": session.created_at.isoformat() if session.created_at else None,
                    "updated_at": session.updated_at.isoformat() if session.updated_at else None
                })
            
            return history
            
        except Exception as e:
            raise Exception(f"계약서 이력 조회 실패: {str(e)}")
        finally:
            db.close()
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """사용자 통계 조회"""
        db = next(get_db())
        try:
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            total_contracts = db.query(ContractSession).count()
            total_chat_sessions = db.query(ChatSession).count()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": total_users - active_users,
                "total_contracts": total_contracts,
                "total_chat_sessions": total_chat_sessions,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"통계 조회 실패: {str(e)}")
        finally:
            db.close()
    
    async def save_chat_session(self, session_id: str, user_id: str):
        """채팅 세션 저장"""
        db = next(get_db())
        try:
            # 기존 세션 확인
            existing_session = db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
            
            if not existing_session:
                # 새 세션 생성
                chat_session = ChatSession(
                    session_id=session_id,
                    user_id=user_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(chat_session)
                db.commit()
            
        except Exception as e:
            db.rollback()
            raise Exception(f"채팅 세션 저장 실패: {str(e)}")
        finally:
            db.close()

    async def get_or_create_social_user(self, email: str, full_name: str, social_type: str, social_id: str) -> Dict[str, Any]:
        """소셜 로그인 사용자 생성 또는 조회"""
        db = next(get_db())
        try:
            # 이메일로 사용자 조회
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                # 새 사용자 생성
                generated_user_id = str(uuid.uuid4())[:8]
                new_user = User(
                    user_id=generated_user_id,
                    email=email,
                    full_name=full_name,
                    social_type=social_type,
                    social_id=social_id,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                user = new_user
            else:
                # 기존 사용자 정보 업데이트
                user.full_name = full_name
                user.social_type = social_type
                user.social_id = social_id
                user.updated_at = datetime.utcnow()
                db.commit()
            
            # 사용자 정보 반환
            return {
                "user_id": user.user_id,
                "email": user.email,
                "full_name": user.full_name,
                "social_type": user.social_type,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            
        except Exception as e:
            db.rollback()
            raise Exception(f"소셜 사용자 처리 실패: {str(e)}")
        finally:
            db.close()

    async def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """사용자 정보로 JWT 토큰 생성"""
        return self._generate_jwt_token(user_data["user_id"]) 