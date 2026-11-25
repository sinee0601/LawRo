import { cn } from './cn';

const base =
  'inline-flex items-center justify-center gap-2 whitespace-nowrap transition-colors ' +
  'focus-visible:outline-none focus-visible:shadow-focus ' +
  'disabled:pointer-events-none disabled:opacity-50';

const variants = {
  primary: 'bg-primary text-primary-foreground hover:bg-primary-hover',
  secondary:
    'bg-primary-100 text-primary-700 hover:bg-primary-200 ' +
    'dark:bg-primary-500/20 dark:text-primary-200 dark:hover:bg-primary-500/30',
  outline: 'bg-surface text-ink border border-line-strong hover:bg-surface-muted',
  ghost: 'bg-transparent text-ink-muted hover:bg-surface-muted hover:text-ink',
  danger: 'bg-danger text-white hover:bg-danger-hover',
};

const sizes = {
  sm: 'px-4 py-2 text-sm font-medium',
  md: 'px-5 py-2.5 text-sm font-medium',
  lg: 'px-6 py-3 text-base font-medium',
  xl: 'px-6 py-4 text-base font-semibold',
  icon: 'w-10 h-10 p-0',
};

/**
 * 공통 버튼.
 * variant: primary | secondary | outline | ghost | danger
 * size: sm | md | lg | xl | icon
 * pill: 모서리를 완전히 둥글게 (아이콘 버튼, 플로팅 버튼)
 */
export default function Button({
  variant = 'primary',
  size = 'md',
  pill = false,
  fullWidth = false,
  type = 'button',
  className,
  children,
  ...props
}) {
  return (
    <button
      type={type}
      className={cn(
        base,
        variants[variant],
        sizes[size],
        pill ? 'rounded-full' : 'rounded-control',
        fullWidth && 'w-full',
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
