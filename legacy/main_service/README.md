# LawRo Main Docker - MySQL 버전

## 개요
LawRo 메인 API 서버가 MySQL 데이터베이스를 사용하도록 변경되었습니다.

## MySQL 설정

### 1. 환경 변수 설정
`env.example` 파일을 `.env`로 복사하고 MySQL 설정을 확인하세요:

```bash
cp env.example .env
```

### 2. MySQL 데이터베이스 생성
실행 중인 MySQL 컨테이너에 접속하여 `lawro_db` 데이터베이스를 생성하세요:

```bash
# MySQL 컨테이너에 접속
docker exec -it shared-mysql mysql -u root -p

# 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS lawro_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 데이터베이스 확인
SHOW DATABASES;

# 종료
EXIT;
```

또는 한 줄로:
```bash
docker exec -it shared-mysql mysql -u root -prootpassword -e "CREATE DATABASE IF NOT EXISTS lawro_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 3. 데이터베이스 테이블 구조

자동으로 생성되는 테이블들:

#### users 테이블
- `user_id` (VARCHAR(50)) - Primary Key
- `email` (VARCHAR(100)) - Unique
- `password_hash` (VARCHAR(255))
- `is_active` (BOOLEAN) - Default: true
- `created_at` (DATETIME)
- `updated_at` (DATETIME)

#### chat_sessions 테이블
- `session_id` (VARCHAR(50)) - Primary Key
- `user_id` (VARCHAR(50))
- `created_at` (DATETIME)
- `updated_at` (DATETIME)

#### contract_sessions 테이블
- `contract_id` (VARCHAR(50)) - Primary Key
- `user_id` (VARCHAR(50))
- `language` (VARCHAR(20)) - Default: 'korean'
- `original_data` (TEXT) - OCR 원본 데이터
- `corrected_data` (TEXT) - 사용자가 수정한 데이터
- `analysis_result` (TEXT) - 분석 결과
- `created_at` (DATETIME)
- `updated_at` (DATETIME)

## 실행 방법

### 방법 1: Docker Compose 사용
```bash
# 이미지 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build
```

### 방법 2: 단독 컨테이너 실행
```bash
# 이미지 빌드
docker build -t lawro-main-api .

# 컨테이너 실행
docker run -d \
  --name lawro-main-api \
  -p 8000:8000 \
  --network bridge \
  --link shared-mysql:mysql \
  -e MYSQL_HOST=shared-mysql \
  -e MYSQL_DATABASE=lawro_db \
  -e MYSQL_USER=root \
  -e MYSQL_PASSWORD=rootpassword \
  lawro-main-api
```

### 방법 3: 기존 네트워크에 연결
```bash
# 기존 MySQL이 속한 네트워크 확인
docker inspect shared-mysql | grep NetworkMode

# 같은 네트워크에서 실행
docker run -d \
  --name lawro-main-api \
  -p 8000:8000 \
  --network [NETWORK_NAME] \
  -e MYSQL_HOST=shared-mysql \
  lawro-main-api
```

## API 테스트

### 헬스 체크
```bash
curl http://localhost:8000/health
```

### 회원가입 테스트
```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "password": "password123",
    "email": "test@example.com"
  }'
```

### 로그인 테스트
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "password": "password123"
  }'
```

## 데이터베이스 연결 확인

### MySQL 컨테이너에서 직접 확인
```bash
# MySQL 접속
docker exec -it shared-mysql mysql -u root -p

# lawro_db 선택
USE lawro_db;

# 테이블 확인
SHOW TABLES;

# 사용자 데이터 확인
SELECT * FROM users;
```

## 주요 변경사항

1. **Firestore → MySQL**: Firebase Firestore에서 MySQL로 데이터베이스 변경
2. **SQLAlchemy ORM**: Python ORM 사용으로 데이터베이스 작업 간소화
3. **자동 테이블 생성**: 앱 시작 시 필요한 테이블 자동 생성
4. **bcrypt 암호화**: 패스워드 해싱을 SHA256에서 bcrypt로 변경
5. **트랜잭션 관리**: 데이터베이스 트랜잭션과 오류 처리 개선

## 문제 해결

### 연결 오류
- MySQL 컨테이너가 실행 중인지 확인
- 네트워크 설정 확인
- 환경 변수 설정 확인

### 테이블 생성 오류
- MySQL 권한 확인
- 데이터베이스 존재 여부 확인

### 로그 확인
```bash
# 컨테이너 로그 확인
docker logs lawro-main-api

# MySQL 로그 확인
docker logs shared-mysql
``` 