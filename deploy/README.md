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
2. 서브넷의 Security List(또는 NSG) Ingress 에 TCP 80, 443 추가
   - 소스 CIDR `0.0.0.0/0`, **대상 포트 범위** `80` / `443`, **소스 포트 범위는 비워 둔다(모두)**
   - 소스 포트에 80 을 넣으면 클라이언트는 임의 포트에서 출발하므로 모든 요청이 막힌다 (외부에서 타임아웃)
   - VNIC 에 NSG 가 붙어 있으면 NSG 에도 같은 규칙이 필요하다
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

배포 전용 SSH 키를 만들어 서버에 등록한다 (개인 접속 키와 분리해 두면 폐기가 쉽다):

```bash
ssh-keygen -t ed25519 -N "" -C "lawro-github-actions-deploy" -f ~/.ssh/lawro-deploy
ssh ubuntu@<IP> "cat >> ~/.ssh/authorized_keys" < ~/.ssh/lawro-deploy.pub
```

Settings → Environments → **production** 생성 후:

| 종류 | 이름 | 값 |
|---|---|---|
| Secret | `OCI_HOST` | VM 공인 IP |
| Secret | `OCI_USER` | `ubuntu` |
| Secret | `OCI_SSH_KEY` | 배포용 SSH **개인키** 전체 |
| Variable | `SITE_ADDRESS` | `lawro.duckdns.org` 처럼 도메인 (비우면 `http://IP` 로 동작) |

`gh` CLI 로 한 번에 설정할 수도 있다 (개인키가 화면에 찍히지 않는다):

```bash
gh api -X PUT repos/<owner>/<repo>/environments/production
gh secret set OCI_HOST    --env production --body <IP>
gh secret set OCI_USER    --env production --body ubuntu
gh secret set OCI_SSH_KEY --env production < ~/.ssh/lawro-deploy
```

도메인을 쓰면 DNS A 레코드를 VM IP 로 맞춘 뒤 배포하면 Caddy 가 Let's Encrypt 인증서를 자동 발급한다.
이때 서버 `~/lawro/backend.env` 의 `CORS_ORIGINS`, `FRONTEND_URL` 도 `https://<도메인>` 으로 바꾼다.

> `SITE_ADDRESS` 를 비워 두면 compose 가 `:80` 을 기본값으로 넘긴다.
> 빈 문자열이 그대로 Caddy 에 들어가면 Caddyfile 첫 줄이 `{` 가 되어 전역 옵션으로 파싱되고
> `unrecognized global option: encode` 로 기동에 실패한다.

## 3. 배포

- `main` 에 머지되면 자동 배포된다.
- 수동: Actions → **deploy** → Run workflow (이 경우 양쪽 모두 빌드).
  ```bash
  gh workflow run deploy.yml --ref main
  ```
- **첫 배포는 수동으로 실행한다.** 자동 배포는 바뀐 쪽 이미지만 빌드하므로, `deploy/` 만 바뀐 푸시로는
  아무 이미지도 만들어지지 않아 ghcr 에 `latest` 가 없는 상태에서 pull 이 실패한다.

### 배포 확인

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://<IP>/     # 200
curl -s http://<IP>/api/health                             # 모든 서비스 "healthy"
```

서버 안에서는 되는데(`curl http://localhost/`) 밖에서 타임아웃이면 OCI Security List 문제다 (1단계 2번 참고).
밖에서 즉시 "연결 거부"면 Security List 는 통과했고 서버 쪽(컨테이너/방화벽) 문제다.

## 운영 명령

```bash
cd ~/lawro
docker compose ps
docker compose logs -f backend
# 특정 커밋으로 롤백
IMAGE_TAG=<commit-sha> docker compose up -d
```

## ChromaDB 초기 데이터

벡터 DB 는 이미지에 포함되지 않는다. 로컬에서 만든 `data/chroma` 를 볼륨으로 옮긴다.

첫 배포 전이라도 볼륨(`lawro_chroma_data`, compose 프로젝트명 `lawro` 기준)에 미리 넣어 둘 수 있다.
컨테이너 사용자 `lawro` 의 uid 는 10001 이다:

```bash
cd backend/data
tar czf - chroma | ssh ubuntu@<IP> 'docker volume create lawro_chroma_data >/dev/null \
  && docker run --rm -i -v lawro_chroma_data:/data alpine \
     sh -c "rm -rf /data/chroma && tar xzf - -C /data && chown -R 10001:10001 /data"'
```

이미 떠 있는 컨테이너에 넣는 경우:

```bash
scp -r backend/data/chroma ubuntu@<IP>:~/chroma
ssh ubuntu@<IP> 'cd ~/lawro && docker compose cp ~/chroma/. backend:/app/data/chroma \
  && docker compose exec -u root backend chown -R lawro:lawro /app/data \
  && docker compose restart backend'
```

## 방화벽 정리

외부에 열어 둘 포트는 22(SSH), 80, 443 뿐이다. 백엔드 8000 은 Caddy 뒤(`/api`)에 있으므로 외부 규칙이 필요 없다.
OCI Security List 와 서버 iptables 두 곳에서 모두 관리한다.

- **Security List:** 쓰지 않는 Ingress 규칙은 지운다. 막힌 포트는 외부에서 "타임아웃"으로 보인다.
- **iptables:** OCI Ubuntu 이미지는 INPUT 체인 끝에 `REJECT` 가 있어 목록에 없는 포트는 막힌다.
  (`ACCEPT all` 처럼 보이는 줄은 `-i lo` 규칙이다. `iptables -L -n -v` 로 인터페이스까지 확인한다)
  규칙을 지울 때는 `iptables -S INPUT` 에 나온 옵션 순서 그대로 `-D` 해야 매칭된다:
  ```bash
  sudo iptables -S INPUT                       # 현재 규칙 확인
  sudo iptables -D INPUT -p tcp --dport 8000 -m state --state NEW -j ACCEPT   # 예시
  sudo netfilter-persistent save               # 재부팅 후에도 유지
  ```
- Docker 가 publish 한 포트(caddy 80/443)는 Docker 자체 체인으로 처리되어 INPUT 규칙과 무관하다.
  DB 처럼 서버 안에서만 쓰는 컨테이너는 `127.0.0.1:<port>` 로 바인딩하고 SSH 터널로 접근한다.
- 같은 VM 에서 다른 서비스를 함께 돌린다면 그 포트는 정리 대상에서 빼야 한다.
