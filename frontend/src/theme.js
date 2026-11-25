// 테마(라이트/다크) 저장과 적용.
// index.html 의 인라인 스크립트가 첫 화면 전에 같은 규칙으로 .dark 클래스를 붙이므로,
// 여기 로직을 바꾸면 그 스크립트도 함께 맞춰 주세요.

const STORAGE_KEY = 'theme';

function prefersDark() {
  return typeof window !== 'undefined' && window.matchMedia?.('(prefers-color-scheme: dark)').matches;
}

/** 저장된 테마. 저장된 값이 없으면 기기 설정을 따릅니다. */
export function getTheme() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'light' || saved === 'dark') return saved;
  } catch {
    // 저장소를 쓸 수 없는 환경(사생활 보호 모드 등)
  }
  return prefersDark() ? 'dark' : 'light';
}

/** <html> 에 .dark 클래스와 color-scheme 을 반영합니다. */
export function applyTheme(theme) {
  const root = document.documentElement;
  root.classList.toggle('dark', theme === 'dark');
  root.style.colorScheme = theme;
  document
    .querySelector('meta[name="theme-color"]')
    ?.setAttribute('content', theme === 'dark' ? '#0f1115' : '#f9fafb');
}

/** 테마를 저장하고 바로 적용합니다. */
export function setTheme(theme) {
  try {
    localStorage.setItem(STORAGE_KEY, theme);
  } catch {
    // 저장에 실패해도 이번 세션에는 적용
  }
  applyTheme(theme);
}
