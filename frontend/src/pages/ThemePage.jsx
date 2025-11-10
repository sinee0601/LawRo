import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { settingsAPI } from '../services/api';
import { Check, Sun, Moon, Info } from 'lucide-react';
import MobileHeader from '../components/MobileHeader';
import BottomNav from '../components/BottomNav';

export default function ThemePage() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [selectedTheme, setSelectedTheme] = useState('light');
  const [isSaving, setIsSaving] = useState(false);

  const themes = [
    {
      code: 'light',
      name: 'Light Mode (Light)',
      description: '밝은 테마',
      icon: Sun,
      bgColor: 'bg-white',
      textColor: 'text-gray-900',
      borderColor: 'border-gray-200',
    },
    {
      code: 'dark',
      name: 'Dark Mode (Dark)',
      description: '어두운 테마',
      icon: Moon,
      bgColor: 'bg-gray-900',
      textColor: 'text-white',
      borderColor: 'border-gray-700',
    },
  ];

  useEffect(() => {
    // localStorage에서 선택된 테마 로드
    const savedTheme = localStorage.getItem('theme') || 'light';
    setSelectedTheme(savedTheme);
  }, []);

  const handleSaveTheme = async (theme) => {
    setIsSaving(true);
    try {
      // localStorage에 저장
      localStorage.setItem('theme', theme);

      // HTML에 테마 클래스 적용
      if (theme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }

      // Backend API 호출로 Firestore user profile 업데이트
      await settingsAPI.updateTheme(theme);

      setSelectedTheme(theme);
      setTimeout(() => {
        navigate('/settings');
      }, 500);
    } catch (error) {
      alert('테마 설정에 실패했습니다.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <MobileHeader title="앱 색상 변경" showBack={true} />

      <main className="max-w-md mx-auto px-4 pt-20 pb-8">
        {/* 테마 선택 카드 */}
        <div className="space-y-3 mb-6">
          {themes.map((theme) => {
            const ThemeIcon = theme.icon;
            return (
              <button
                key={theme.code}
                onClick={() => handleSaveTheme(theme.code)}
                disabled={isSaving}
                className={`w-full p-4 rounded-2xl border-2 transition-all ${
                  selectedTheme === theme.code
                    ? 'border-primary-600 bg-primary-50'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                } disabled:opacity-50`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center border-2 border-gray-200">
                      <ThemeIcon className="w-6 h-6 text-gray-900" />
                    </div>
                    <div className="text-left">
                      <p className="text-gray-900 font-bold">{theme.name}</p>
                      <p className="text-xs text-gray-500">{theme.description}</p>
                    </div>
                  </div>

                  {selectedTheme === theme.code && (
                    <div className="w-6 h-6 bg-primary-600 rounded-full flex items-center justify-center">
                      <Check className="w-4 h-4 text-white" />
                    </div>
                  )}
                </div>

                {/* 테마 미리보기 */}
                <div className="mt-3 flex gap-2">
                  <div
                    className={`flex-1 h-20 rounded-lg border ${theme.borderColor} ${theme.bgColor} flex items-center justify-center`}
                  >
                    <div className="text-center">
                      <p className={`text-xs font-medium ${theme.textColor}`}>미리보기</p>
                      <p className={`text-xs ${theme.textColor} opacity-70`}>
                        {theme.code === 'light' ? '밝은 화면' : '어두운 화면'}
                      </p>
                    </div>
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* 정보 메시지 */}
        <div className="p-4 bg-blue-50 rounded-2xl flex items-start gap-3">
          <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-blue-900 mb-1">테마 설정</p>
            <p className="text-xs text-blue-800">
              선택한 테마가 즉시 적용됩니다. 아직은 라이트 모드와 다크 모드 2가지를 지원합니다.
            </p>
          </div>
        </div>
      </main>

      <BottomNav />
    </div>
  );
}
