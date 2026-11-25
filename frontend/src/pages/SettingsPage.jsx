import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { ChevronRight, User, Lock, Globe, Palette, HelpCircle, Shield, LogIn } from 'lucide-react';
import { Button, Card } from '../components/ui';
import { loginPath, signupPath } from '../services/authRedirect';
import AppLayout from '../components/layout/AppLayout';

export default function SettingsPage() {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // 내정보·비밀번호는 계정이 있어야 의미가 있어서 로그인했을 때만 보여줍니다.
  const accountSettings = [
    ...(isAuthenticated
      ? [
          { icon: User, label: '내정보', path: '/profile' },
          { icon: Lock, label: '비밀번호 변경', path: '/change-password' },
        ]
      : []),
    { icon: Globe, label: '언어 번역', path: '/language' },
    { icon: Palette, label: '앱 색상 변경', path: '/theme' },
  ];

  const infoSettings = [
    { icon: HelpCircle, label: '앱 설명', path: '/about' },
    { icon: Shield, label: '개인정보 처리 방침', path: '/privacy' },
  ];

  return (
    <AppLayout title="설정" width="narrow">
        {/* 비로그인: 로그인 안내 */}
        {!isAuthenticated && (
          <Card className="mb-6">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 bg-primary-100 dark:bg-primary-500/20 rounded-full flex items-center justify-center shrink-0">
                <LogIn className="w-5 h-5 text-primary-600 dark:text-primary-400" />
              </div>
              <div>
                <p className="font-semibold text-ink">로그인하고 더 많은 기능을 써 보세요</p>
                <p className="mt-1 text-sm text-ink-muted">계약서 분석 내역, 상담 기록, 근무시간이 계정에 저장돼요.</p>
              </div>
            </div>
            <div className="mt-4 flex gap-2">
              <Button className="flex-1" onClick={() => navigate(loginPath('/settings'))}>
                로그인
              </Button>
              <Button variant="outline" className="flex-1" onClick={() => navigate(signupPath('/settings'))}>
                회원가입
              </Button>
            </div>
          </Card>
        )}

        {/* 계정 섹션 */}
        <div className="mb-6">
          <h2 className="text-lg font-bold text-ink mb-3 px-2">{isAuthenticated ? '계정' : '앱 설정'}</h2>
          <Card padding="none" className="overflow-hidden">
            {accountSettings.map((item, index) => {
              const Icon = item.icon;
              return (
                <button
                  key={index}
                  onClick={() => navigate(item.path)}
                  className={`w-full flex items-center justify-between p-4 hover:bg-surface-muted transition-colors ${
                    index !== accountSettings.length - 1 ? 'border-b border-line' : ''
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary-100 dark:bg-primary-500/20 rounded-full flex items-center justify-center">
                      <Icon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                    </div>
                    <span className="text-ink font-medium">{item.label}</span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-ink-subtle" />
                </button>
              );
            })}
          </Card>
        </div>

        {/* 정보 섹션 */}
        <div className="mb-6">
          <h2 className="text-lg font-bold text-ink mb-3 px-2">정보</h2>
          <Card padding="none" className="overflow-hidden">
            {infoSettings.map((item, index) => {
              const Icon = item.icon;
              return (
                <button
                  key={index}
                  onClick={() => navigate(item.path)}
                  className={`w-full flex items-center justify-between p-4 hover:bg-surface-muted transition-colors ${
                    index !== infoSettings.length - 1 ? 'border-b border-line' : ''
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary-100 dark:bg-primary-500/20 rounded-full flex items-center justify-center">
                      <Icon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                    </div>
                    <span className="text-ink font-medium">{item.label}</span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-ink-subtle" />
                </button>
              );
            })}
          </Card>
        </div>

        {/* 로그아웃 버튼 */}
        {isAuthenticated && (
          <button
            onClick={handleLogout}
            className="w-full bg-surface hover:bg-surface-muted text-red-600 dark:text-red-400 font-medium py-4 rounded-card shadow-card transition-colors"
          >
            로그아웃
          </button>
        )}

        {/* 사용자 정보 */}
        {user && (
          <div className="mt-6 text-center text-sm text-ink-muted">
            <p>{user.email}</p>
            <p className="mt-1">LawRo v1.0.0</p>
          </div>
        )}
      </AppLayout>
  );
}
