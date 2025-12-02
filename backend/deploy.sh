#!/bin/bash

# LawRo Backend EC2 배포 스크립트
# 사용법: bash deploy.sh

set -e

echo "======================================"
echo "🚀 LawRo Backend EC2 배포 시작"
echo "======================================"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 시스템 업데이트
echo -e "${YELLOW}[1/8] 시스템 업데이트 중...${NC}"
sudo apt update && sudo apt upgrade -y

# 2. 필수 패키지 설치
echo -e "${YELLOW}[2/8] 필수 패키지 설치 중...${NC}"
sudo apt install -y python3.11 python3.11-venv python3-pip git curl wget build-essential nginx

# 3. Python 가상환경 생성
echo -e "${YELLOW}[3/8] Python 가상환경 생성 중...${NC}"
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
    echo -e "${GREEN}✓ 가상환경 생성 완료${NC}"
else
    echo -e "${GREEN}✓ 가상환경이 이미 존재합니다${NC}"
fi

# 4. 의존성 설치
echo -e "${YELLOW}[4/8] Python 의존성 설치 중...${NC}"
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
deactivate
echo -e "${GREEN}✓ 의존성 설치 완료${NC}"

# 5. 환경변수 파일 설정
echo -e "${YELLOW}[5/8] 환경변수 파일 설정 중...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  .env 파일을 생성했습니다. 아래 항목을 수정하세요:${NC}"
    echo -e "${RED}   - FIREBASE_CREDENTIALS_PATH${NC}"
    echo -e "${RED}   - FIREBASE_PROJECT_ID${NC}"
    echo -e "${RED}   - FIREBASE_API_KEY${NC}"
    echo -e "${RED}   - UPSTAGE_API_KEY${NC}"
    echo -e "${RED}   - CORS_ORIGINS (도메인)${NC}"
    echo ""
    echo -e "${YELLOW}nano /home/ubuntu/LawRo/backend/.env${NC}"
    echo ""
    echo "수정 후 다시 스크립트를 실행하세요"
    exit 1
else
    echo -e "${GREEN}✓ .env 파일이 이미 존재합니다${NC}"
fi

# 6. 필수 디렉토리 생성
echo -e "${YELLOW}[6/8] 필수 디렉토리 생성 중...${NC}"
mkdir -p data/chroma
mkdir -p storage/contracts
mkdir -p /var/log/lawro
sudo chown ubuntu:ubuntu /var/log/lawro
echo -e "${GREEN}✓ 디렉토리 생성 완료${NC}"

# 7. Systemd 서비스 파일 설정
echo -e "${YELLOW}[7/8] Systemd 서비스 등록 중...${NC}"
sudo cp systemd/lawro-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable lawro-backend
echo -e "${GREEN}✓ Systemd 서비스 등록 완료${NC}"

# 8. Nginx 설정
echo -e "${YELLOW}[8/8] Nginx 설정 중...${NC}"
sudo cp nginx/lawro.conf /etc/nginx/sites-available/lawro
if [ ! -L "/etc/nginx/sites-enabled/lawro" ]; then
    sudo ln -s /etc/nginx/sites-available/lawro /etc/nginx/sites-enabled/lawro
fi
sudo nginx -t
sudo systemctl restart nginx
echo -e "${GREEN}✓ Nginx 설정 완료${NC}"

echo ""
echo -e "${GREEN}======================================"
echo "✅ 배포 준비 완료!"
echo "======================================${NC}"
echo ""
echo "다음 단계:"
echo "1. Firebase 인증 JSON 파일 업로드:"
echo "   scp -i your-key.pem firebase-credentials.json ubuntu@your-ec2-ip:/home/ubuntu/LawRo/backend/"
echo ""
echo "2. 환경변수 수정 (필요시):"
echo "   nano /home/ubuntu/LawRo/backend/.env"
echo ""
echo "3. 서비스 시작:"
echo "   sudo systemctl start lawro-backend"
echo "   sudo systemctl status lawro-backend"
echo ""
echo "4. 로그 확인:"
echo "   tail -f /var/log/lawro/error.log"
echo ""
echo "5. API 접속:"
echo "   http://your-ec2-ip"
echo "   http://your-ec2-ip/docs (Swagger UI)"
