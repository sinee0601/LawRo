EC2 + S3 + CloudFront 배포 가이드
Phase 1: Backend 배포 (EC2)
1-1. EC2 인스턴스 생성
# AWS Console에서:
1. EC2 → Instances → Launch Instance
2. OS: Ubuntu 22.04 LTS (Free tier eligible)
3. Instance Type: t2.micro (프리 티어)
4. Key Pair: 새로 생성 후 저장 (.pem 파일)
5. Security Group: 
   - SSH (22): 귀사 IP만
   - HTTP (80): 0.0.0.0/0
   - HTTPS (443): 0.0.0.0/0
   - 8000 (Backend): 0.0.0.0/0
1-2. EC2 접속 및 환경 설정
# 로컬에서 SSH 접속
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# EC2 인스턴스 내에서:
sudo apt update
sudo apt install -y python3-pip python3-venv git nginx

# 프로젝트 클론
git clone https://github.com/your-repo/LawRo.git
cd LawRo/backend

# Python 가상 환경
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
1-3. 환경 변수 설정 (AWS Secrets Manager 이용)
# EC2 내에서 .env 파일 생성
cat > .env << 'EOF'
APP_NAME=LawRo Unified Backend
APP_VERSION=1.0.0
HOST=0.0.0.0
PORT=8000
DEBUG=false
ENVIRONMENT=production

# Firebase 설정
FIREBASE_CREDENTIALS_PATH=/home/ubuntu/LawRo/backend/firebase-credentials.json
FIREBASE_PROJECT_ID=lawro-8e494
FIREBASE_API_KEY=your_actual_key_here

# JWT
JWT_EXPIRE_HOURS=24
JWT_SECRET_KEY=your_secure_random_key_here

# Upstage AI
UPSTAGE_API_KEY=your_upstage_key_here

# ChromaDB
CHROMA_PERSIST_DIRECTORY=/home/ubuntu/LawRo/backend/data/chroma
CHROMA_COLLECTION_NAME=lawro_legal_docs

# Chat LLM
CHAT_LLM_MODEL=solar-pro2
CHAT_EMBEDDING_MODEL=solar-embedding-1-large-query

# Storage
LOCAL_STORAGE_PATH=/home/ubuntu/LawRo/backend/storage/contracts

# OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_secret
NAVER_CLIENT_ID=your_naver_id
NAVER_CLIENT_SECRET=your_naver_secret

# CORS & Frontend
CORS_ORIGINS=https://your-cloudfront-domain.cloudfront.net,https://your-custom-domain.com
FRONTEND_URL=https://your-custom-domain.com
EOF
1-4. Firebase Credentials 복사
# 로컬에서 EC2로 파일 전송
scp -i your-key.pem /path/to/firebase-credentials.json \
    ubuntu@your-ec2-public-ip:/home/ubuntu/LawRo/backend/

# EC2에서 권한 설정
chmod 600 firebase-credentials.json
1-5. Systemd 서비스 설정
# EC2에서 Systemd 서비스 파일 생성
sudo cat > /etc/systemd/system/lawro-backend.service << 'EOF'
[Unit]
Description=LawRo Backend API
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/LawRo/backend
Environment="PATH=/home/ubuntu/LawRo/backend/venv/bin"
ExecStart=/home/ubuntu/LawRo/backend/venv/bin/gunicorn \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    app.main:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 서비스 시작
sudo systemctl daemon-reload
sudo systemctl enable lawro-backend
sudo systemctl start lawro-backend

# 상태 확인
sudo systemctl status lawro-backend
1-6. Nginx 리버스 프록시 설정
# Nginx 설정
sudo cat > /etc/nginx/sites-available/lawro-backend << 'EOF'
server {
    listen 80;
    server_name your-ec2-public-ip;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
EOF

# 사이트 활성화
sudo ln -s /etc/nginx/sites-available/lawro-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
Phase 2: Frontend 배포 (S3 + CloudFront)
2-1. Frontend 빌드
cd frontend

# .env 업데이트 (production)
cat > .env.production << 'EOF'
VITE_API_URL=https://your-ec2-public-ip:8000
VITE_NAVER_MAP_CLIENT_ID=xvyp5v7zoj
VITE_NAVER_MAP_API_KEY=zecYeWEX9hX803Yq2QRpAeLI75iqNVbzdJ1oIlTo
EOF

# 빌드
npm run build

# dist 폴더 생성 확인
ls -la dist/
2-2. S3 버킷 생성
# AWS Console에서:
1. S3 → Create bucket
2. Bucket name: lawro-frontend-prod
3. ACL: Private
4. Block Public Access: 모두 활성화
5. Versioning: 활성화
6. 생성
2-3. Frontend를 S3에 업로드
# AWS CLI 설치 (로컬)
pip install awscli

# AWS 자격증명 설정
aws configure
# Access Key, Secret Key, Region (ap-northeast-2) 입력

# Frontend 배포
aws s3 sync dist/ s3://lawro-frontend-prod/ --delete
2-4. S3 정적 웹사이트 설정
# AWS Console에서:
1. S3 → lawro-frontend-prod
2. Properties → Static website hosting
3. Enable
4. Index document: index.html
5. Error document: index.html (SPA 라우팅)
6. Save
2-5. S3 버킷 정책 설정 (CloudFront용)
# AWS Console에서:
1. lawro-frontend-prod → Permissions → Bucket Policy
2. 다음 정책 추가:

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontRead",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::lawro-frontend-prod/*",
      "Condition": {
        "StringEquals": {
          "aws:SourceArn": "arn:aws:cloudfront::ACCOUNT-ID:distribution/YOUR-DISTRIBUTION-ID"
        }
      }
    }
  ]
}
Phase 3: CloudFront 배포
3-1. CloudFront Distribution 생성
# AWS Console에서:
1. CloudFront → Create distribution
2. Origin:
   - Origin domain: S3 버킷 선택 (lawro-frontend-prod.s3.amazonaws.com)
   - Origin access: OAC (Origin Access Control) 생성
3. Viewer protocol policy: Redirect HTTP to HTTPS
4. Cache policy: CachingOptimized
5. Create distribution
3-2. Origin Access Control (OAC) 설정
# CloudFront 생성 후:
1. Distribution → Permissions → Origin access
2. OAC 생성
3. S3 버킷 정책 자동 업데이트 (Copy policy 후 S3 정책에 추가)
3-3. CloudFront 캐시 무효화
# AWS Console에서:
1. CloudFront distribution → Invalidations
2. Create invalidation
3. Path: /* (모든 파일)
4. Invalidate
Phase 4: HTTPS 및 도메인 설정
4-1. AWS Certificate Manager (ACM) - SSL 인증서
# AWS Console에서:
1. ACM → Request certificate
2. Domain names: 
   - your-custom-domain.com
   - *.your-custom-domain.com
3. Validation method: DNS validation
4. Email 확인
4-2. Route 53 DNS 설정
# AWS Console에서:
1. Route 53 → Hosted zones
2. your-custom-domain.com 선택
3. Create records:

# Backend (EC2)
Name: api.your-custom-domain.com
Type: A
Value: your-ec2-elastic-ip

# Frontend (CloudFront)
Name: your-custom-domain.com
Type: A
Value: CloudFront distribution domain name
(또는 Alias record로 직접 선택)
4-3. CloudFront에 SSL 연결
# AWS Console에서:
1. CloudFront distribution → Edit
2. Alternate domain names (CNAME):
   - your-custom-domain.com
3. Custom SSL certificate: ACM에서 생성한 인증서 선택
4. Save
4-4. EC2에 Let's Encrypt SSL 설정
# EC2에서:
sudo apt install certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot certonly --nginx -d api.your-custom-domain.com

# Nginx 설정 업데이트
sudo cat > /etc/nginx/sites-available/lawro-backend << 'EOF'
server {
    listen 80;
    server_name api.your-custom-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.your-custom-domain.com;

    ssl_certificate /etc/letsencrypt/live/api.your-custom-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.your-custom-domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo systemctl restart nginx
Phase 5: 환경 변수 최종 수정
Backend .env 업데이트:
CORS_ORIGINS=https://your-custom-domain.com,https://www.your-custom-domain.com
FRONTEND_URL=https://your-custom-domain.com
Frontend .env 업데이트:
VITE_API_URL=https://api.your-custom-domain.com
Phase 6: 배포 후 검증
# Backend 상태 확인
curl https://api.your-custom-domain.com/health

# Frontend 접속
https://your-custom-domain.com

# CloudFront 캐시 확인
# → 첫 방문: Origin에서 가져옴
# → 두 번째 방문: 캐시에서 제공
배포 완료 체크리스트
✅ EC2 인스턴스 생성 및 Backend 배포
✅ S3 버킷 생성 및 Frontend 업로드
✅ CloudFront Distribution 생성
✅ ACM SSL 인증서 발급
✅ Route 53 DNS 설정
✅ EC2 Let's Encrypt SSL 설정
✅ 환경 변수 수정
✅ CORS 설정 완료
✅ 배포 후 모든 기능 테스트
질문이 있거나 특정 단계에서 문제가 발생하면 알려주세요!