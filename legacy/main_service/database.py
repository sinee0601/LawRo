import os
import json
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
from passlib.context import CryptContext

# 환경 변수
MYSQL_HOST = os.getenv("MYSQL_HOST", "shared-mysql")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "lawro_db")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "rootpassword")

# 데이터베이스 URL
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# SQLAlchemy 설정
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 암호화 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User 모델 (소셜 로그인 지원 추가)
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String(8), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255), nullable=True)  # 소셜 로그인의 경우 NULL 가능
    full_name = Column(String(255))
    social_type = Column(String(50), nullable=True)  # 'google', 'kakao', 'naver' 등
    social_id = Column(String(255), nullable=True)  # 소셜 서비스의 사용자 ID
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 세션 모델 (채팅 세션 관리용)
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    session_id = Column(String(50), primary_key=True)
    user_id = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 계약서 분석 저장 모델 (main-docker의 주요 기능)
class ContractAnalysis(Base):
    __tablename__ = "contract_analysis"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False)
    contract_id = Column(String(50), unique=True, nullable=False)
    analysis_result = Column(Text, nullable=False)  # JSON 문자열로 저장
    language = Column(String(20), default="korean")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 계약서 분석 세션 모델 (기존, OCR 관련)
class ContractSession(Base):
    __tablename__ = "contract_sessions"
    
    contract_id = Column(String(50), primary_key=True)
    user_id = Column(String(50), nullable=False)
    language = Column(String(20), default="korean")
    original_data = Column(Text)  # OCR 원본 데이터
    corrected_data = Column(Text)  # 사용자가 수정한 데이터
    analysis_result = Column(Text)  # 분석 결과
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 데이터베이스 연결
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 테이블 생성
def create_tables():
    Base.metadata.create_all(bind=engine)

# 비밀번호 해싱
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 계약서 분석 결과 저장 함수 (main-docker의 핵심 기능)
def save_contract_analysis(db: Session, user_id: str, contract_id: str, analysis_result: dict, language: str = "korean"):
    """계약서 분석 결과를 DB에 저장"""
    try:
        # 기존 데이터가 있는지 확인
        existing = db.query(ContractAnalysis).filter(ContractAnalysis.contract_id == contract_id).first()
        
        analysis_json = json.dumps(analysis_result, ensure_ascii=False)
        
        if existing:
            # 업데이트
            existing.analysis_result = analysis_json
            existing.language = language
            existing.updated_at = datetime.utcnow()
        else:
            # 새로 생성
            new_analysis = ContractAnalysis(
                user_id=user_id,
                contract_id=contract_id,
                analysis_result=analysis_json,
                language=language
            )
            db.add(new_analysis)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ 계약서 분석 결과 저장 실패: {e}")
        return False

def get_contract_analysis(db: Session, contract_id: str) -> dict:
    """계약서 분석 결과를 DB에서 조회"""
    try:
        analysis = db.query(ContractAnalysis).filter(ContractAnalysis.contract_id == contract_id).first()
        if analysis:
            return {
                "user_id": analysis.user_id,
                "contract_id": analysis.contract_id,
                "analysis_result": json.loads(analysis.analysis_result),
                "language": analysis.language,
                "created_at": analysis.created_at,
                "updated_at": analysis.updated_at
            }
        return None
    except Exception as e:
        print(f"❌ 계약서 분석 결과 조회 실패: {e}")
        return None

def get_user_contract_history(db: Session, user_id: str):
    """사용자의 계약서 분석 히스토리 조회"""
    try:
        analyses = db.query(ContractAnalysis).filter(ContractAnalysis.user_id == user_id).order_by(ContractAnalysis.created_at.desc()).all()
        
        history = []
        for analysis in analyses:
            try:
                result_data = json.loads(analysis.analysis_result)
                # 기본 정보 추출
                company_name = "N/A"
                worker_name = "N/A"
                
                if "사업주" in result_data and "업체명" in result_data["사업주"]:
                    company_name = result_data["사업주"]["업체명"]
                elif "employer" in result_data and "company_name" in result_data["employer"]:
                    company_name = result_data["employer"]["company_name"]
                
                if "근로자" in result_data and "이름" in result_data["근로자"]:
                    worker_name = result_data["근로자"]["이름"]
                elif "employee" in result_data and "name" in result_data["employee"]:
                    worker_name = result_data["employee"]["name"]
                
                history.append({
                    "contract_id": analysis.contract_id,
                    "analysis_date": analysis.created_at,
                    "status": "completed",
                    "company_name": company_name,
                    "worker_name": worker_name,
                    "language": analysis.language
                })
            except Exception as e:
                print(f"⚠️ 히스토리 파싱 오류: {e}")
                history.append({
                    "contract_id": analysis.contract_id,
                    "analysis_date": analysis.created_at,
                    "status": "completed",
                    "company_name": "파싱 오류",
                    "worker_name": "파싱 오류",
                    "language": analysis.language
                })
        
        return history
    except Exception as e:
        print(f"❌ 사용자 계약서 히스토리 조회 실패: {e}")
        return [] 