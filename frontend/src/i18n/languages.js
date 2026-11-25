// 앱이 지원하는 언어. code 는 서버(Firestore)에 저장하는 값, i18n 은 i18next·Intl 에서 쓰는 값입니다.
export const LANGUAGES = [
  { code: 'korean', i18n: 'ko', name: '한국어', flag: '🇰🇷' },
  { code: 'english', i18n: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'chinese', i18n: 'zh', name: '中文', flag: '🇨🇳' },
  { code: 'vietnamese', i18n: 'vi', name: 'Tiếng Việt', flag: '🇻🇳' },
  { code: 'japanese', i18n: 'ja', name: '日本語', flag: '🇯🇵' },
  { code: 'thai', i18n: 'th', name: 'ไทย', flag: '🇹🇭' },
];

export const DEFAULT_LANGUAGE = 'ko';

/** 'korean' 이나 'ko' 어느 쪽을 받아도 i18next 코드('ko')로 바꿉니다. 모르는 값이면 기본 언어. */
export function toI18nCode(value) {
  const found = LANGUAGES.find((l) => l.code === value || l.i18n === value);
  return found ? found.i18n : DEFAULT_LANGUAGE;
}

/** i18next 코드('ko')를 서버에 저장하는 값('korean')으로 바꿉니다. */
export function toServerCode(value) {
  const found = LANGUAGES.find((l) => l.code === value || l.i18n === value);
  return found ? found.code : 'korean';
}
