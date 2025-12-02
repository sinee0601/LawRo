import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Axios 인스턴스 생성
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Performance tracking
const performanceMetrics = {
  requests: [],
  maxSamples: 100,

  record(endpoint, duration, success) {
    this.requests.push({
      endpoint,
      duration,
      success,
      timestamp: Date.now(),
    });
    if (this.requests.length > this.maxSamples) {
      this.requests.shift();
    }
  },

  getAverageLatency() {
    if (this.requests.length === 0) return 0;
    const sum = this.requests.reduce((acc, r) => acc + r.duration, 0);
    return sum / this.requests.length;
  },

  getSuccessRate() {
    if (this.requests.length === 0) return 0;
    const successes = this.requests.filter(r => r.success).length;
    return successes / this.requests.length;
  },

  getStats() {
    return {
      totalRequests: this.requests.length,
      avgLatency: Math.round(this.getAverageLatency()),
      successRate: (this.getSuccessRate() * 100).toFixed(1),
    };
  },
};

// 요청 인터셉터: JWT 토큰 자동 추가 & 성능 추적
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Start timing
    config.metadata = { startTime: Date.now() };
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터: 에러 처리 & 성능 추적
api.interceptors.response.use(
  (response) => {
    // Record performance
    const duration = Date.now() - response.config.metadata.startTime;
    performanceMetrics.record(response.config.url, duration, true);
    return response;
  },
  (error) => {
    // Record failed request
    if (error.config?.metadata) {
      const duration = Date.now() - error.config.metadata.startTime;
      performanceMetrics.record(error.config.url, duration, false);
    }

    if (error.response?.status === 401) {
      // 토큰 만료 시 로그아웃 처리
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      localStorage.removeItem('userId');
      localStorage.removeItem('userLanguage');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Retry helper with exponential backoff
const retryWithBackoff = async (fn, retries = 3, delay = 1000) => {
  for (let i = 0; i < retries; i++) {
    try {
      return await fn();
    } catch (error) {
      // Don't retry on 4xx errors (except 429)
      if (error.response?.status >= 400 && error.response?.status < 500 && error.response?.status !== 429) {
        throw error;
      }

      if (i === retries - 1) throw error;

      // Exponential backoff
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
    }
  }
};

// 인증 API
export const authAPI = {
  // 회원가입
  signup: async (userData) => {
    const response = await api.post('/auth/signup', userData);
    if (response.data.id_token) {
      localStorage.setItem('access_token', response.data.id_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      // user_id를 별도로 저장 (계약서 분석용)
      if (response.data.user?.uid) {
        localStorage.setItem('userId', response.data.user.uid);
      }
      // 언어 설정 저장
      if (response.data.user?.preferred_language) {
        localStorage.setItem('userLanguage', response.data.user.preferred_language);
      }
    }
    return response.data;
  },

  // 로그인
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    if (response.data.id_token) {
      localStorage.setItem('access_token', response.data.id_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      // user_id를 별도로 저장 (계약서 분석용)
      if (response.data.user?.uid) {
        localStorage.setItem('userId', response.data.user.uid);
      }
      // 언어 설정 저장
      if (response.data.user?.preferred_language) {
        localStorage.setItem('userLanguage', response.data.user.preferred_language);
      }
    }
    return response.data;
  },

  // 로그아웃
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('userId');
    localStorage.removeItem('userLanguage');
  },

  // 프로필 조회
  getProfile: async () => {
    const response = await api.get('/auth/profile');
    return response.data;
  },

  // 소셜 로그인 URL 가져오기
  getSocialLoginUrl: async (provider) => {
    const response = await api.get(`/auth/social/${provider}/login`);
    return response.data;
  },
};

// 챗봇 API (Enhanced with retry logic)
export const chatAPI = {
  // 새 세션 생성
  createSession: async () => {
    return await retryWithBackoff(async () => {
      const response = await api.post('/chat/new-session');
      return response.data;
    });
  },

  // 메시지 전송 (with retry for transient errors)
  sendMessage: async (sessionId, message, customPrompt = null, userLanguage = 'korean') => {
    return await retryWithBackoff(async () => {
      const response = await api.post('/chat/send', {
        session_id: sessionId,
        message,
        custom_prompt: customPrompt,
        user_language: userLanguage,
      });
      return response.data;
    }, 2, 1000); // 2 retries, 1 second initial delay
  },

  // 배치 메시지 전송 (new feature)
  sendBatchMessages: async (messages) => {
    const response = await api.post('/chat/batch', { messages });
    return response.data;
  },

  // 채팅 히스토리 조회
  getHistory: async (sessionId) => {
    const response = await api.get(`/chat/history/${sessionId}`);
    return response.data;
  },

  // 세션 삭제
  deleteSession: async (sessionId) => {
    const response = await api.delete(`/chat/history/${sessionId}`);
    return response.data;
  },

  // 세션 통계 조회 (new)
  getSessionStats: async () => {
    const response = await api.get('/chat/stats');
    return response.data;
  },
};

// 계약서 분석 API
export const contractAPI = {
  // 계약서 업로드
  uploadContract: async (file, onProgress, userId, language = 'korean') => {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('language', language);
    formData.append('files', file);

    const response = await api.post('/contract/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      },
    });
    return response.data;
  },

  // 계약서 분석 (기본)
  analyzeContract: async (contractId) => {
    const response = await api.post('/api/analyze', {
      contract_id: contractId,
    });
    return response.data;
  },

  // 계약서 완전 분석 (챗봇 통합)
  analyzeWithChatbot: async (contractId, userId, language = 'korean') => {
    const response = await api.post('/contract/api/analyze-with-chatbot', {
      user_id: userId,
      contract_id: contractId,
      use_chatbot: true,
      user_language: language,
      use_saved_data: true,
    });
    return response.data;
  },

  // 계약서 템플릿 가져오기
  getTemplates: async () => {
    const response = await api.get('/api/template');
    return response.data;
  },

  // 분석 히스토리 조회 (레거시)
  getHistory: async () => {
    const response = await api.get('/contract/history');
    return response.data;
  },

  // 분석 내역 조회 (Firestore)
  getAnalysisHistory: async (userId) => {
    const response = await api.get(`/contract/api/analysis-history/${userId}`);
    return response.data;
  },

  // 분석 삭제
  deleteAnalysis: async (analysisId) => {
    const response = await api.delete(`/contract/api/analysis/${analysisId}`);
    return response.data;
  },
};

// 근무시간 추적 API
export const worktimeAPI = {
  // 근무지 저장/업데이트
  saveWorkplace: async (latitude, longitude, address = null, radiusMeters = 500) => {
    const response = await api.post('/worktime/workplace', {
      latitude,
      longitude,
      address,
      radius_meters: radiusMeters,
    });
    return response.data;
  },

  // 근무지 조회
  getWorkplace: async () => {
    const response = await api.get('/worktime/workplace');
    return response.data;
  },

  // 근무지 삭제
  deleteWorkplace: async () => {
    const response = await api.delete('/worktime/workplace');
    return response.data;
  },

  // 위치 상태 확인 (근무지 반경 내인지 확인)
  checkLocationStatus: async (currentLatitude, currentLongitude) => {
    const response = await api.post('/worktime/location-status', {
      current_latitude: currentLatitude,
      current_longitude: currentLongitude,
    });
    return response.data;
  },

  // 근무 기록 저장
  saveWorkRecord: async (startTime, endTime, location, date) => {
    const response = await api.post('/worktime/records', {
      start_time: startTime,
      end_time: endTime,
      duration_seconds: Math.floor((endTime - startTime) / 1000),
      location: {
        latitude: location.latitude,
        longitude: location.longitude,
        address: location.address,
      },
      date,
    });
    return response.data;
  },

  // 근무 기록 조회
  getWorkRecords: async (date = null, limit = 100) => {
    const params = new URLSearchParams();
    if (date) params.append('date', date);
    if (limit) params.append('limit', limit);

    const response = await api.get(`/worktime/records?${params.toString()}`);
    return response.data;
  },

  // 근무 기록 삭제
  deleteWorkRecord: async (recordId) => {
    const response = await api.delete(`/worktime/records/${recordId}`);
    return response.data;
  },

  // 근무 요약 (날짜 범위)
  getWorkSummary: async (startDate, endDate) => {
    const response = await api.get(
      `/worktime/summary?start_date=${startDate}&end_date=${endDate}`
    );
    return response.data;
  },

  // 근무 서비스 상태 확인
  checkHealth: async () => {
    const response = await api.get('/worktime/health');
    return response.data;
  },
};

// 설정 API
export const settingsAPI = {
  // 사용자 프로필 업데이트
  updateProfile: async (fullName) => {
    const response = await api.put('/auth/profile', {
      full_name: fullName,
    });
    return response.data;
  },

  // 비밀번호 변경
  changePassword: async (email, currentPassword, newPassword) => {
    const response = await api.post('/auth/change-password', {
      email,
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  },

  // 사용자 언어 설정 저장
  updateLanguage: async (language) => {
    const response = await api.put('/auth/profile', {
      preferred_language: language,
    });
    return response.data;
  },

  // 사용자 테마 설정 저장
  updateTheme: async (theme) => {
    const response = await api.put('/auth/profile', {
      theme_preference: theme,
    });
    return response.data;
  },
};

// 헬스 체크 API (Enhanced)
export const healthAPI = {
  // 기본 헬스 체크
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // 상세 헬스 상태 (chat service 포함)
  getDetailedStatus: async () => {
    const response = await api.get('/chat/health');
    return response.data;
  },

  // 프론트엔드 성능 메트릭
  getClientMetrics: () => {
    return performanceMetrics.getStats();
  },
};

// Export performance metrics for monitoring
export { performanceMetrics };

export default api;
