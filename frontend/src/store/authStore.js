import { create } from 'zustand';
import { authAPI } from '../services/api';

const useAuthStore = create((set) => ({
  user: JSON.parse(localStorage.getItem('user')) || null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,

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
        error: error.response?.data?.detail || '로그인에 실패했습니다.',
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
      set({ isLoading: false });
      return data;
    } catch (error) {
      set({
        error: error.response?.data?.detail || '회원가입에 실패했습니다.',
        isLoading: false
      });
      throw error;
    }
  },

  // 로그아웃
  logout: () => {
    authAPI.logout();
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

  // 에러 초기화
  clearError: () => set({ error: null }),
}));

export default useAuthStore;
