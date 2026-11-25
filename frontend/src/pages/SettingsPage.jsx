import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { ChevronRight, User, Lock, Globe, Palette, HelpCircle, Shield } from 'lucide-react';
import { Card } from '../components/ui';
import AppLayout from '../components/layout/AppLayout';

export default function SettingsPage() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const accountSettings = [
    { icon: User, label: '내정보', path: '/profile' },
    { icon: Lock, label: '비밀번호 변경', path: '/change-password' },
    { icon: Globe, label: '언어 번역', path: '/language' },
    { icon: Palette, label: '앱 색상 변경', path: '/theme' },
  ];

  const infoSettings = [
    { icon: HelpCircle, label: '앱 설명', path: '/about' },
    { icon: Shield, label: '개인정보 처리 방침', path: '/privacy' },
  ];

  return (
    <AppLayout title="설정" width="narrow">
        {/* 계정 섹션 */}
        <div className="mb-6">
          <h2 className="text-lg font-bold text-ink mb-3 px-2">계정</h2>
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
        <button
          onClick={handleLogout}
          className="w-full bg-surface hover:bg-surface-muted text-red-600 dark:text-red-400 font-medium py-4 rounded-card shadow-card transition-colors"
        >
          로그아웃
        </button>

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
