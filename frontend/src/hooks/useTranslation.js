import { useEffect, useState } from 'react';
import i18next from '../i18n/config';

/**
 * Custom hook for translation
 * Wraps i18next.t() function with component re-render on language change
 * @returns {Object} Translation object with t function and current language
 */
export const useTranslation = () => {
  const [language, setLanguage] = useState(i18next.language);

  useEffect(() => {
    // Listen for language changes
    const handleLanguageChanged = (lng) => {
      setLanguage(lng);
    };

    i18next.on('languageChanged', handleLanguageChanged);

    // Cleanup
    return () => {
      i18next.off('languageChanged', handleLanguageChanged);
    };
  }, []);

  return {
    t: i18next.t.bind(i18next),
    language,
    changeLanguage: (lng) => {
      i18next.changeLanguage(lng);
      localStorage.setItem('userLanguage', lng);
      // Map language code to Firestore compatible format if needed
      const languageMap = {
        'ko': 'korean',
        'en': 'english',
        'zh': 'chinese',
        'vi': 'vietnamese',
        'ja': 'japanese',
        'th': 'thai'
      };
      return languageMap[lng] || lng;
    },
    i18n: i18next,
  };
};

export default useTranslation;
