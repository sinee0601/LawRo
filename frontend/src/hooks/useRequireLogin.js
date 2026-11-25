import { useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { loginPath } from '../services/authRedirect';

/**
 * 로그인이 필요한 동작 앞에서 부릅니다.
 * 로그인돼 있으면 true, 아니면 로그인 화면으로 보내고 false 를 돌려줍니다.
 * next 를 주지 않으면 지금 보고 있는 화면으로 돌아옵니다.
 *
 *   const requireLogin = useRequireLogin();
 *   if (!requireLogin()) return;
 */
export default function useRequireLogin() {
  const navigate = useNavigate();
  const location = useLocation();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  return useCallback(
    (next) => {
      if (isAuthenticated) return true;
      navigate(loginPath(next ?? `${location.pathname}${location.search}`));
      return false;
    },
    [isAuthenticated, navigate, location.pathname, location.search]
  );
}
