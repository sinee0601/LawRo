# ==========================================
# 1️⃣ 로컬 머신에서 파일 전송
# ==========================================

# PEM 키 권한 설정 (첫 1회만)
chmod 400 /path/to/your-key.pem

# Backend 전송
scp -i assq2123123.pem -r backend ubuntu@54.180.142.115:/home/ubuntu/

# Frontend 전송
scp -i assq2123123.pem  -r frontend ubuntu@54.180.142.115:/home/ubuntu/

# Firebase 인증 파일 전송 (필수)
scp -i /path/to/your-key.pem firebase-credentials.json ubuntu@54.180.142.115:/home/ubuntu/backend/


# ==========================================
# 2️⃣ AWS 서버 초기 설정 (SSH 접속)
# ==========================================

ssh -i /path/to/your-key.pem ubuntu@54.180.142.115

# 서버에서:
sudo apt update && sudo apt upgrade -y

# Python & 필수 패키지
sudo apt install -y python3-pip python3-venv python3-dev
sudo apt install -y nginx supervisor curl wget git

# Node.js & npm (Frontend 빌드용)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs


# ==========================================
# 3️⃣ Backend 설정 및 실행
# ==========================================

cd /home/ubuntu/backend

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt

# .env 파일 생성 (Firebase 정보 포함)
nano .env
# 아래 내용 추가:
# FIREBASE_CREDENTIALS_PATH=/home/ubuntu/backend/firebase-credentials.json
# FIREBASE_PROJECT_ID=your-project-id
# FIREBASE_API_KEY=your-api-key
# UPSTAGE_API_KEY=your-upstage-key
# CORS_ORIGINS=http://54.180.142.115,http://localhost:3000


# ==========================================
# 4️⃣ Supervisor로 Backend 서비스화
# ==========================================

sudo nano /etc/supervisor/conf.d/lawro-backend.conf

# 아래 내용 입력:
"""
[program:lawro-backend]
directory=/home/ubuntu/backend
command=/home/ubuntu/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/lawro-backend.log
environment=PATH="/home/ubuntu/backend/venv/bin"
"""

# Supervisor 적용
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start lawro-backend

# 상태 확인
sudo supervisorctl status lawro-backend


# ==========================================
# 5️⃣ Frontend 빌드 및 배포
# ==========================================

cd /home/ubuntu/frontend

# 의존성 설치
npm install

# 프로덕션 빌드
npm run build

# 빌드 결과를 Nginx 웹 루트로 복사
sudo mkdir -p /var/www/lawro
sudo cp -r dist/* /var/www/lawro/
sudo chown -R www-data:www-data /var/www/lawro


# ==========================================
# 6️⃣ Nginx 설정 (Frontend + Backend Proxy)
# ==========================================

sudo nano /etc/nginx/sites-available/lawro

# 아래 내용 입력:
"""
server {
    listen 80;
    server_name 54.180.142.115;

    # Frontend - React SPA
    location / {
        root /var/www/lawro;
        try_files $uri /index.html;
        add_header Cache-Control "no-cache";
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Swagger UI
    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://localhost:8000/openapi.json;
        proxy_set_header Host $host;
    }
}
"""

# Nginx 활성화
sudo ln -s /etc/nginx/sites-available/lawro /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Nginx 재시작
sudo systemctl restart nginx
sudo systemctl enable nginx


# ==========================================
# 7️⃣ 방화벽 설정 (보안 그룹)
# ==========================================

# AWS Security Group에서:
# Inbound Rules:
# - SSH (22): 내 IP에서만 허용
# - HTTP (80): 0.0.0.0/0 (모든 곳)
# - HTTPS (443): 0.0.0.0/0 (선택사항)


# ==========================================
# 8️⃣ 접속 테스트
# ==========================================

# 브라우저에서:
# http://54.180.142.115  → Frontend
# http://54.180.142.115/docs  → Backend Swagger
# http://54.180.142.115/health  → Backend Health Check

# 또는 curl로:
curl http://54.180.142.115/health
curl http://54.180.142.115/docs


# ==========================================
# 9️⃣ 로그 확인
# ==========================================

# Backend 로그
tail -f /var/log/lawro-backend.log

# Nginx 로그
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Supervisor 상태
sudo supervisorctl status


# ==========================================
# 🔄 업데이트 배포
# ==========================================

# 로컬에서 새 파일 전송
scp -i /path/to/your-key.pem -r backend ubuntu@54.180.142.115:/home/ubuntu/

# 서버에서:
cd /home/ubuntu/backend
source venv/bin/activate
pip install -r requirements.txt  # 새 의존성 있으면
sudo supervisorctl restart lawro-backend