# 🚀 최적화된 Contract Analyzer Dockerfile
# 멀티스테이지 빌드로 이미지 크기 최소화

FROM python:3.11-slim as builder

# 빌드 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치 (빌드 스테이지)
COPY requirements_optimized.txt /tmp/
RUN pip install --no-cache-dir --user -r /tmp/requirements_optimized.txt

# 실행 스테이지
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 런타임 의존성만 설치
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 빌드 스테이지에서 설치된 패키지 복사
COPY --from=builder /root/.local /root/.local

# PATH 업데이트
ENV PATH=/root/.local/bin:$PATH

# 애플리케이션 코드 복사
COPY . .

# 불필요한 파일 제거 (이미지 크기 최소화)
RUN rm -rf \
    requirements.txt \
    Dockerfile \
    __pycache__ \
    .git* \
    *.md \
    test* \
    .env*

# 업로드 및 임시 디렉토리 생성
RUN mkdir -p /app/uploads /app/temp

# 포트 8002 노출
EXPOSE 8002

# 헬스체크 최적화 (더 빠른 간격)
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=2 \
    CMD curl -f http://localhost:8002/health || exit 1

# 프로덕션 모드로 실행 (reload 비활성화)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "1"] 