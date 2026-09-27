# LawRo 프론트엔드 이미지 (Vite 빌드 → nginx 정적 서빙)

FROM node:20-alpine AS build
WORKDIR /app

# 의존성 레이어를 분리해 소스 변경 시 재설치를 피한다
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY . .

# API 는 같은 오리진의 /api 아래로 프록시된다 (deploy/Caddyfile 참고)
ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
