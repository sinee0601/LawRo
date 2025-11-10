# 🚀 LawRo 파이프라인 빠른 수정 가이드

## 📋 체크리스트

### Issue 1: Contract Upload FormData 필드 누락
**파일**: `frontend/src/services/api.js`

❌ **현재** (라인 204):
```javascript
const uploadContract = (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append("file", file);
```

✅ **수정**:
```javascript
const uploadContract = (file, onUploadProgress, userId, language = "korean") => {
    const formData = new FormData();
    formData.append("user_id", userId);           // NEW
    formData.append("language", language);        // NEW
    formData.append("files", file);               // Changed from "file" to "files"
```

---

### Issue 2: analyzeWithChatbot 요청 필드 누락
**파일**: `frontend/src/services/api.js`

❌ **현재** (라인 220-230):
```javascript
const analyzeWithChatbot = (contractId) => {
    return api.post("/api/analyze-with-chatbot", {
        contract_id: contractId
    });
};
```

✅ **수정**:
```javascript
const analyzeWithChatbot = (contractId, userId, language = "korean") => {
    return api.post("/contract/api/analyze-with-chatbot", {
        user_id: userId,              // NEW
        contract_id: contractId,
        use_chatbot: true,            // NEW
        user_language: language,      // NEW
        use_saved_data: true          // NEW
    });
};
```

---

### Issue 3: ContractPage에서 userId 전달 필요
**파일**: `frontend/src/pages/ContractPage.jsx`

❌ **현재** (라인 67):
```javascript
const uploadData = await contractAPI.uploadContract(
    file,
    (percent) => {
        console.log(`Upload progress: ${percent}%`);
    }
);
```

✅ **수정**:
```javascript
const uploadData = await contractAPI.uploadContract(
    file,
    (percent) => {
        console.log(`Upload progress: ${percent}%`);
    },
    userId,                  // NEW
    userLanguage || "korean" // NEW
);
```

그리고:

❌ **현재** (라인 73):
```javascript
const analysisData = await contractAPI.analyzeWithChatbot(contractId);
```

✅ **수정**:
```javascript
const analysisData = await contractAPI.analyzeWithChatbot(
    contractId,
    userId,                  // NEW
    userLanguage || "korean" // NEW
);
```

---

## 🔍 ContractPage에서 필요한 상태 변수 확인

ContractPage.jsx 에서 `userId`와 `userLanguage` 변수가 있는지 확인하세요:

```javascript
const userId = useAuth().user?.uid;  // Firebase UID
const userLanguage = useAuth().user?.language || "korean";  // 사용자 언어 설정
```

만약 없다면 다음과 같이 추가:

```javascript
import { useAuth } from "../store/authStore";  // 또는 Firebase hook

export default function ContractPage() {
    const auth = useAuth();
    const userId = auth.user?.id || auth.user?.uid;
    const userLanguage = localStorage.getItem("userLanguage") || "korean";

    // ... 나머지 코드
}
```

---

## ✅ 수정 후 테스트

### 테스트 시나리오

1️⃣ **파일 업로드 테스트**
```
1. ContractPage에 로그인
2. 계약서 이미지 선택
3. "분석 시작" 클릭
4. 파일 업로드 진행률 확인 (0-100%)
5. 업로드 완료 대기
```

✅ **성공 기준**:
- 네트워크 탭에서 FormData가 `user_id`, `language`, `files` 포함
- 응답에서 `contract_id` 수신

---

2️⃣ **계약서 분석 테스트**
```
1. 파일 업로드 완료 후
2. "분석 중..." 메시지 표시
3. 약 20-30초 대기
4. 분석 결과 표시
```

✅ **성공 기준**:
- 네트워크 탭에서 POST body가 `user_id`, `contract_id`, `use_chatbot`, `user_language`, `use_saved_data` 포함
- 응답에서 `structured_result`, `chatbot_analysis`, `risks` 포함
- UI에 계약 정보, AI 분석, 위험 요소 모두 표시

---

3️⃣ **에러 처리 테스트**
```
1. 잘못된 파일 형식 선택 (예: .txt)
2. 매우 큰 파일 선택 (10MB 이상)
3. API 키 없이 실행
```

✅ **성공 기준**:
- 사용자 친화적 에러 메시지 표시
- 재시도 버튼 제공

---

## 📊 Backend 엔드포인트 확인

### 1. Upload Endpoint
```
POST /contract/api/upload

Request (FormData):
- user_id: string
- language: string (default: "korean")
- files: File[]

Response:
{
    "message": "파일 업로드 성공",
    "contract_id": "uuid",
    "uploaded_files": ["file1.jpg"],
    "s3_urls": ["local://..."]
}
```

### 2. Analyze Endpoint
```
POST /contract/api/analyze-with-chatbot

Request (JSON):
{
    "user_id": "uuid",
    "contract_id": "uuid",
    "use_chatbot": true,
    "user_language": "korean",
    "use_saved_data": true
}

Response:
{
    "message": "계약서 분석 및 법률 상담 완료",
    "structured_result": {
        "contract_type": "근로계약서",
        "parties": "...",
        "contract_period": "...",
        "payment_terms": "..."
    },
    "chatbot_analysis": {
        "totalScore": 85,
        "aware": "양호",
        "summary": "...",
        "highlights": [...],
        "legalInterpretation": [...],
        "deepAnalysis": "..."
    },
    "session_id": "uuid",
    "data_source": "fresh_ocr"
}
```

---

## 🔧 디버깅 팁

### 브라우저 DevTools 확인

1️⃣ **Network 탭**
```
1. F12 → Network 탭
2. Upload/Analyze 요청 클릭
3. Request Headers 확인:
   - Authorization: Bearer {token}
   - Content-Type: application/json (또는 multipart/form-data)
4. Request Body 확인:
   - FormData: user_id, language, files
   - JSON: user_id, contract_id, use_chatbot, ...
5. Response Status 확인:
   - 200 OK ✅
   - 400 Bad Request ❌
   - 401 Unauthorized ❌
   - 500 Server Error ❌
```

2️⃣ **Console 탭**
```
에러 메시지 확인:
- "user_id is required" → FormData에 user_id 누락
- "API key suspended" → Upstage 계정 크레딧 부족
- "CORS error" → 백엔드 CORS 설정 확인
```

3️⃣ **Application 탭**
```
localStorage 확인:
- token: JWT 토큰
- userLanguage: 사용자 언어
- userId: 사용자 ID
```

---

## 🚨 Common Issues & Solutions

### 문제 1: 400 Bad Request - "user_id is required"
**원인**: FormData에 user_id 필드 누락
**해결**: Issue 1 수정 적용

### 문제 2: 401 Unauthorized
**원인**: 인증 토큰 없음 또는 만료
**해결**: 다시 로그인하여 새 토큰 받기

### 문제 3: 429 Too Many Requests
**원인**: API 요청 제한
**해결**: 30초 대기 후 재시도

### 문제 4: 500 Internal Server Error - "OCR failed"
**원인**: Upstage API 크레딧 부족
**해결**: Upstage 계정에서 크레딧 확인

### 문제 5: 빈 응답 또는 "N/A"
**원인**: OCR이 제대로 작동하지 않음
**해결**:
- 더 선명한 이미지 사용
- PDF 대신 JPG/PNG 사용
- 이미지 크기 확인

---

## 📈 성능 기준

| 단계 | 예상 시간 | 기준 |
|------|---------|------|
| 파일 업로드 | 5-30초 | 파일 크기 & 네트워크 |
| OCR 처리 | 3-8초/페이지 | Upstage API 응답 |
| 구조 파싱 | 2-3초 | Solar Pro 모델 |
| 챗봇 분석 | 3-5초 | RAG + LLM |
| **전체 분석** | **15-50초** | 1-3페이지 기준 |

---

## ✨ 수정 완료 체크리스트

- [ ] `frontend/src/services/api.js` - Issue 1 수정 (uploadContract)
- [ ] `frontend/src/services/api.js` - Issue 2 수정 (analyzeWithChatbot)
- [ ] `frontend/src/pages/ContractPage.jsx` - Issue 3 수정 (userId 전달)
- [ ] 브라우저 캐시 비우기 (Ctrl+Shift+Delete)
- [ ] 개발 서버 재시작 (npm run dev)
- [ ] 백엔드 재시작 (Docker restart 또는 uvicorn)
- [ ] End-to-End 테스트 실행
- [ ] 네트워크 탭에서 요청/응답 확인

---

**수정 완료 후**: 전체 PIPELINE_ANALYSIS.md를 다시 확인하여 Priority 2 개선 사항 검토
