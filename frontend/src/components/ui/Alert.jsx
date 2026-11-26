import { AlertCircle, CheckCircle2, Info, TriangleAlert } from 'lucide-react';
import { cn } from './cn';

const tones = {
  info: { box: 'bg-info-soft border-primary-200 dark:border-primary-500/30 text-info-ink', icon: Info },
  success: { box: 'bg-success-soft border-success/30 text-success-ink', icon: CheckCircle2 },
  warning: { box: 'bg-warning-soft border-warning/30 text-warning-ink', icon: TriangleAlert },
  danger: { box: 'bg-danger-soft border-danger/30 text-danger-ink', icon: AlertCircle },
};

/**
 * 안내·경고·오류 상자.
 * tone: info | success | warning | danger
 * title 을 주면 굵은 제목 아래 본문을 그립니다. icon={false} 로 아이콘을 뺄 수 있습니다.
 * danger 는 화면 읽기 프로그램이 바로 읽도록 role="alert", 나머지는 role="status" 입니다.
 */
export default function Alert({ tone = 'info', title, icon, className, children, ...props }) {
  const { box, icon: DefaultIcon } = tones[tone] ?? tones.info;
  const Icon = icon === false ? null : icon ?? DefaultIcon;

  return (
    <div
      role={tone === 'danger' ? 'alert' : 'status'}
      className={cn('flex items-start gap-3 rounded-control border p-4 text-sm', box, className)}
      {...props}
    >
      {Icon && <Icon className="w-5 h-5 shrink-0 mt-px" aria-hidden="true" />}
      <div className="min-w-0 flex-1">
        {title && <p className="font-semibold mb-1">{title}</p>}
        {children && <div className={cn(title && 'text-xs leading-relaxed opacity-90')}>{children}</div>}
      </div>
    </div>
  );
}
