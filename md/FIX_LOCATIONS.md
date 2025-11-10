# 🎯 정확한 수정 위치 맵

## 📍 3개 파일, 3가지 수정

### 1️⃣ `frontend/src/services/api.js` - uploadContract 함수

**위치**: 라인 200-210

**현재 코드** ❌:
```javascript
const uploadContract = (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/api/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (event) => {
            onUploadProgress(Math.round((event.loaded / event.total) * 100));
        }
    });
};
```

**수정 코드** ✅:
```javascript
const uploadContract = (file, onUploadProgress, userId, language = "korean") => {
    const formData = new FormData();
    formData.append("user_id", userId);           // NEW
    formData.append("language", language);        // NEW
    formData.append("files", file);               // CHANGED: "file" → "files"
    return api.post("/contract/api/upload", formData, {  // CHANGED: "/api/upload" → "/contract/api/upload"
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (event) => {
            onUploadProgress(Math.round((event.loaded / event.total) * 100));
        }
    });
};
```

**변경 요약**:
- [ ] 함수 서명에 `userId`, `language = "korean"` 파라미터 추가
- [ ] `formData.append("user_id", userId)` 추가
- [ ] `formData.append("language", language)` 추가
- [ ] `formData.append("file", file)` → `formData.append("files", file)` 변경
- [ ] 엔드포인트 `/api/upload` → `/contract/api/upload` 변경

---

### 2️⃣ `frontend/src/services/api.js` - analyzeWithChatbot 함수

**위치**: 라인 220-230

**현재 코드** ❌:
```javascript
const analyzeWithChatbot = (contractId) => {
    return api.post("/api/analyze-with-chatbot", {
        contract_id: contractId
    });
};
```

**수정 코드** ✅:
```javascript
const analyzeWithChatbot = (contractId, userId, language = "korean") => {
    return api.post("/contract/api/analyze-with-chatbot", {  // CHANGED: "/api/..." → "/contract/api/..."
        user_id: userId,              // NEW
        contract_id: contractId,
        use_chatbot: true,            // NEW
        user_language: language,      // NEW
        use_saved_data: true          // NEW
    });
};
```

**변경 요약**:
- [ ] 함수 서명에 `userId`, `language = "korean"` 파라미터 추가
- [ ] 엔드포인트 `/api/analyze-with-chatbot` → `/contract/api/analyze-with-chatbot` 변경
- [ ] `user_id: userId,` 추가
- [ ] `use_chatbot: true,` 추가
- [ ] `user_language: language,` 추가
- [ ] `use_saved_data: true` 추가

---

### 3️⃣ `frontend/src/pages/ContractPage.jsx` - handleAnalyze 함수

**위치**: 라인 60-92

**현재 코드** ❌:
```javascript
const handleAnalyze = async () => {
    if (!file) return;
    setIsUploading(true);
    setError(null);

    try {
        // 1. 파일 업로드 (진행률 추적)
        const uploadData = await contractAPI.uploadContract(
            file,
            (percent) => {
                console.log(`Upload progress: ${percent}%`);
            }
        );
        const contractId = uploadData.contract_id;

        setIsUploading(false);
        setIsAnalyzing(true);

        // 2. 계약서 분석 (챗봇 통합)
        // - OCR 처리
        // - 구조화 (Solar Pro 2)
        // - Chatbot 분석 (분석 템플릿 사용)
        const analysisData = await contractAPI.analyzeWithChatbot(contractId);

        setResult(analysisData);
        setIsAnalyzing(false);
    } catch (err) {
        setError(err.response?.data?.detail || '분석 중 오류가 발생했습니다.');
        setIsUploading(false);
        setIsAnalyzing(false);
    }
};
```

**수정 코드** ✅:
```javascript
const handleAnalyze = async () => {
    if (!file) return;
    setIsUploading(true);
    setError(null);

    try {
        // 1. 파일 업로드 (진행률 추적)
        const uploadData = await contractAPI.uploadContract(
            file,
            (percent) => {
                console.log(`Upload progress: ${percent}%`);
            },
            userId,                  // NEW
            userLanguage || "korean" // NEW
        );
        const contractId = uploadData.contract_id;

        setIsUploading(false);
        setIsAnalyzing(true);

        // 2. 계약서 분석 (챗봇 통합)
        // - OCR 처리
        // - 구조화 (Solar Pro 2)
        // - Chatbot 분석 (분석 템플릿 사용)
        const analysisData = await contractAPI.analyzeWithChatbot(
            contractId,
            userId,                  // NEW
            userLanguage || "korean" // NEW
        );

        setResult(analysisData);
        setIsAnalyzing(false);
    } catch (err) {
        setError(err.response?.data?.detail || '분석 중 오류가 발생했습니다.');
        setIsUploading(false);
        setIsAnalyzing(false);
    }
};
```

**변경 요약**:
- [ ] `uploadContract` 호출에 `, userId, userLanguage || "korean"` 추가 (라인 70-71)
- [ ] `analyzeWithChatbot` 호출에 `, userId, userLanguage || "korean"` 추가 (라인 82-84)

**주의**: ContractPage.jsx 상단에서 `userId`와 `userLanguage` 변수 확인 필요!

```javascript
// ContractPage.jsx 상단에 추가되어 있는지 확인
const userId = localStorage.getItem("userId") || useAuth()?.user?.id;  // 또는 다른 방식
const userLanguage = localStorage.getItem("userLanguage") || "korean";
```

만약 없다면 다음과 같이 추가:
```javascript
// useAuth는 프로젝트의 인증 훅 (Firebase, Supabase 등)
import { useAuth } from "../store/authStore";  // 또는 적절한 훅

export default function ContractPage() {
    const auth = useAuth();
    const userId = auth?.user?.id || auth?.user?.uid;
    const userLanguage = localStorage.getItem("userLanguage") || "korean";
    // ... 나머지 코드
}
```

---

## 🔄 변경 요약 표

| 파일 | 함수 | 라인 | 변경 사항 | 우선순위 |
|------|------|------|---------|---------|
| api.js | uploadContract | 200-210 | 함수 서명 + FormData 필드 3개 | 🔴 P1 |
| api.js | analyzeWithChatbot | 220-230 | 함수 서명 + 요청 바디 5개 필드 | 🔴 P1 |
| ContractPage.jsx | handleAnalyze | 70-71, 82-84 | 함수 호출에 userId, language 전달 | 🔴 P1 |

---

## ✅ 검증 체크리스트

### 수정 전
- [ ] VSCode에서 3개 파일 열기
- [ ] git 상태 확인 (변경 사항 없는 상태)

### 수정 중
- [ ] `frontend/src/services/api.js` - uploadContract 수정 완료
  - [ ] 함수 서명 수정
  - [ ] FormData 필드 3개 추가
  - [ ] 엔드포인트 경로 수정

- [ ] `frontend/src/services/api.js` - analyzeWithChatbot 수정 완료
  - [ ] 함수 서명 수정
  - [ ] 요청 바디 5개 필드 추가
  - [ ] 엔드포인트 경로 수정

- [ ] `frontend/src/pages/ContractPage.jsx` - handleAnalyze 수정 완료
  - [ ] userId, userLanguage 변수 확인/추가
  - [ ] uploadContract 호출에 파라미터 추가
  - [ ] analyzeWithChatbot 호출에 파라미터 추가

### 수정 후
- [ ] 문법 오류 확인 (IDE 오류 표시 없음)
- [ ] 파일 저장
- [ ] git diff 확인
  ```bash
  git diff frontend/src/services/api.js
  git diff frontend/src/pages/ContractPage.jsx
  ```

### 테스트
- [ ] 개발 서버 재시작: `npm run dev`
- [ ] 브라우저 캐시 비우기: Ctrl+Shift+Delete
- [ ] 파일 업로드 테스트
  - [ ] 로그인 후 ContractPage 접속
  - [ ] 계약서 이미지 선택
  - [ ] "분석 시작" 클릭
  - [ ] DevTools Network 탭에서 요청 확인
    - [ ] FormData에 `user_id`, `language` 포함
    - [ ] `files` 필드 포함 (복수형)
  - [ ] 업로드 완료 및 contract_id 수신 확인

- [ ] 계약서 분석 테스트
  - [ ] 분석이 자동으로 시작되는지 확인
  - [ ] DevTools Network 탭에서 요청 확인
    - [ ] POST body에 `user_id`, `contract_id`, `use_chatbot`, `user_language`, `use_saved_data` 포함
    - [ ] 200 OK 응답 확인
  - [ ] 분석 결과 표시 확인
    - [ ] 계약 정보 (structured_result)
    - [ ] AI 분석 (chatbot_analysis)
    - [ ] 위험 요소 (risks)

---

## 🐛 일반적인 실수 (피해야 할 것들)

❌ **하면 안 되는 것들**:
- `formData.append("file", file)` - 필드명이 "file"이 아니라 "files" (복수형)
- `/api/upload` - 정확한 경로는 `/contract/api/upload`
- `/api/analyze-with-chatbot` - 정확한 경로는 `/contract/api/analyze-with-chatbot`
- userId 미전달 - Backend에서 필수 필드
- use_chatbot, use_saved_data 미포함 - Backend에서 필수 필드

✅ **해야 할 것들**:
- FormData에 `user_id`, `language` 추가
- 요청 바디에 5개 필드 모두 포함
- 함수 호출 시 userId, language 전달
- 엔드포인트 경로 정확히 일치

---

## 📝 수정 예상 시간

| 항목 | 시간 |
|------|------|
| 이해 및 준비 | 5분 |
| uploadContract 수정 | 3분 |
| analyzeWithChatbot 수정 | 3분 |
| ContractPage 수정 | 3분 |
| 저장 및 테스트 | 5분 |
| **총 시간** | **19분** |

---

## 🚀 다음 명령어

### 수정 완료 후
```bash
# 개발 서버 재시작
npm run dev

# (새 터미널) 백엔드 재시작 (필요시)
cd backend
docker-compose restart
```

### 테스트
```bash
# 브라우저에서 테스트
http://localhost:5173/contract
```

---

**최종 확인**: 3개 파일, 3가지 수정, 19분 소요
**현재 상태**: 🔴 수정 필요
**수정 후 상태**: 🟢 프로덕션 준비 완료
