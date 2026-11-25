import { create } from 'zustand';
import { authAPI } from '../services/api';
import useChatStore from './chatStore';
import i18next from '../i18n/config';
import { toI18nCode } from '../i18n/languages';

const useAuthStore = create((set) => ({
  user: JSON.parse(localStorage.getItem('user')) || null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,
  language: i18next.language, // i18next 코드('ko', 'en' ...)

  // 로그인
  login: async (credentials) => {
    set({ isLoading: true, error: null });
    try {
      const data = await authAPI.login(credentials);
      set({
        user: data.user,
        isAuthenticated: true,
        isLoading: false
      });
      return data;
    } catch (error) {
      set({
        error: error.response?.data?.detail || i18next.t('auth.login.failed'),
        isLoading: false
      });
      throw error;
    }
  },

  // 회원가입
  signup: async (userData) => {
    set({ isLoading: true, error: null });
    try {
      const data = await authAPI.signup(userData);
      set({
        user: data.user,
        isAuthenticated: true,
        isLoading: false
      });
      return data;
    } catch (error) {
      set({
        error: error.response?.data?.detail || i18next.t('auth.signup.failed'),
        isLoading: false
      });
      throw error;
    }
  },

  // 로그아웃
  logout: () => {
    authAPI.logout();
    // 다음 사용자(또는 비로그인 방문자)에게 이전 계정의 대화가 보이지 않도록 비웁니다.
    useChatStore.getState().reset();
    set({
      user: null,
      isAuthenticated: false,
      error: null
    });
  },

  // 프로필 업데이트
  updateProfile: async () => {
    try {
      const profile = await authAPI.getProfile();
      set({ user: profile });
      localStorage.setItem('user', JSON.stringify(profile));
    } catch (error) {
      console.error('Failed to update profile:', error);
    }
  },

  // 언어 설정 변경. 'korean' 같은 서버 코드나 'ko' 같은 i18next 코드 둘 다 받습니다.
  setLanguage: (languageCode) => {
    const i18nCode = toI18nCode(languageCode);
    i18next.changeLanguage(i18nCode);
    localStorage.setItem('userLanguage', i18nCode);
    set({ language: i18nCode });
  },

  // 로그인 시 사용자 언어 설정
  initializeLanguage: (user) => {
    if (user?.preferred_language) {
      useAuthStore.getState().setLanguage(user.preferred_language);
    }
  },

  // 에러 초기화
  clearError: () => set({ error: null }),
}));

export default useAuthStore;
