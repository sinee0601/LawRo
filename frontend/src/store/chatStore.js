import { create } from 'zustand';
import { chatAPI, performanceMetrics } from '../services/api';

const useChatStore = create((set, get) => ({
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

  // 새 세션 생성
  createSession: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await chatAPI.createSession();
      const sessionId = data.session_id;

      set((state) => ({
        sessions: {
          ...state.sessions,
          [sessionId]: {
            id: sessionId,
            messages: [],
            createdAt: new Date().toISOString(),
            language: 'korean', // default language
          }
        },
        currentSessionId: sessionId,
        isLoading: false,
        retryCount: 0,
      }));

      return sessionId;
    } catch (error) {
      set({
        error: error.response?.data?.detail || '세션 생성에 실패했습니다.',
        isLoading: false,
      });
      throw error;
    }
  },

  // 메시지 전송 (enhanced with retry and error handling)
  sendMessage: async (message, customPrompt = null, userLanguage = 'korean') => {
    const { currentSessionId, stats } = get();
    if (!currentSessionId) {
      throw new Error('활성 세션이 없습니다.');
    }

    set({ isLoading: true, error: null });

    // 사용자 메시지 추가
    const userMessageTimestamp = new Date().toISOString();
    set((state) => ({
      sessions: {
        ...state.sessions,
        [currentSessionId]: {
          ...state.sessions[currentSessionId],
          messages: [
            ...state.sessions[currentSessionId].messages,
            {
              role: 'user',
              content: message,
              timestamp: userMessageTimestamp
            }
          ]
        }
      },
      stats: {
        ...state.stats,
        totalMessages: state.stats.totalMessages + 1,
      }
    }));

    const startTime = Date.now();

    try {
      const data = await chatAPI.sendMessage(
        currentSessionId,
        message,
        customPrompt,
        userLanguage
      );

      const duration = Date.now() - startTime;

      // AI 응답 추가
      set((state) => ({
        sessions: {
          ...state.sessions,
          [currentSessionId]: {
            ...state.sessions[currentSessionId],
            messages: [
              ...state.sessions[currentSessionId].messages,
              {
                role: 'assistant',
                content: data.message,  // Backend에서는 'message' 필드 사용
                timestamp: new Date().toISOString(),
                latency: duration,
              }
            ],
            language: userLanguage,
          }
        },
        isLoading: false,
        retryCount: 0,
        stats: {
          ...state.stats,
          successfulMessages: state.stats.successfulMessages + 1,
        }
      }));

      return data;
    } catch (error) {
      const errorMessage = error.response?.data?.detail || '메시지 전송에 실패했습니다.';

      // 특정 에러 메시지 처리
      let userFriendlyError = errorMessage;
      if (errorMessage.includes('credit') || errorMessage.includes('키')) {
        userFriendlyError = 'API 크레딧이 부족합니다. 관리자에게 문의하세요.';
      } else if (errorMessage.includes('timeout')) {
        userFriendlyError = '응답 시간이 초과되었습니다. 다시 시도해주세요.';
      } else if (errorMessage.includes('rate limit')) {
        userFriendlyError = '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.';
      }

      // 에러 메시지를 채팅에 추가
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
        error: userFriendlyError,
        isLoading: false,
        retryCount: state.retryCount + 1,
        stats: {
          ...state.stats,
          failedMessages: state.stats.failedMessages + 1,
        }
      }));

      throw error;
    }
  },

  // 배치 메시지 전송 (new feature)
  sendBatchMessages: async (messages) => {
    const { currentSessionId } = get();
    if (!currentSessionId) {
      throw new Error('활성 세션이 없습니다.');
    }

    set({ isLoading: true, error: null });

    try {
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
          newMessages.push({ role: 'user', content: msg.content, timestamp: new Date().toISOString() });
          newMessages.push({ role: 'assistant', content: responses[idx].message, timestamp: new Date().toISOString() });
        });

        return {
          sessions: {
            ...state.sessions,
            [currentSessionId]: {
              ...state.sessions[currentSessionId],
              messages: newMessages,
            }
          },
          isLoading: false,
        };
      });

      return responses;
    } catch (error) {
      set({
        error: error.response?.data?.detail || '배치 메시지 전송에 실패했습니다.',
        isLoading: false,
      });
      throw error;
    }
  },

  // 세션 히스토리 로드
  loadHistory: async (sessionId) => {
    set({ isLoading: true });
    try {
      const data = await chatAPI.getHistory(sessionId);
      set((state) => ({
        sessions: {
          ...state.sessions,
          [sessionId]: {
            id: sessionId,
            messages: data.messages || [],
            createdAt: data.created_at,
            language: data.language || 'korean',
          }
        },
        currentSessionId: sessionId,
        isLoading: false,
      }));
    } catch (error) {
      console.error('Failed to load history:', error);
      set({
        error: '히스토리 로드에 실패했습니다.',
        isLoading: false,
      });
    }
  },

  // 세션 선택
  selectSession: (sessionId) => {
    set({ currentSessionId: sessionId, error: null });
  },

  // 세션 삭제
  deleteSession: async (sessionId) => {
    try {
      await chatAPI.deleteSession(sessionId);
      set((state) => {
        const newSessions = { ...state.sessions };
        delete newSessions[sessionId];

        return {
          sessions: newSessions,
          currentSessionId: state.currentSessionId === sessionId ? null : state.currentSessionId,
        };
      });
    } catch (error) {
      console.error('Failed to delete session:', error);
      set({ error: '세션 삭제에 실패했습니다.' });
    }
  },

  // 세션 언어 변경
  setSessionLanguage: (language) => {
    const { currentSessionId } = get();
    if (!currentSessionId) return;

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

  // 통계 조회
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

  // 세션 메시지 카운트
  getMessageCount: (sessionId) => {
    const { sessions } = get();
    return sessions[sessionId]?.messages.length || 0;
  },

  // 현재 세션 정보
  getCurrentSession: () => {
    const { sessions, currentSessionId } = get();
    return currentSessionId ? sessions[currentSessionId] : null;
  },

  // 에러 초기화
  clearError: () => set({ error: null }),

  // 전체 상태 초기화
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
}));

export default useChatStore;
