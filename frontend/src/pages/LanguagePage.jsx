import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import useTranslation from '../hooks/useTranslation';
import { settingsAPI } from '../services/api';
import { Check, Globe } from 'lucide-react';
import { Alert, Card } from '../components/ui';
import AppLayout from '../components/layout/AppLayout';
import { toast } from '../store/notifyStore';
import { LANGUAGES } from '../i18n/languages';

export default function LanguagePage() {
  const navigate = useNavigate();
  const { setLanguage, isAuthenticated } = useAuthStore();
  const { t, language: currentLanguage } = useTranslation();
  const [isSaving, setIsSaving] = useState(false);

  const handleSaveLanguage = async (language) => {
    setIsSaving(true);
    try {
      // 화면 언어는 바로 바꿉니다 (이 기기에 저장).
      setLanguage(language);

      // 로그인했으면 계정 프로필에도 저장합니다. 챗봇·계약서 분석 답변 언어에도 쓰여요.
      if (isAuthenticated) {
        await settingsAPI.updateLanguage(language);
      }

      setTimeout(() => {
        navigate('/settings');
      }, 500);
    } catch (error) {
      console.error('언어 설정 저장 실패:', error);
      toast.error(t('common.error'));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <AppLayout title={t('language.title')} showBack width="narrow">
        <Card padding="none" className="overflow-hidden">
          {LANGUAGES.map((lang, index) => (
            <button
              key={lang.code}
              onClick={() => handleSaveLanguage(lang.code)}
              disabled={isSaving}
              aria-pressed={currentLanguage === lang.i18n}
              className={`w-full flex items-center justify-between p-4 transition-colors ${
                index !== LANGUAGES.length - 1 ? 'border-b border-line' : ''
              } ${
                currentLanguage === lang.i18n
                  ? 'bg-primary-50 dark:bg-primary-500/10 hover:bg-primary-100 dark:hover:bg-primary-500/20'
                  : 'hover:bg-surface-muted'
              } disabled:opacity-50`}
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{lang.flag}</span>
                <div className="text-left">
                  <p className="text-ink font-medium">{lang.name}</p>
                  <p className="text-xs text-ink-muted">{lang.code}</p>
                </div>
              </div>

              {currentLanguage === lang.i18n && (
                <div className="w-6 h-6 bg-primary-600 rounded-full flex items-center justify-center">
                  <Check className="w-4 h-4 text-white" />
                </div>
              )}
            </button>
          ))}
        </Card>

        {/* 정보 메시지 */}
        <Alert tone="info" icon={Globe} className="mt-6">
          {t('settings.languageDescription')}
        </Alert>
      </AppLayout>
  );
}
