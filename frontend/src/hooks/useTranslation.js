import { useEffect, useMemo, useState } from 'react';
import i18next from '../i18n/config';

/**
 * 번역 훅. 언어가 바뀌면 이 훅을 쓰는 컴포넌트가 다시 그려집니다.
 * language 는 'ko', 'en' 같은 i18next 코드라 날짜 표시(toLocaleDateString(language))에도 그대로 씁니다.
 */
export const useTranslation = () => {
  const [language, setLanguage] = useState(i18next.language);

  useEffect(() => {
    const handleLanguageChanged = (lng) => setLanguage(lng);
    i18next.on('languageChanged', handleLanguageChanged);
    // 구독 전에 언어가 바뀌었을 수도 있으니 한 번 맞춰 둡니다.
    setLanguage(i18next.language);
    return () => i18next.off('languageChanged', handleLanguageChanged);
  }, []);

  // 언어가 바뀔 때만 새 함수가 되므로 useEffect 의존성에 넣어도 안전합니다.
  const t = useMemo(() => i18next.getFixedT(language), [language]);

  return {
    t,
    language,
    i18n: i18next,
  };
};

export default useTranslation;
