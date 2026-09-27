#!/usr/bin/env bash
# OCI Ampere A1 (Ubuntu 22.04/24.04) 최초 1회 설정 스크립트
# 사용법: 서버에 ssh 접속 후  bash setup-server.sh
set -euo pipefail

echo "[1/4] Docker 설치"
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sudo sh
fi
sudo usermod -aG docker "$USER"

echo "[2/4] OS 방화벽에서 80/443 개방"
# OCI Ubuntu 이미지는 iptables 에 기본 REJECT 규칙이 있어서
# Security List 만 열어서는 외부 접속이 안 된다
for port in 80 443; do
  sudo iptables -C INPUT -p tcp --dport "$port" -j ACCEPT 2>/dev/null \
    || sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport "$port" -j ACCEPT
done
sudo iptables -C INPUT -p udp --dport 443 -j ACCEPT 2>/dev/null \
  || sudo iptables -I INPUT 6 -p udp --dport 443 -j ACCEPT
sudo apt-get install -y iptables-persistent >/dev/null
sudo netfilter-persistent save

echo "[3/4] 스왑 2GB (빌드/임베딩 순간 메모리 여유용)"
if ! swapon --show | grep -q /swapfile; then
  sudo fallocate -l 2G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab >/dev/null
fi

echo "[4/4] 배포 디렉토리"
mkdir -p ~/lawro

cat <<'EOF'

완료. 다음을 진행하세요:
  1) 로그아웃 후 재접속 (docker 그룹 적용)
  2) ~/lawro/backend.env               ← backend/.env 내용 (운영 값으로)
  3) ~/lawro/firebase-credentials.json ← Firebase 서비스 계정 키
  4) GitHub 에서 deploy 워크플로우 실행 (Actions → deploy → Run workflow)
EOF
