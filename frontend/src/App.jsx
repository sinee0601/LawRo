import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useSearchParams } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import useAuthStore from './store/authStore';
import NotificationHost from './components/feedback/NotificationHost';
import { LoadingState } from './components/ui';
import { loginPath, safeNext } from './services/authRedirect';
import useTranslation from './hooks/useTranslation';

// Lazy-loaded Pages (Code Splitting for better performance)
const LoginPage = lazy(() => import('./pages/LoginPage'));
const SignupPage = lazy(() => import('./pages/SignupPage'));
const ChatPage = lazy(() => import('./pages/ChatPage'));
const ContractPage = lazy(() => import('./pages/ContractPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));
const AnalysisHistoryPage = lazy(() => import('./pages/AnalysisHistoryPage'));
const WorkTimePage = lazy(() => import('./pages/WorkTimePage'));
const SupportCenterPage = lazy(() => import('./pages/SupportCenterPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const ChangePasswordPage = lazy(() => import('./pages/ChangePasswordPage'));
const LanguagePage = lazy(() => import('./pages/LanguagePage'));
const ThemePage = lazy(() => import('./pages/ThemePage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));
const PrivacyPage = lazy(() => import('./pages/PrivacyPage'));

// Loading Fallback Component
function PageLoader() {
  const { t } = useTranslation();
  return <LoadingState fullScreen size="lg" label={t('common.loading')} />;
}

// 로그인이 꼭 필요한 화면: 비로그인이면 로그인으로 보내고, 로그인 후 이 화면으로 돌아옵니다.
function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuthStore();
  const location = useLocation();
  if (isAuthenticated) return children;
  return <Navigate to={loginPath(`${location.pathname}${location.search}`)} replace />;
}

// 로그인·회원가입 화면: 이미 로그인돼 있으면 돌아갈 화면(next)으로 보냅니다.
function GuestOnlyRoute({ children }) {
  const { isAuthenticated } = useAuthStore();
  const [searchParams] = useSearchParams();
  return !isAuthenticated ? children : <Navigate to={safeNext(searchParams.get('next'))} replace />;
}

function App() {
  return (
    <Router>
      <NotificationHost />
      <Suspense fallback={<PageLoader />}>
        <Routes>
        {/* 로그인·회원가입 */}
        <Route
          path="/login"
          element={
            <GuestOnlyRoute>
              <LoginPage />
            </GuestOnlyRoute>
          }
        />
        <Route
          path="/signup"
          element={
            <GuestOnlyRoute>
              <SignupPage />
            </GuestOnlyRoute>
          }
        />

        {/* 로그인 없이 볼 수 있는 화면 (안에서 저장·전송 같은 기능을 쓸 때 로그인으로 보냅니다) */}
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/contract" element={<AnalysisHistoryPage />} />
        <Route
          path="/contract/new"
          element={
            <ProtectedRoute>
              <ContractPage />
            </ProtectedRoute>
          }
        />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/analysis-history" element={<AnalysisHistoryPage />} />
        <Route
          path="/work-time"
          element={
            <ProtectedRoute>
              <WorkTimePage />
            </ProtectedRoute>
          }
        />
        <Route path="/support-center" element={<SupportCenterPage />} />

        {/* 설정 하위 화면 */}
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/change-password"
          element={
            <ProtectedRoute>
              <ChangePasswordPage />
            </ProtectedRoute>
          }
        />
        <Route path="/language" element={<LanguagePage />} />
        <Route path="/theme" element={<ThemePage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/privacy" element={<PrivacyPage />} />

        {/* Default Route */}
        <Route path="/" element={<Navigate to="/contract" replace />} />

        {/* 404 Route */}
        <Route path="*" element={<Navigate to="/contract" replace />} />
        </Routes>
      </Suspense>
    </Router>
  );
}

export default App;
