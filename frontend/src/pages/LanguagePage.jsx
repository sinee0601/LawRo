import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import useTranslation from '../hooks/useTranslation';
import { settingsAPI } from '../services/api';
import { Check, Globe } from 'lucide-react';
import MobileHeader from '../components/MobileHeader';
import BottomNav from '../components/BottomNav';

export default function LanguagePage() {
  const navigate = useNavigate();
  const { user, setLanguage } = useAuthStore();
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

      // Backend API 호출로 Firestore user profile 업데이트
      await settingsAPI.updateLanguage(language);

      setSelectedLanguage(language);
      setTimeout(() => {
        navigate('/settings');
      }, 500);
    } catch (error) {
      alert(t('common.error'));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <MobileHeader title="언어 선택" showBack={true} />

      <main className="max-w-md mx-auto px-4 pt-20 pb-8">
        <div className="bg-white rounded-3xl shadow-sm overflow-hidden">
          {languages.map((lang, index) => (
            <button
              key={lang.code}
              onClick={() => handleSaveLanguage(lang.code)}
              disabled={isSaving}
              className={`w-full flex items-center justify-between p-4 transition-colors ${
                index !== languages.length - 1 ? 'border-b border-gray-100' : ''
              } ${
                selectedLanguage === lang.code
                  ? 'bg-primary-50 hover:bg-primary-100'
                  : 'hover:bg-gray-50'
              } disabled:opacity-50`}
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{lang.flag}</span>
                <div className="text-left">
                  <p className="text-gray-900 font-medium">{lang.name}</p>
                  <p className="text-xs text-gray-500">{lang.code}</p>
                </div>
              </div>

              {selectedLanguage === lang.code && (
                <div className="w-6 h-6 bg-primary-600 rounded-full flex items-center justify-center">
                  <Check className="w-4 h-4 text-white" />
                </div>
              )}
            </button>
          ))}
        </div>

        {/* 정보 메시지 */}
        <div className="mt-6 p-4 bg-blue-50 rounded-2xl flex items-start gap-3">
          <Globe className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-blue-900">
            {t('settings.languageDescription')}
          </p>
        </div>
      </main>

      <BottomNav />
    </div>
  );
}
