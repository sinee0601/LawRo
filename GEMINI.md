# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# LawRo - AI Legal Consultation Platform for Foreign Workers

## 개요
외국인 노동자를 위한 AI 기반 법률 상담 및 계약서 분석 플랫폼. RAG 기반 챗봇과 OCR 기반 계약서 분석을 통해 법률 정보를 제공합니다.

## 기술 스택
- **Frontend**: React 19, Vite, React Router v7, Zustand, TanStack Query, Tailwind CSS, Axios
- **Backend**: FastAPI, Firebase Firestore, ChromaDB, Upstage Solar AI
- **Storage**: Local file storage (contracts), Firestore (sessions, analysis)
- **AI**: Upstage Solar Pro 2 (LLM), Solar Embedding (RAG), Upstage Document OCR

## 프로젝트 구조

```
/backend          - Unified FastAPI backend (auth + chatbot + contract analysis)
  /app
    /routers      - API route handlers (auth.py, chat.py, contract.py)
    /services     - Business logic (chat_service.py, contract_service.py)
    /models       - Pydantic request/response models
    /utils        - Utility functions
  /data/chroma    - ChromaDB vector database (chroma.sqlite3)
  /prompts        - AI prompt templates (analysis_request_template.txt)
  /storage        - Local contract file storage

/frontend         - React SPA with mobile-first design
  /src
    /pages        - Page components (LoginPage, ChatPage, ContractPage, etc.)
    /components   - Reusable components (BottomNav, MobileHeader)
    /store        - Zustand stores (authStore, chatStore)
    /services     - API client (api.js)

/chatbot_service, /contract_parser, /main_service - DEPRECATED (사용 안 함)
```

## 핵심 파이프라인

### 1. RAG 챗봇 (backend/app/services/chat_service.py)
**흐름**: 사용자 질문 → ChromaDB 벡터 검색 (K=2) → RAG context 생성 → Solar Pro 2 LLM → 응답 반환

**핵심 구성요소**:
- **Vector DB**: `backend/data/chroma/chroma.sqlite3` (lawro_legal_docs collection)
- **Embedding**: solar-embedding-1-large-query
- **LLM**: solar-pro2 (일반 상담), solar-pro (계약서 분석)
- **Session**: Firestore + in-memory 2-tier cache (5분 timeout, 최대 50개 메시지)
- **Custom Prompt**: 계약서 분석 시 analysis_request_template.txt 주입

**주요 메서드**:
- `process_message()` - 메시지 처리 with RAG
- `_call_llm_with_retry()` - LLM API 호출 (3회 재시도)
- `_build_system_prompt()` - System prompt 생성 (custom prompt 지원)

### 2. 계약서 분석 (backend/app/services/contract_service.py)
**흐름**: 파일 업로드 → 로컬 저장 → OCR (Upstage) → 구조 파싱 (Solar Pro) → 챗봇 분석 (custom prompt) → 위험 탐지 → Firestore 저장

**단계별 처리**:
1. `upload_contract_files()` - 로컬 스토리지 저장 (`./storage/contracts/{user_id}/{contract_id}/`)
2. `_process_ocr()` - Upstage Document OCR API로 텍스트 추출
3. `_parse_with_solar()` - Solar Pro로 JSON 구조화 (계약 유형, 당사자, 기간, 주요 조건, 위험 요소)
4. `_analyze_with_chatbot()` - ChatService 재사용, custom prompt로 법률 분석
5. `_save_analysis()` - Firestore 캐싱 (재분석 시 saved data 우선 사용)

**출력 데이터 구조**:
```python
{
  "contract_type": str,
  "parties": {"party_a": str, "party_b": str},
  "effective_date": str,
  "termination_date": str,
  "key_terms": [str],
  "payment_terms": str,
  "special_conditions": [str],
  "risks": [str],  # 법률적 위험 요소
  "extracted_text": str  # OCR 원본 텍스트
}
```

## 명령어

### Backend
```bash
cd backend

# 로컬 실행
pip install -r requirements.txt
uvicorn app.main:app --reload  # http://localhost:8000

# Docker 실행
docker-compose up --build

# 테스트
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Swagger UI
```

### Frontend
```bash
cd frontend

# 개발 서버 실행
npm install
npm run dev  # http://localhost:5173

# 빌드
npm run build
npm run preview

# Lint
npm run lint
```

## API 엔드포인트

### Backend (Port 8000)

**인증** (`/auth`)
- `POST /auth/signup` - 회원가입 (email/password)
- `POST /auth/login` - 로그인
- `GET /auth/profile` - 프로필 조회 (JWT 필요)
- `POST /auth/google/callback` - Google OAuth
- `POST /auth/kakao/callback` - Kakao OAuth
- `POST /auth/naver/callback` - Naver OAuth

**챗봇** (`/chat`)
- `POST /chat/send` - 메시지 전송 (RAG)
- `GET /chat/history/{session_id}` - 히스토리 조회
- `POST /chat/new-session` - 새 세션 생성
- `DELETE /chat/history/{session_id}` - 히스토리 삭제
- `POST /chat/batch` - 배치 메시지 (병렬 처리)

**계약서 분석** (`/contract`)
- `POST /contract/api/upload` - 파일 업로드 (multipart/form-data)
- `POST /contract/api/analyze-with-chatbot` - 전체 분석 파이프라인
- `GET /contract/api/chatbot-status` - 챗봇 상태 확인

### Frontend API 클라이언트 (src/services/api.js)

```javascript
// 챗봇
chatAPI.createSession()
chatAPI.sendMessage(sessionId, message, customPrompt, language)
chatAPI.getHistory(sessionId)

// 계약서
contractAPI.uploadContract(file, onProgress, userId, language)
contractAPI.analyzeWithChatbot(contractId, userId, language)
```

## 환경 설정

### Backend (.env)
```bash
# Firebase
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_API_KEY=your-api-key

# AI API
UPSTAGE_API_KEY=up_xxx  # Solar LLM + OCR

# Storage
LOCAL_STORAGE_PATH=./storage/contracts

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./data/chroma
CHROMA_COLLECTION_NAME=lawro_legal_docs

# LLM 설정
CHAT_LLM_MODEL=solar-pro2
CHAT_EMBEDDING_MODEL=solar-embedding-1-large-query
CHAT_RETRIEVAL_K=2
CHAT_RETRIEVAL_SCORE_THRESHOLD=0.5

# Session
SESSION_BACKEND=firestore  # or "memory"
CHAT_MAX_SESSIONS=1000
CHAT_SESSION_TIMEOUT=300
```

### Frontend
```bash
VITE_API_BASE_URL=http://localhost:8000
```

## 아키텍처 특이사항

### 1. Session Management (2-tier cache)
- **In-memory**: 빠른 응답, 최대 1000 세션, 5분 timeout
- **Firestore**: 영구 저장, in-memory 만료 시 자동 로드
- **Cleanup**: Background thread로 1분마다 expired session 삭제

### 2. Custom Prompt Injection
계약서 분석 시 `backend/prompts/analysis_request_template.txt` 템플릿을 사용하여 챗봇에게 구조화된 분석 요청:
- Template에서 `{{context}}`, `{{language_instruction}}` 치환
- ChatService의 `process_message(custom_prompt=...)` 사용
- Custom prompt 사용 시 RAG 검색 비활성화 (문맥은 이미 포함됨)

### 3. Frontend State Management
- **authStore.js**: 로그인 상태, JWT 토큰 관리
- **chatStore.js**: 세션별 메시지 히스토리, 로딩 상태, 에러 처리, 성공률 통계

### 4. Error Handling & Retry
- **Backend**: Exponential backoff (3회 재시도), RateLimitError/APIConnectionError 처리
- **Frontend**: Axios interceptor로 JWT 자동 주입, 401 시 자동 로그아웃

## 주의사항

### Frontend 수정 시
- **ContractPage.jsx**: 분석 결과는 실제 `result.structured_result`, `result.chatbot_analysis` 데이터를 사용 (하드코딩 금지)
- **api.js**: `contractAPI.analyzeWithChatbot()`는 전체 파이프라인을 한 번에 실행 (업로드 후 별도 호출 필요)
- **BottomNav**: 모든 protected 페이지에 포함 (ContractPage, ChatPage, StatisticsPage, WorkTimePage, SettingsPage)

### Backend 수정 시
- **Prompt Template**: 다중 경로 탐색 (backend/prompts/, prompts/, contract_parser/prompts/)
- **ChromaDB**: `chroma.sqlite3` 파일 삭제 금지 (벡터 DB 초기화됨)
- **Session**: Custom prompt 사용 시 `used_custom_prompt` 플래그로 추적, 다음 메시지에서 자동 리셋

### AI 모델 선택
- **일반 챗봇**: solar-pro2 (구조화 출력 우수)
- **계약서 파싱**: solar-pro (JSON 추출)
- **OCR**: Upstage Document OCR API
- **Embedding**: solar-embedding-1-large-query

## 디자인 시스템 (Frontend)
- **Color**: Material Design Blue palette (primary-50 ~ primary-900, #0d47a1)
- **Layout**: Mobile-first, max-w-md, rounded-3xl cards
- **Navigation**: Bottom nav (fixed, 5 tabs)
- **Icons**: lucide-react

## Firebase 구조
```
Firestore Collections:
- users: 사용자 정보
- chat_sessions: 챗봇 세션 (messages 배열 포함)
- contract_analysis: 계약서 분석 결과 (캐싱)
```

## 개발 모드 디버깅
```bash
# Backend 로그 레벨
DEBUG=true  # config.py에서 설정

# ChatService 상태 확인
curl http://localhost:8000/chat/health

# Contract Service 상태 확인
curl http://localhost:8000/contract/health

# Firestore 데이터 확인
Firebase Console > Firestore Database
```