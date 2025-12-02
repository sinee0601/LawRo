# 🚀 EC2 배포 빠른 시작 (5분)

## 사전 준비
- AWS 계정 + EC2 인스턴스 생성 (Ubuntu 22.04)
- Firebase 인증 파일 (`firebase-credentials.json`)
- Upstage API 키

---

## 로컬에서 (1분)

```bash
# 프로젝트 준비
cd backend
git add .
git commit -m "Prepare for EC2 deployment"
git push origin develop
```

---

## EC2에서 (4분)

### 1️⃣ 접속 (30초)
```bash
ssh -i lawro-key.pem ubuntu@your-ec2-ip
```

### 2️⃣ 코드 다운로드 (30초)
```bash
cd /home/ubuntu
git clone https://github.com/your-username/LawRo.git
cd LawRo/backend
```

### 3️⃣ 자동 배포 (2분)
```bash
bash deploy.sh
```

### 4️⃣ Firebase 파일 업로드 (로컬 새 터미널에서 - 30초)
```bash
scp -i lawro-key.pem firebase-credentials.json \
  ubuntu@your-ec2-ip:/home/ubuntu/LawRo/backend/
```

### 5️⃣ 환경변수 설정 (EC2에서 - 1분)
```bash
nano /home/ubuntu/LawRo/backend/.env

# 다음 3개 항목만 수정:
# FIREBASE_PROJECT_ID=your-id
# FIREBASE_API_KEY=your-key
# UPSTAGE_API_KEY=up_your-key

# Ctrl+X → Y → Enter로 저장
```

### 6️⃣ 서비스 시작 (30초)
```bash
sudo systemctl start lawro-backend
sudo systemctl status lawro-backend
```

---

## 완료! 🎉

### API 접속
```
http://your-ec2-ip/docs
```

### 로그 확인
```bash
tail -f /var/log/lawro/error.log
```

---

## 문제 발생 시

```bash
# 서비스 상태 확인
sudo systemctl status lawro-backend

# 에러 로그 확인
tail -100 /var/log/lawro/error.log

# 서비스 재시작
sudo systemctl restart lawro-backend
```

---

## 유용한 명령어

| 명령어 | 설명 |
|--------|------|
| `sudo systemctl start lawro-backend` | 서비스 시작 |
| `sudo systemctl stop lawro-backend` | 서비스 중지 |
| `sudo systemctl restart lawro-backend` | 서비스 재시작 |
| `sudo systemctl status lawro-backend` | 상태 확인 |
| `tail -f /var/log/lawro/error.log` | 에러 로그 (실시간) |
| `journalctl -u lawro-backend -f` | 서비스 로그 (실시간) |
| `curl http://localhost/health` | 헬스 체크 |

---

자세한 가이드는 `DEPLOY.md` 참고!
