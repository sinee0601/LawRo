import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { settingsAPI } from '../services/api';
import useAuthStore from '../store/authStore';
import { Check, Sun, Moon } from 'lucide-react';
import { Alert } from '../components/ui';
import AppLayout from '../components/layout/AppLayout';
import { getTheme, setTheme } from '../theme';
import useTranslation from '../hooks/useTranslation';


export default function ThemePage() {
  const navigate = useNavigate();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const { t } = useTranslation();
  const [selectedTheme, setSelectedTheme] = useState(getTheme);
  const [isSaving, setIsSaving] = useState(false);

  const themes = [
    {
      code: 'light',
      name: t('theme.light'),
      description: t('theme.lightDesc'),
      preview: t('theme.lightPreview'),
      icon: Sun,
      // 미리보기는 현재 테마와 상관없이 고정 색으로 보여 줍니다.
      bgColor: 'bg-white',
      textColor: 'text-gray-900',
      borderColor: 'border-gray-200',
    },
    {
      code: 'dark',
      name: t('theme.dark'),
      description: t('theme.darkDesc'),
      preview: t('theme.darkPreview'),
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
    // 비로그인이면 이 기기에만 저장합니다.
    if (isAuthenticated) {
      setIsSaving(true);
      try {
        await settingsAPI.updateTheme(theme);
      } catch (error) {
        // 서버 저장에 실패해도 이 기기에서는 선택한 테마가 유지됩니다.
        console.warn('테마를 계정에 저장하지 못했습니다.', error);
      } finally {
        setIsSaving(false);
      }
    }
    setTimeout(() => navigate('/settings'), 500);
  };

  return (
    <AppLayout title={t('theme.title')} showBack width="narrow">
        {/* 테마 선택 카드 */}
        <div className="grid gap-3 sm:grid-cols-2 mb-6">
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
                      <p className={`text-xs font-medium ${theme.textColor}`}>{t('theme.preview')}</p>
                      <p className={`text-xs ${theme.textColor} opacity-70`}>
                        {theme.preview}
                      </p>
                    </div>
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* 정보 메시지 */}
        <Alert tone="info" title={t('theme.infoTitle')}>
          {t('theme.infoBody')}
        </Alert>
      </AppLayout>
  );
}
