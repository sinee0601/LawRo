import i18next from 'i18next';
import { toI18nCode } from './languages';

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

// 예전 버전은 'korean' 처럼 서버 코드로 저장했으므로 둘 다 받아 줍니다.
const getSavedLanguage = () => {
  try {
    return toI18nCode(localStorage.getItem('userLanguage'));
  } catch {
    return toI18nCode(null);
  }
};

// 화면 읽기 프로그램과 브라우저 번역·글꼴 선택이 올바른 언어를 쓰도록 <html lang> 을 맞춥니다.
const syncHtmlLang = (lng) => {
  if (typeof document !== 'undefined') document.documentElement.lang = lng;
};

i18next.on('languageChanged', syncHtmlLang);

i18next.init({
  resources,
  lng: getSavedLanguage(),
  fallbackLng: 'ko',
  ns: ['translation'],
  defaultNS: 'translation',
  interpolation: {
    escapeValue: false, // React 가 이미 이스케이프합니다
  },
});

syncHtmlLang(i18next.language);

export default i18next;
