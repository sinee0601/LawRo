# OCI 프리티어 배포

## 구성

```
GitHub (main push)
  ├─ backend 변경 → ci.yml (ruff, pytest, docker build) ─┐
  ├─ frontend 변경 → frontend-ci.yml (eslint, vite build) ┤
  │                                                       ▼
  ├─ arm64 이미지 빌드 → ghcr.io/<owner>/lawro-{backend,frontend}:{sha,latest}
  └─ SSH → OCI VM: docker compose pull && up -d

OCI VM (Ampere A1, Always Free)
  caddy :80/:443 ── /api/*  → backend:8000  (프리픽스 제거)
                 └─ 그 외   → frontend:80   (nginx, SPA)
```

- 변경된 쪽만 검증·빌드하고, 배포는 두 이미지의 `latest` 를 함께 올린다.
- 프론트는 `VITE_API_URL=/api` 로 빌드된다. SPA 경로(`/chat`, `/contract`)와 API 경로가 겹쳐서 `/api` 로 분리했다.
- 운영 시크릿(`backend.env`, `firebase-credentials.json`)은 **서버에만** 두고 CI 에는 넣지 않는다.
- ChromaDB 데이터와 업로드된 계약서는 named volume(`chroma_data`, `contract_storage`)에 남아 재배포해도 유지된다.

## 1. OCI 인스턴스 만들기

1. Compute → Instances → Create
   - Image: **Canonical Ubuntu 24.04**
   - Shape: **VM.Standard.A1.Flex** (Ampere) — Always Free 한도는 합계 4 OCPU / 24GB. 예: 2 OCPU / 12GB
   - SSH 공개키 등록 (배포 전용 키를 새로 만드는 것을 권장)
2. 서브넷의 Security List(또는 NSG) Ingress 에 TCP 80, 443 추가 (source `0.0.0.0/0`)
3. 서버 접속 후 초기화:
   ```bash
   scp deploy/setup-server.sh ubuntu@<IP>:~
   ssh ubuntu@<IP> 'bash setup-server.sh'
   ```
4. 시크릿 파일 업로드:
   ```bash
   scp backend/.env ubuntu@<IP>:~/lawro/backend.env
   scp backend/firebase-credentials.json ubuntu@<IP>:~/lawro/
   ```
   `backend.env` 에서 운영 값 확인: `CORS_ORIGINS`, `FRONTEND_URL`(=`https://<도메인>`), `JWT_SECRET_KEY`, `DEBUG=false`.

> A1 인스턴스는 "Out of capacity" 로 생성이 실패하는 일이 잦다. 다른 AD 를 고르거나 시간을 두고 재시도한다.
> Always Free 인스턴스가 7일간 CPU/네트워크/메모리 사용률이 매우 낮으면 회수될 수 있다. 계정을 Pay As You Go 로 전환하면(프리티어 범위 안에서는 과금 없음) 회수 대상에서 빠진다.

## 2. GitHub 설정

Settings → Environments → **production** 생성 후:

| 종류 | 이름 | 값 |
|---|---|---|
| Secret | `OCI_HOST` | VM 공인 IP |
| Secret | `OCI_USER` | `ubuntu` |
| Secret | `OCI_SSH_KEY` | 배포용 SSH **개인키** 전체 |
| Variable | `SITE_ADDRESS` | `lawro.duckdns.org` 처럼 도메인 (비우면 `http://IP` 로 동작) |

도메인을 쓰면 DNS A 레코드를 VM IP 로 맞춘 뒤 배포하면 Caddy 가 Let's Encrypt 인증서를 자동 발급한다.

## 3. 배포

- `main` 에 머지되면 자동 배포된다.
- 수동: Actions → **deploy** → Run workflow (이 경우 양쪽 모두 빌드).

## 운영 명령

```bash
cd ~/lawro
docker compose ps
docker compose logs -f backend
# 특정 커밋으로 롤백
IMAGE_TAG=<commit-sha> docker compose up -d
```

## ChromaDB 초기 데이터

벡터 DB 는 이미지에 포함되지 않는다. 로컬에서 만든 `data/chroma` 를 볼륨으로 옮긴다:

```bash
scp -r backend/data/chroma ubuntu@<IP>:~/chroma
ssh ubuntu@<IP> 'cd ~/lawro && docker compose cp ~/chroma/. backend:/app/data/chroma \
  && docker compose exec -u root backend chown -R lawro:lawro /app/data \
  && docker compose restart backend'
```
