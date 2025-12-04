import i18next from 'i18next';

// Import all language locale files
import ko from './locales/ko.json';
import en from './locales/en.json';
import zh from './locales/zh.json';
import vi from './locales/vi.json';
import ja from './locales/ja.json';
import th from './locales/th.json';

const resources = {
  ko: { translation: ko },
  en: { translation: en },
  zh: { translation: zh },
  vi: { translation: vi },
  ja: { translation: ja },
  th: { translation: th },
};

// Get initial language from localStorage
// Map Firestore language codes to i18next codes if needed
const getSavedLanguage = () => {
  const saved = localStorage.getItem('userLanguage');
  if (!saved) return 'ko'; // Default to Korean

  const codeMap = {
    'korean': 'ko',
    'english': 'en',
    'chinese': 'zh',
    'vietnamese': 'vi',
    'japanese': 'ja',
    'thai': 'th'
  };

  return codeMap[saved] || saved;
};

// Initialize i18next
i18next.init({
  resources,
  lng: getSavedLanguage(),
  fallbackLng: 'ko',
  ns: ['translation'],
  defaultNS: 'translation',
  interpolation: {
    escapeValue: false, // React already escapes values
  },
});

export default i18next;
