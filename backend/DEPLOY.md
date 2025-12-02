# LawRo Backend EC2 배포 가이드

## 📋 사전 준비사항

1. **AWS 계정** - EC2 인스턴스 생성 권한
2. **Firebase 인증 파일** - `firebase-credentials.json`
3. **API 키들**:
   - FIREBASE_API_KEY
   - UPSTAGE_API_KEY
4. **EC2 키페어** - 접속용 PEM 파일
5. **도메인** (선택사항, SSL 적용 시)

---

## 🚀 배포 단계

### 단계 1️⃣: AWS EC2 인스턴스 생성

**AWS Console에서:**
1. EC2 대시보드 → 인스턴스 시작
2. **AMI 선택**: Ubuntu 22.04 LTS (Free tier eligible)
3. **인스턴스 타입**: `t3.small` (또는 t3.micro)
4. **스토리지**: 30GB EBS (gp2)
5. **보안 그룹 설정**:
   - SSH (22) - 내 IP에서만
   - HTTP (80) - 모든 곳 (0.0.0.0/0)
   - HTTPS (443) - 모든 곳 (0.0.0.0/0)

**생성 후:**
- 퍼블릭 IP 주소 확인
- 키페어 다운로드 (`lawro-key.pem`)

---

### 단계 2️⃣: EC2 접속

```bash
# 터미널에서 (로컬)
chmod 400 lawro-key.pem
ssh -i lawro-key.pem ubuntu@your-ec2-public-ip

# 또는 SSH 설정 파일에 추가
cat >> ~/.ssh/config << EOF
Host lawro-ec2
    HostName your-ec2-public-ip
    User ubuntu
    IdentityFile ~/.ssh/lawro-key.pem
EOF

ssh lawro-ec2
```

---

### 단계 3️⃣: 코드 다운로드 및 배포 스크립트 실행

```bash
# EC2 인스턴스에서
cd /home/ubuntu

# GitHub에서 클론
git clone https://github.com/your-username/LawRo.git
cd LawRo/backend

# 배포 스크립트 실행 (자동화)
bash deploy.sh
```

**스크립트 실행 시 자동으로:**
- ✅ 시스템 업데이트
- ✅ 필수 패키지 설치 (Python, Nginx 등)
- ✅ 가상환경 생성
- ✅ Python 의존성 설치
- ✅ 디렉토리 생성
- ✅ Systemd 서비스 등록
- ✅ Nginx 설정

---

### 단계 4️⃣: Firebase 인증 파일 업로드

**로컬 터미널에서** (새 터미널 열기):
```bash
# firebase-credentials.json 파일이 있는 디렉토리로 이동
cd /path/to/firebase/creds

# EC2에 업로드
scp -i lawro-key.pem firebase-credentials.json \
  ubuntu@your-ec2-public-ip:/home/ubuntu/LawRo/backend/
```

---

### 단계 5️⃣: 환경변수 설정

**EC2에서:**
```bash
cd /home/ubuntu/LawRo/backend

# .env 파일 수정
nano .env
```

**필수 수정 항목:**
```bash
# Firebase
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json  # 이미 설정됨
FIREBASE_PROJECT_ID=your-actual-project-id           # ✏️ 수정 필요
FIREBASE_API_KEY=your-actual-api-key                 # ✏️ 수정 필요

# Upstage
UPSTAGE_API_KEY=up_your_actual_key                   # ✏️ 수정 필요

# 도메인 (선택사항)
CORS_ORIGINS=http://your-ec2-ip,https://your-domain.com
```

**저장:** `Ctrl+X` → `Y` → `Enter`

---

### 단계 6️⃣: 서비스 시작 및 확인

```bash
# 서비스 시작
sudo systemctl start lawro-backend

# 상태 확인
sudo systemctl status lawro-backend

# 자동 시작 활성화 (이미 deploy.sh에서 설정됨)
sudo systemctl enable lawro-backend

# 로그 확인
tail -50 /var/log/lawro/error.log
tail -f /var/log/lawro/error.log  # 실시간 확인
```

---

### 단계 7️⃣: API 접속 테스트

**브라우저에서:**
```
http://your-ec2-public-ip/docs       # Swagger UI
http://your-ec2-public-ip/health     # 헬스 체크
```

**또는 curl로:**
```bash
curl http://your-ec2-public-ip/health
curl http://your-ec2-public-ip/docs
```

---

### 단계 8️⃣: SSL 설정 (선택사항, 권장)

도메인이 있다면:

```bash
# Certbot 설치
sudo apt install -y certbot python3-certbot-nginx

# SSL 인증서 자동 설정
sudo certbot --nginx -d your-domain.com

# 갱신 테스트
sudo certbot renew --dry-run
```

**Nginx 설정이 자동으로 HTTPS로 업그레이드됩니다.**

---

## 📊 모니터링 및 관리

### 서비스 관리

```bash
# 서비스 시작/중지/재시작
sudo systemctl start lawro-backend
sudo systemctl stop lawro-backend
sudo systemctl restart lawro-backend

# 로그 확인
journalctl -u lawro-backend -f              # 실시간
journalctl -u lawro-backend -n 100          # 최근 100줄
journalctl -u lawro-backend --since today   # 오늘의 로그
```

### 로그 파일

```bash
# 접근 로그
tail -f /var/log/lawro/access.log

# 에러 로그
tail -f /var/log/lawro/error.log

# Nginx 로그
tail -f /var/log/nginx/lawro_error.log
tail -f /var/log/nginx/lawro_access.log
```

### 리소스 모니터링

```bash
# CPU/메모리 사용량
top

# 디스크 사용량
df -h

# 포트 확인
sudo lsof -i :80
sudo lsof -i :8000
```

---

## 🔄 배포 업데이트

최신 코드로 업데이트하려면:

```bash
cd /home/ubuntu/LawRo/backend

# 코드 가져오기
git pull origin develop

# 의존성 업데이트 (필요시)
source venv/bin/activate
pip install -r requirements.txt

# 서비스 재시작
sudo systemctl restart lawro-backend

# 로그 확인
tail -f /var/log/lawro/error.log
```

---

## 🐛 트러블슈팅

### 1. "Permission denied" 에러

```bash
# 디렉토리 권한 확인
ls -la /var/log/lawro
ls -la /home/ubuntu/LawRo

# 필요시 권한 변경
sudo chown -R ubuntu:ubuntu /var/log/lawro
```

### 2. "Address already in use" 에러

```bash
# 포트 사용 확인
sudo lsof -i :8000
sudo lsof -i :80

# 기존 프로세스 종료
sudo kill -9 <PID>
```

### 3. "ModuleNotFoundError"

```bash
# 가상환경 활성화 확인
source /home/ubuntu/LawRo/backend/venv/bin/activate

# 의존성 재설치
pip install -r requirements.txt
```

### 4. Firebase 연결 오류

```bash
# 인증 파일 위치 확인
ls -la /home/ubuntu/LawRo/backend/firebase-credentials.json

# .env 파일의 경로 확인
cat /home/ubuntu/LawRo/backend/.env | grep FIREBASE
```

### 5. 서비스 시작 안 됨

```bash
# 상태 확인 (상세)
sudo systemctl status lawro-backend -l

# 로그 확인
journalctl -u lawro-backend -n 50

# 수동 실행 (디버그)
cd /home/ubuntu/LawRo/backend
source venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

---

## 📈 성능 최적화

### Gunicorn 워커 수 조정

```bash
# systemd 서비스 파일 수정
sudo nano /etc/systemd/system/lawro-backend.service

# workers 값 변경 (CPU 코어 수 * 2 + 1이 일반적)
# t3.small = 2 코어 → 5 워커
# t3.medium = 2 코어 → 5 워커

# 변경 후
sudo systemctl daemon-reload
sudo systemctl restart lawro-backend
```

### Nginx 캐싱 설정

필요시 `/etc/nginx/sites-available/lawro` 수정

---

## ✅ 배포 체크리스트

- [ ] EC2 인스턴스 생성 (Ubuntu 22.04)
- [ ] 보안 그룹 설정 (80, 443, 22 포트)
- [ ] 코드 클론: `git clone ...`
- [ ] 배포 스크립트 실행: `bash deploy.sh`
- [ ] Firebase 파일 업로드: `scp ...`
- [ ] 환경변수 설정: `nano .env`
- [ ] 서비스 시작: `sudo systemctl start lawro-backend`
- [ ] API 접속 테스트: `curl http://ip/health`
- [ ] 로그 확인: 에러 없음
- [ ] 도메인 연결 (선택사항)
- [ ] SSL 설정 (선택사항)

---

## 🆘 추가 도움

에러가 발생하면:

1. **로그 확인**
   ```bash
   tail -100 /var/log/lawro/error.log
   journalctl -u lawro-backend -n 50
   ```

2. **설정 검증**
   ```bash
   cat /home/ubuntu/LawRo/backend/.env
   ls -la /home/ubuntu/LawRo/backend/firebase-credentials.json
   ```

3. **수동 실행으로 디버그**
   ```bash
   cd /home/ubuntu/LawRo/backend
   source venv/bin/activate
   python -m uvicorn app.main:app --reload
   ```

---

**문제 해결이 안 되면 로그 전체를 공유하세요!**
