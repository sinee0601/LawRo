import { cn } from './cn';

/** 목록이 비었을 때 보여 주는 안내. icon, title, description, action(버튼 등) 을 받습니다. */
export default function EmptyState({ icon: Icon, title, description, action, className }) {
  return (
    <div className={cn('flex flex-col items-center text-center py-8 px-4', className)}>
      {Icon && (
        <span className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-surface-muted text-ink-subtle">
          <Icon className="w-8 h-8" aria-hidden="true" />
        </span>
      )}
      {title && <p className="font-medium text-ink">{title}</p>}
      {description && <p className="mt-1.5 text-sm text-ink-muted max-w-sm">{description}</p>}
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
