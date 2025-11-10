# Frontend 개선 사항 요약

Backend chat_service.py의 개선사항에 맞춰 Frontend를 전면 재구성했습니다.

## 📋 목차
1. [API 서비스 개선](#1-api-서비스-개선)
2. [Chat Store 개선](#2-chat-store-개선)
3. [Health Dashboard 추가](#3-health-dashboard-추가)
4. [주요 기능 추가](#4-주요-기능-추가)
5. [사용 방법](#5-사용-방법)

---

## 1. API 서비스 개선

### 📁 파일: `frontend/src/services/api.js`

### ✨ 주요 개선사항

#### 1.1 성능 메트릭 추적
```javascript
const performanceMetrics = {
  requests: [],
  maxSamples: 100,

  record(endpoint, duration, success) {
    // 요청 성능 기록
  },

  getAverageLatency() { ... },
  getSuccessRate() { ... },
  getStats() { ... }
}
```

**효과**:
- 모든 API 요청의 지연시간 추적
- 성공률 실시간 계산
- 최근 100개 요청 샘플 유지

#### 1.2 요청/응답 인터셉터 강화
```javascript
// 요청 시작 시간 기록
api.interceptors.request.use((config) => {
  config.metadata = { startTime: Date.now() };
  return config;
});

// 응답 시간 계산 및 기록
api.interceptors.response.use((response) => {
  const duration = Date.now() - response.config.metadata.startTime;
  performanceMetrics.record(response.config.url, duration, true);
  return response;
});
```

#### 1.3 재시도 로직 (Exponential Backoff)
```javascript
const retryWithBackoff = async (fn, retries = 3, delay = 1000) => {
  for (let i = 0; i < retries; i++) {
    try {
      return await fn();
    } catch (error) {
      // 4xx 에러는 재시도 안함 (429 제외)
      if (error.response?.status >= 400 &&
          error.response?.status < 500 &&
          error.response?.status !== 429) {
        throw error;
      }

      // 지수 백오프
      await new Promise(resolve =>
        setTimeout(resolve, delay * Math.pow(2, i))
      );
    }
  }
};
```

**재시도 전략**:
- 1차 실패: 1초 대기
- 2차 실패: 2초 대기
- 3차 실패: 4초 대기
- Rate Limit (429): 자동 재시도
- Client Error (4xx): 재시도 안함

#### 1.4 챗봇 API 개선
```javascript
export const chatAPI = {
  // 메시지 전송 (재시도 + 다국어 지원)
  sendMessage: async (sessionId, message, customPrompt, userLanguage = 'korean') => {
    return await retryWithBackoff(async () => {
      const response = await api.post('/chat/send', {
        session_id: sessionId,
        message,
        custom_prompt: customPrompt,
        user_language: userLanguage,  // ✨ 새로 추가
      });
      return response.data;
    }, 2, 1000);
  },

  // 배치 메시지 전송 (✨ 새 기능)
  sendBatchMessages: async (messages) => {
    const response = await api.post('/chat/batch', { messages });
    return response.data;
  },

  // 세션 통계 (✨ 새 기능)
  getSessionStats: async () => {
    const response = await api.get('/chat/stats');
    return response.data;
  },
};
```

#### 1.5 헬스 체크 API 강화
```javascript
export const healthAPI = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // ✨ 상세 헬스 상태
  getDetailedStatus: async () => {
    const response = await api.get('/chat/health');
    return response.data;
  },

  // ✨ 클라이언트 메트릭
  getClientMetrics: () => {
    return performanceMetrics.getStats();
  },
};
```

#### 1.6 파일 업로드 진행률 추적
```javascript
uploadContract: async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (onProgress) {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percentCompleted);
      }
    },
  });
  return response.data;
}
```

---

## 2. Chat Store 개선

### 📁 파일: `frontend/src/store/chatStore.js`

### ✨ 주요 개선사항

#### 2.1 상태 추가
```javascript
const useChatStore = create((set, get) => ({
  sessions: {},
  currentSessionId: null,
  isLoading: false,
  error: null,
  retryCount: 0,  // ✨ 재시도 카운터
  stats: {        // ✨ 통계
    totalMessages: 0,
    successfulMessages: 0,
    failedMessages: 0,
  },
}));
```

#### 2.2 메시지 전송 강화
```javascript
sendMessage: async (message, customPrompt = null, userLanguage = 'korean') => {
  const startTime = Date.now();

  try {
    const data = await chatAPI.sendMessage(
      currentSessionId,
      message,
      customPrompt,
      userLanguage  // ✨ 언어 지원
    );

    const duration = Date.now() - startTime;

    // ✨ 응답에 지연시간 포함
    set((state) => ({
      sessions: {
        ...state.sessions,
        [currentSessionId]: {
          ...state.sessions[currentSessionId],
          messages: [
            ...state.sessions[currentSessionId].messages,
            {
              role: 'assistant',
              content: data.response,
              timestamp: new Date().toISOString(),
              latency: duration,  // ✨ 지연시간
            }
          ],
        }
      },
      stats: {
        ...state.stats,
        successfulMessages: state.stats.successfulMessages + 1,
      }
    }));
  } catch (error) {
    // ✨ 사용자 친화적 에러 메시지
    let userFriendlyError = errorMessage;
    if (errorMessage.includes('credit')) {
      userFriendlyError = 'API 크레딧이 부족합니다.';
    } else if (errorMessage.includes('timeout')) {
      userFriendlyError = '응답 시간이 초과되었습니다.';
    } else if (errorMessage.includes('rate limit')) {
      userFriendlyError = '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.';
    }

    // ✨ 에러를 채팅에 표시
    set((state) => ({
      sessions: {
        ...state.sessions,
        [currentSessionId]: {
          ...state.sessions[currentSessionId],
          messages: [
            ...state.sessions[currentSessionId].messages,
            {
              role: 'assistant',
              content: `⚠️ ${userFriendlyError}`,
              timestamp: new Date().toISOString(),
              isError: true,
            }
          ]
        }
      },
      stats: {
        ...state.stats,
        failedMessages: state.stats.failedMessages + 1,
      }
    }));
  }
}
```

#### 2.3 새로운 유틸리티 함수들
```javascript
// ✨ 언어 변경
setSessionLanguage: (language) => {
  set((state) => ({
    sessions: {
      ...state.sessions,
      [currentSessionId]: {
        ...state.sessions[currentSessionId],
        language,
      }
    }
  }));
},

// ✨ 통계 조회
getStats: () => {
  const { stats } = get();
  const clientMetrics = performanceMetrics.getStats();

  return {
    ...stats,
    successRate: stats.totalMessages > 0
      ? ((stats.successfulMessages / stats.totalMessages) * 100).toFixed(1)
      : 0,
    clientMetrics,
  };
},

// ✨ 메시지 카운트
getMessageCount: (sessionId) => {
  const { sessions } = get();
  return sessions[sessionId]?.messages.length || 0;
},

// ✨ 현재 세션 정보
getCurrentSession: () => {
  const { sessions, currentSessionId } = get();
  return currentSessionId ? sessions[currentSessionId] : null;
},

// ✨ 전체 초기화
reset: () => set({
  sessions: {},
  currentSessionId: null,
  isLoading: false,
  error: null,
  retryCount: 0,
  stats: {
    totalMessages: 0,
    successfulMessages: 0,
    failedMessages: 0,
  },
}),
```

#### 2.4 배치 메시지 전송
```javascript
// ✨ 여러 메시지를 한번에 전송
sendBatchMessages: async (messages) => {
  const { currentSessionId } = get();

  const batchRequests = messages.map(msg => ({
    session_id: currentSessionId,
    message: msg.content,
    custom_prompt: msg.customPrompt,
    user_language: msg.language || 'korean',
  }));

  const responses = await chatAPI.sendBatchMessages(batchRequests);

  // 모든 응답을 세션에 추가
  set((state) => {
    const newMessages = [...state.sessions[currentSessionId].messages];

    messages.forEach((msg, idx) => {
      newMessages.push({
        role: 'user',
        content: msg.content,
        timestamp: new Date().toISOString()
      });
      newMessages.push({
        role: 'assistant',
        content: responses[idx].response,
        timestamp: new Date().toISOString()
      });
    });

    return {
      sessions: {
        ...state.sessions,
        [currentSessionId]: {
          ...state.sessions[currentSessionId],
          messages: newMessages,
        }
      },
    };
  });
}
```

---

## 3. Health Dashboard 추가

### 📁 파일: `frontend/src/components/HealthDashboard.jsx`

### ✨ 주요 기능

#### 3.1 실시간 헬스 모니터링
```javascript
useEffect(() => {
  fetchHealthStatus();
  const interval = setInterval(fetchHealthStatus, 30000); // 30초마다 업데이트
  return () => clearInterval(interval);
}, []);
```

#### 3.2 표시 정보

**1. 전체 시스템 상태**
- 시스템이 정상인지 확인
- 문제가 있는 경우 경고 표시

**2. 컴포넌트 상태**
- LLM (Language Model): AI 모델 상태
- Vector Store: 문서 검색 DB 상태
- Firestore: 세션 저장소 상태

**3. 성능 메트릭**
- LLM 평균 지연시간
- LLM 성공률
- RAG 평균 지연시간
- RAG 히트율

**4. 세션 통계**
- 전체 세션 수
- 활성 세션 수
- 전체 메시지 수
- 저장소 백엔드 (firestore/memory)

**5. 클라이언트 메트릭**
- 총 요청 수
- 평균 지연시간
- 성공률

**6. 사용자 세션 통계**
- 총 메시지
- 성공한 메시지
- 실패한 메시지

**7. 시스템 설정**
- LLM 모델 (solar-pro2)
- 임베딩 모델 (solar-embedding-1-large-query)
- 검색 문서 수 (k=2)
- 유사도 임계값 (0.5)

#### 3.3 컴포넌트 구조
```jsx
<HealthDashboard>
  <OverallStatus /> {/* 전체 상태 */}
  <ComponentsStatus /> {/* LLM, VectorStore, Firestore */}
  <PerformanceMetrics /> {/* 성능 지표 */}
  <SessionStats /> {/* 세션 통계 */}
  <ClientMetrics /> {/* 클라이언트 메트릭 */}
  <UserSessionStats /> {/* 사용자 통계 */}
  <Configuration /> {/* 시스템 설정 */}
</HealthDashboard>
```

#### 3.4 시각적 요소
- ✅ 정상: 녹색 배경
- ⚠️ 비활성: 회색 배경
- ❌ 오류: 빨간색 배경
- 📊 메트릭 카드: 색상별 구분

---

## 4. 주요 기능 추가

### 4.1 다국어 지원
```javascript
// 한국어, 영어, 중국어, 베트남어, 일본어, 태국어 지원
const languages = ['korean', 'english', 'chinese', 'vietnamese', 'japanese', 'thai'];

// 사용 예시
await sendMessage('안녕하세요', null, 'korean');
await sendMessage('Hello', null, 'english');
```

### 4.2 에러 핸들링
```javascript
// Backend에서 발생한 에러를 사용자 친화적으로 변환
if (errorMessage.includes('credit')) {
  return 'API 크레딧이 부족합니다. 관리자에게 문의하세요.';
} else if (errorMessage.includes('timeout')) {
  return '응답 시간이 초과되었습니다. 다시 시도해주세요.';
} else if (errorMessage.includes('rate limit')) {
  return '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.';
}
```

### 4.3 성능 추적
```javascript
// 모든 메시지에 응답 지연시간 기록
{
  role: 'assistant',
  content: '답변 내용',
  timestamp: '2025-11-03T12:33:52.451Z',
  latency: 1460  // 1.46초
}
```

### 4.4 재시도 메커니즘
- API 요청 실패 시 자동 재시도
- 지수 백오프 전략 사용
- Rate Limit 에러 자동 처리

### 4.5 배치 처리
```javascript
// 여러 메시지를 한번에 전송 (비용 절감)
const messages = [
  { content: '질문 1', language: 'korean' },
  { content: '질문 2', language: 'korean' },
  { content: '질문 3', language: 'korean' },
];

await sendBatchMessages(messages);
```

---

## 5. 사용 방법

### 5.1 Health Dashboard 사용

#### DashboardPage에 추가하기
```jsx
// frontend/src/pages/DashboardPage.jsx
import HealthDashboard from '../components/HealthDashboard';

function DashboardPage() {
  return (
    <div>
      {/* 기존 대시보드 내용 */}

      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">시스템 상태</h2>
        <HealthDashboard />
      </div>
    </div>
  );
}
```

### 5.2 다국어 채팅

```jsx
// frontend/src/pages/ChatPage.jsx
import useChatStore from '../store/chatStore';

function ChatPage() {
  const sendMessage = useChatStore(state => state.sendMessage);
  const [language, setLanguage] = useState('korean');

  const handleSend = async (message) => {
    await sendMessage(message, null, language);
  };

  return (
    <div>
      <select value={language} onChange={(e) => setLanguage(e.target.value)}>
        <option value="korean">한국어</option>
        <option value="english">English</option>
        <option value="chinese">中文</option>
      </select>

      {/* 채팅 UI */}
    </div>
  );
}
```

### 5.3 통계 조회

```jsx
import useChatStore from '../store/chatStore';

function StatsPanel() {
  const getStats = useChatStore(state => state.getStats);
  const stats = getStats();

  return (
    <div>
      <p>총 메시지: {stats.totalMessages}</p>
      <p>성공률: {stats.successRate}%</p>
      <p>평균 지연시간: {stats.clientMetrics.avgLatency}ms</p>
    </div>
  );
}
```

### 5.4 파일 업로드 진행률

```jsx
import { contractAPI } from '../services/api';

function ContractUpload() {
  const [progress, setProgress] = useState(0);

  const handleUpload = async (file) => {
    try {
      const result = await contractAPI.uploadContract(file, (percent) => {
        setProgress(percent);
      });
      console.log('Upload complete:', result);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  return (
    <div>
      <input type="file" onChange={(e) => handleUpload(e.target.files[0])} />
      <div>진행률: {progress}%</div>
    </div>
  );
}
```

---

## 6. Backend와의 통합

### 6.1 새 엔드포인트 요구사항

Frontend에서 사용하는 새 엔드포인트들:

```
GET  /chat/health          - 상세 헬스 체크
GET  /chat/stats           - 세션 통계
POST /chat/batch           - 배치 메시지 전송
```

### 6.2 Backend 라우터 추가 필요

```python
# backend/app/routers/chat.py

@router.get("/health")
async def get_chat_health():
    """Get detailed health status"""
    health = await chat_service.get_health_status()
    return health

@router.get("/stats")
async def get_session_stats():
    """Get session statistics"""
    stats = chat_service.get_session_stats()
    return stats

@router.post("/batch")
async def batch_process_messages(request: BatchMessageRequest):
    """Process multiple messages in batch"""
    results = await chat_service.batch_process_messages(request.messages)
    return {"results": results}
```

---

## 7. 성능 개선 효과

| 항목 | 개선 전 | 개선 후 |
|------|---------|---------|
| **에러 처리** | 기본 try-catch | 재시도 + 사용자 친화적 메시지 |
| **성능 추적** | 없음 | 실시간 메트릭 + 통계 |
| **언어 지원** | 한국어만 | 6개 언어 지원 |
| **모니터링** | 없음 | Health Dashboard |
| **업로드 진행률** | 없음 | 실시간 진행률 표시 |
| **재시도 로직** | 없음 | 지수 백오프 |
| **배치 처리** | 없음 | 다중 메시지 처리 |

---

## 8. 테스트 방법

### 8.1 성능 메트릭 확인
```javascript
import { performanceMetrics } from './services/api';

console.log(performanceMetrics.getStats());
// {
//   totalRequests: 42,
//   avgLatency: 1234,
//   successRate: "95.2"
// }
```

### 8.2 Health Dashboard 확인
1. 대시보드 페이지 접속
2. "시스템 상태" 섹션 확인
3. 각 컴포넌트 상태 확인 (정상/비활성/오류)
4. 성능 메트릭 확인

### 8.3 에러 시뮬레이션
```javascript
// API 키를 잘못된 값으로 변경하여 에러 테스트
// 채팅에 "⚠️ API 크레딧이 부족합니다" 메시지가 표시되는지 확인
```

---

## 9. 다음 단계

### 9.1 추가 개선 사항
- [ ] 실시간 스트리밍 응답 지원
- [ ] 채팅 내보내기/가져오기
- [ ] 음성 입력 지원
- [ ] 다크 모드
- [ ] 채팅 검색 기능

### 9.2 Backend 연동 필요
- [ ] `/chat/health` 엔드포인트 구현
- [ ] `/chat/stats` 엔드포인트 구현
- [ ] `/chat/batch` 엔드포인트 구현

---

## 10. 요약

✅ **완료된 작업**:
1. API 서비스 전면 개선 (재시도, 성능 추적, 배치 처리)
2. Chat Store 강화 (에러 핸들링, 통계, 다국어)
3. Health Dashboard 컴포넌트 추가
4. 성능 모니터링 시스템 구축
5. 사용자 경험 개선 (진행률, 에러 메시지)

🎯 **핵심 개선 효과**:
- 안정성 향상: 재시도 로직 + 에러 핸들링
- 모니터링: 실시간 성능 메트릭
- 사용자 경험: 친화적 에러 메시지 + 진행률 표시
- 국제화: 6개 언어 지원
- 성능: 배치 처리 + 지연시간 추적

🚀 **다음 단계**:
1. Backend 라우터에 새 엔드포인트 추가
2. Health Dashboard를 DashboardPage에 통합
3. 프로덕션 배포 전 테스트
