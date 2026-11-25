import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import useTranslation from '../hooks/useTranslation';
import { settingsAPI } from '../services/api';
import { Check, Globe } from 'lucide-react';
import { Card } from '../components/ui';
import AppLayout from '../components/layout/AppLayout';
import { toast } from '../store/notifyStore';

export default function LanguagePage() {
  const navigate = useNavigate();
  const { setLanguage, isAuthenticated } = useAuthStore();
  const { t } = useTranslation();
  const [selectedLanguage, setSelectedLanguage] = useState('korean');
  const [isSaving, setIsSaving] = useState(false);

  const languages = [
    { code: 'korean', name: '한국어', flag: '🇰🇷' },
    { code: 'english', name: 'English', flag: '🇺🇸' },
    { code: 'chinese', name: '中文', flag: '🇨🇳' },
    { code: 'vietnamese', name: 'Tiếng Việt', flag: '🇻🇳' },
    { code: 'japanese', name: '日本語', flag: '🇯🇵' },
    { code: 'thai', name: 'ไทย', flag: '🇹🇭' },
  ];

  useEffect(() => {
    // localStorage에서 선택된 언어 로드
    const savedLanguage = localStorage.getItem('userLanguage') || 'korean';
    setSelectedLanguage(savedLanguage);
  }, []);

  const handleSaveLanguage = async (language) => {
    setIsSaving(true);
    try {
      // Update Zustand store and i18next
      setLanguage(language);

      // 로그인했으면 계정 프로필에도 저장합니다. 비로그인이면 이 기기에만 저장돼요.
      if (isAuthenticated) {
        await settingsAPI.updateLanguage(language);
      }

      setSelectedLanguage(language);
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
    <AppLayout title="언어 선택" showBack width="narrow">
        <Card padding="none" className="overflow-hidden">
          {languages.map((lang, index) => (
            <button
              key={lang.code}
              onClick={() => handleSaveLanguage(lang.code)}
              disabled={isSaving}
              className={`w-full flex items-center justify-between p-4 transition-colors ${
                index !== languages.length - 1 ? 'border-b border-line' : ''
              } ${
                selectedLanguage === lang.code
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

              {selectedLanguage === lang.code && (
                <div className="w-6 h-6 bg-primary-600 rounded-full flex items-center justify-center">
                  <Check className="w-4 h-4 text-white" />
                </div>
              )}
            </button>
          ))}
        </Card>

        {/* 정보 메시지 */}
        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-500/10 rounded-2xl flex items-start gap-3">
          <Globe className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-blue-900 dark:text-blue-200">
            {t('settings.languageDescription')}
          </p>
        </div>
      </AppLayout>
  );
}
