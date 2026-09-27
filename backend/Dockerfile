# LawRo 통합 백엔드 이미지
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 일부 패키지가 소스 빌드로 떨어질 때를 대비한 최소 빌드 도구
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# 의존성 레이어를 분리해 소스 변경 시 재설치를 피한다
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app ./app
COPY prompts ./prompts

# 비root 실행. 볼륨 마운트 지점을 미리 만들어 named volume 이 소유권을 이어받게 한다
RUN useradd --create-home --uid 10001 lawro \
    && mkdir -p data/chroma storage/contracts \
    && chown -R lawro:lawro /app
USER lawro

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
