import { cn } from './cn';
import i18next from '../../i18n/config';

const sizes = {
  sm: 'w-4 h-4 border-2',
  md: 'w-8 h-8 border-[3px]',
  lg: 'w-12 h-12 border-4',
};

/** 돌아가는 원. label 은 화면 읽기 프로그램에만 읽힙니다 (기본: "불러오는 중"). */
export default function Spinner({ size = 'md', label, className }) {
  return (
    <span role="status" className={cn('inline-flex', className)}>
      <span
        aria-hidden="true"
        className={cn(
          'animate-spin rounded-full border-primary-200 border-t-primary-600',
          'dark:border-primary-500/25 dark:border-t-primary-400',
          sizes[size]
        )}
      />
      <span className="sr-only">{label ?? i18next.t('common.loading')}</span>
    </span>
  );
}

/** 화면이나 영역 가운데에 스피너와 안내 문구를 함께 보여 줍니다. */
export function LoadingState({ label, size = 'md', fullScreen = false, className }) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center gap-4 text-center',
        fullScreen ? 'min-h-screen bg-canvas' : 'py-20',
        className
      )}
    >
      <Spinner size={size} label={label} />
      {label && <p className="text-sm text-ink-muted" aria-hidden="true">{label}</p>}
    </div>
  );
}
