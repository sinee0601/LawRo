import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { settingsAPI } from '../services/api';
import { Check, Sun, Moon, Info } from 'lucide-react';
import MobileHeader from '../components/MobileHeader';
import BottomNav from '../components/BottomNav';
import { getTheme, setTheme } from '../theme';

export default function ThemePage() {
  const navigate = useNavigate();
    const [selectedTheme, setSelectedTheme] = useState(getTheme);
  const [isSaving, setIsSaving] = useState(false);

  const themes = [
    {
      code: 'light',
      name: 'Light Mode (Light)',
      description: '밝은 테마',
      icon: Sun,
      // 미리보기는 현재 테마와 상관없이 고정 색으로 보여 줍니다.
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

  const handleSaveTheme = async (theme) => {
    // 화면에는 바로 적용하고, 계정 프로필 저장은 그 뒤에 시도합니다.
    setTheme(theme);
    setSelectedTheme(theme);
    setIsSaving(true);
    try {
      await settingsAPI.updateTheme(theme);
    } catch (error) {
      // 서버 저장에 실패해도 이 기기에서는 선택한 테마가 유지됩니다.
      console.warn('테마를 계정에 저장하지 못했습니다.', error);
    } finally {
      setIsSaving(false);
    }
    setTimeout(() => navigate('/settings'), 500);
  };

  return (
    <div className="min-h-screen bg-canvas pb-20">
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
                    ? 'border-primary-600 bg-primary-50 dark:bg-primary-500/10'
                    : 'border-line bg-surface hover:border-line-strong'
                } disabled:opacity-50`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center border-2 border-line">
                      <ThemeIcon className="w-6 h-6 text-ink" />
                    </div>
                    <div className="text-left">
                      <p className="text-ink font-bold">{theme.name}</p>
                      <p className="text-xs text-ink-muted">{theme.description}</p>
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
        <div className="p-4 bg-blue-50 dark:bg-blue-500/10 rounded-2xl flex items-start gap-3">
          <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-blue-900 dark:text-blue-200 mb-1">테마 설정</p>
            <p className="text-xs text-blue-800 dark:text-blue-200">
              선택한 테마가 즉시 적용됩니다. 아직은 라이트 모드와 다크 모드 2가지를 지원합니다.
            </p>
          </div>
        </div>
      </main>

      <BottomNav />
    </div>
  );
}
