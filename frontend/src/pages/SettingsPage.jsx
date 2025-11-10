import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { ChevronRight, User, Lock, Globe, Palette, HelpCircle, Shield } from 'lucide-react';
import BottomNav from '../components/BottomNav';
import MobileHeader from '../components/MobileHeader';

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
    <div className="min-h-screen bg-gray-50 pb-20">
      <MobileHeader title="설정" showBack={false} />

      <main className="max-w-md mx-auto px-4 pt-20 pb-8">
        {/* 계정 섹션 */}
        <div className="mb-6">
          <h2 className="text-lg font-bold text-gray-900 mb-3 px-2">계정</h2>
          <div className="bg-white rounded-3xl shadow-sm overflow-hidden">
            {accountSettings.map((item, index) => {
              const Icon = item.icon;
              return (
                <button
                  key={index}
                  onClick={() => navigate(item.path)}
                  className={`w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors ${
                    index !== accountSettings.length - 1 ? 'border-b border-gray-100' : ''
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                      <Icon className="w-5 h-5 text-primary-600" />
                    </div>
                    <span className="text-gray-900 font-medium">{item.label}</span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400" />
                </button>
              );
            })}
          </div>
        </div>

        {/* 정보 섹션 */}
        <div className="mb-6">
          <h2 className="text-lg font-bold text-gray-900 mb-3 px-2">정보</h2>
          <div className="bg-white rounded-3xl shadow-sm overflow-hidden">
            {infoSettings.map((item, index) => {
              const Icon = item.icon;
              return (
                <button
                  key={index}
                  onClick={() => navigate(item.path)}
                  className={`w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors ${
                    index !== infoSettings.length - 1 ? 'border-b border-gray-100' : ''
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                      <Icon className="w-5 h-5 text-primary-600" />
                    </div>
                    <span className="text-gray-900 font-medium">{item.label}</span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400" />
                </button>
              );
            })}
          </div>
        </div>

        {/* 로그아웃 버튼 */}
        <button
          onClick={handleLogout}
          className="w-full bg-white hover:bg-gray-50 text-red-600 font-medium py-4 rounded-3xl shadow-sm transition-colors"
        >
          로그아웃
        </button>

        {/* 사용자 정보 */}
        {user && (
          <div className="mt-6 text-center text-sm text-gray-500">
            <p>{user.email}</p>
            <p className="mt-1">LawRo v1.0.0</p>
          </div>
        )}
      </main>

      <BottomNav />
    </div>
  );
}
