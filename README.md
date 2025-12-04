# LawRo - 외국인 노동자를 위한 AI 법률 상담 플랫폼

**LawRo**는 대한민국에 거주하는 외국인 노동자들이 겪는 법률적 어려움을 해소하기 위해 설계된 AI 기반 법률 상담 및 계약서 분석 플랫폼입니다. RAG(검색 증강 생성) 기반 챗봇을 통해 법률 및 노동 관련 질문에 답변하고, OCR 기술을 활용하여 근로 계약서를 분석하고 위험 요소를 알려주는 기능을 제공합니다.

## ✨ 주요 기능

- **🤖 AI 법률 상담 챗봇:** Upstage Solar LLM과 RAG 기술을 활용하여, 내장된 법률 문서를 기반으로 정확하고 신뢰도 높은 법률 상담을 제공합니다.
- **📄 계약서 분석:** 스마트폰으로 촬영한 계약서 이미지를 업로드하면, OCR로 텍스트를 추출하고 LLM이 핵심 내용을 요약 및 분석하여 법률적 위험 요소를 알려줍니다.
- **🗂️ 채팅 기록 관리:** Gemini 웹 버전과 같이, 이전 대화 기록이 세션별로 저장되어 언제든지 지난 상담 내용을 확인하고 이어서 대화를 나눌 수 있습니다.
- **🌐 다국어 지원:** 다양한 국적의 사용자를 위해 다국어 질문 및 답변을 지원합니다.

## 🛠️ 기술 스택

| 구분 | 기술 | 설명 |
|---|---|---|
| **Frontend** | React, Vite, Zustand, Tailwind CSS | 사용자 인터페이스 및 상태 관리 |
| **Backend** | FastAPI (Python) | 통합 API 서버 |
| **AI** | Upstage Solar, Upstage Embeddings | LLM 및 임베딩 모델 |
| **Database**| Firestore, ChromaDB | 사용자/세션 데이터 및 벡터DB |
| **Deployment**| Nginx, uvicorn | 리버스 프록시 및 ASGI 서버 |

<br/>

## 📂 프로젝트 구조

```
/
├── backend/              # FastAPI 통합 백엔드
│   ├── app/              # 메인 애플리케이션 로직
│   │   ├── routers/      # API 엔드포인트 라우터
│   │   ├── services/     # 비즈니스 로직 (챗봇, 계약서 분석 등)
│   │   └── config.py     # 애플리케이션 설정
│   ├── data/
│   │   └── chroma/       # ChromaDB 벡터 데이터베이스
│   └── embed_data.py     # 데이터 임베딩 스크립트
│
├── frontend/             # React 프론트엔드
│   ├── src/
│   │   ├── pages/        # 페이지 컴포넌트 (ChatPage, ContractPage 등)
│   │   ├── components/   # 재사용 가능한 컴포넌트
│   │   ├── store/        # Zustand 상태 관리
│   │   └── services/     # API 클라이언트
│   └── vite.config.js    # Vite 설정
│
└── storage/
    └── data/
        ├── raw/          # 원본 PDF 문서 저장 폴더
        ├── processed/    # 1차 가공된 JSON 파일 저장 폴더
        └── data_processing.py # PDF 전처리 스크립트
```

## 🚀 설치 및 실행 방법

### 사전 요구 사항
- Python 3.11+
- Node.js 18+
- (배포 시) Nginx

### 1. 프로젝트 클론
```bash
git clone https://github.com/your-repository/LawRo.git
cd LawRo
```

### 2. 백엔드 설정
1.  **가상 환경 생성 및 활성화 (권장)**
    ```bash
    python -m venv venv
    source venv/Scripts/activate  # Windows
    # source venv/bin/activate    # macOS/Linux
    ```
2.  **필요 패키지 설치**
    ```bash
    pip install -r backend/requirements.txt
    ```
3.  **`.env` 파일 생성**
    -   프로젝트 최상위 폴더(`LawRo/`)에 `.env` 파일을 생성합니다.
    -   아래 내용을 복사하여 붙여넣고, `UPSTAGE_API_KEY` 등 본인의 환경에 맞게 값을 수정합니다. Firebase 관련 키도 필요합니다.
      ```dotenv
      # .env
      UPSTAGE_API_KEY="up_..."
      FIREBASE_CREDENTIALS_PATH="firebase-credentials.json"
      # ... 기타 필요한 설정값들 ...
      CHAT_RETRIEVAL_SCORE_THRESHOLD=0.4
      ```
4.  **Firebase 인증 설정**
    -   Firebase 프로젝트에서 발급받은 서비스 계정 키 파일의 이름을 `firebase-credentials.json`으로 변경하여 프로젝트 최상위 폴더에 위치시킵니다.

### 3. 프론트엔드 설정
```bash
cd frontend
npm install
```

### 4. 데이터 준비 및 임베딩 (매우 중요!)
챗봇이 법률 문서를 참고하여 답변하게 하려면, 로컬 벡터 데이터베이스(ChromaDB)를 구축해야 합니다.

1.  **PDF 준비:**
    -   챗봇의 지식 기반이 될 PDF 법률 문서들을 `storage/data/raw` 폴더에 넣습니다.

2.  **PDF 전처리 (PDF -> JSON):**
    -   프로젝트 최상위 폴더에서 아래 명령어를 실행합니다. `raw` 폴더의 모든 PDF가 `processed` 폴더에 JSON 파일로 변환됩니다.
    ```bash
    python storage/data/data_processing.py
    ```

3.  **데이터 임베딩 (JSON -> ChromaDB):**
    -   전처리가 완료되면, 아래 명령어를 실행하여 JSON 파일들을 임베딩하고 ChromaDB에 저장합니다.
    ```bash
    python backend/embed_data.py
    ```

### 5. 애플리케이션 실행 (개발 모드)
두 개의 터미널을 열고 각각 다음을 실행합니다.

-   **터미널 1 (백엔드):**
    ```bash
    uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
-   **터미널 2 (프론트엔드):**
    ```bash
    cd frontend
    npm run dev
    ```
-   이제 웹 브라우저에서 `http://localhost:5173`으로 접속합니다.

##  배포 (Nginx 리버스 프록시)

개발 환경을 외부 인터넷에 공개하고 HTTPS를 적용하려면 Nginx를 리버스 프록시로 사용하는 것이 가장 좋습니다.

1.  **Nginx 설치 및 SSL 인증서 발급:** `win-acme` 등의 ACME 클라이언트를 사용하여 Let's Encrypt 인증서를 발급받습니다.
2.  **`nginx.conf` 설정:** Nginx가 443(HTTPS) 포트로 들어오는 요청을 받아, 경로에 따라 프론트엔드(`localhost:5173`) 또는 백엔드(`localhost:8000`)로 전달하도록 설정합니다.
3.  **포트 포워딩:** 공유기에서 외부 80, 443 포트를 Nginx가 실행되는 PC로 포워딩합니다.
4.  **DNS 설정:** 구매한 도메인의 A 레코드를 서버의 공인 IP 주소로 향하게 합니다.

## 라이선스
이 프로젝트는 MIT 라이선스 하에 있습니다.