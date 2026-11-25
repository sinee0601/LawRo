/** @type {import('tailwindcss').Config} */

// 색상 값은 src/index.css 의 :root CSS 변수에 정의되어 있습니다.
// 변수를 "R G B" 채널로 두었기 때문에 bg-primary-600/50 같은 투명도 문법도 그대로 동작합니다.
const withAlpha = (name) => `rgb(var(--color-${name}) / <alpha-value>)`;

const primaryScale = Object.fromEntries(
  [50, 100, 200, 300, 400, 500, 600, 700, 800, 900].map((step) => [
    step,
    withAlpha(`primary-${step}`),
  ])
);

export default {
  // <html class="dark"> 일 때 dark: 변형과 .dark 토큰이 적용됩니다 (src/theme.js).
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          ...primaryScale,
          DEFAULT: withAlpha('primary-600'),
          hover: withAlpha('primary-700'),
          soft: withAlpha('primary-soft'),
          foreground: withAlpha('on-primary'),
        },
        canvas: withAlpha('canvas'),
        surface: {
          DEFAULT: withAlpha('surface'),
          muted: withAlpha('surface-muted'),
        },
        line: {
          DEFAULT: withAlpha('line'),
          strong: withAlpha('line-strong'),
        },
        ink: {
          DEFAULT: withAlpha('ink'),
          muted: withAlpha('ink-muted'),
          subtle: withAlpha('ink-subtle'),
        },
        danger: {
          DEFAULT: withAlpha('danger'),
          hover: withAlpha('danger-hover'),
          soft: withAlpha('danger-soft'),
        },
        success: {
          DEFAULT: withAlpha('success'),
          soft: withAlpha('success-soft'),
        },
        warning: {
          DEFAULT: withAlpha('warning'),
          soft: withAlpha('warning-soft'),
        },
      },
      borderRadius: {
        control: 'var(--radius-control)',
        card: 'var(--radius-card)',
        sheet: 'var(--radius-sheet)',
      },
      boxShadow: {
        card: 'var(--shadow-card)',
        raised: 'var(--shadow-raised)',
        focus: 'var(--shadow-focus)',
      },
    },
  },
  plugins: [],
}
