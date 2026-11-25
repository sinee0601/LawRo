import { useEffect, useRef } from 'react';
import { CheckCircle2, XCircle, Info, AlertTriangle, X } from 'lucide-react';
import useNotifyStore from '../../store/notifyStore';
import { Button, cn } from '../ui';

const toastStyles = {
  success: { icon: CheckCircle2, color: 'text-success' },
  error: { icon: XCircle, color: 'text-danger' },
  warning: { icon: AlertTriangle, color: 'text-warning' },
  info: { icon: Info, color: 'text-primary' },
};

function ToastViewport() {
  const toasts = useNotifyStore((s) => s.toasts);
  const dismiss = useNotifyStore((s) => s.dismissToast);

  return (
    // 하단 내비게이션(BottomNav) 위에 뜨도록 bottom 여백을 둡니다.
    <div
      aria-live="polite"
      className="pointer-events-none fixed inset-x-0 bottom-24 z-[60] flex flex-col items-center gap-2 px-4"
    >
      {toasts.map((t) => {
        const { icon: Icon, color } = toastStyles[t.type] || toastStyles.info;
        return (
          <div
            key={t.id}
            role={t.type === 'error' ? 'alert' : 'status'}
            className="notify-toast pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-control border border-line bg-surface px-4 py-3 text-sm text-ink shadow-raised"
          >
            <Icon className={cn('mt-0.5 h-5 w-5 shrink-0', color)} aria-hidden="true" />
            <p className="flex-1 whitespace-pre-line leading-relaxed">{t.message}</p>
            <button
              type="button"
              onClick={() => dismiss(t.id)}
              aria-label="알림 닫기"
              className="-mr-1 shrink-0 rounded-full p-1 text-ink-subtle hover:bg-surface-muted hover:text-ink"
              style={{ minHeight: 0 }}
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
}

function ConfirmDialog() {
  const dialog = useNotifyStore((s) => s.dialog);
  const close = useNotifyStore((s) => s.closeDialog);
  const confirmRef = useRef(null);

  useEffect(() => {
    if (!dialog) return;
    const previous = document.activeElement;
    confirmRef.current?.focus();
    const onKey = (e) => {
      if (e.key === 'Escape') close(false);
    };
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('keydown', onKey);
      previous?.focus?.();
    };
  }, [dialog, close]);

  if (!dialog) return null;
  const { title, message, confirmText, cancelText, tone } = dialog;

  return (
    <div className="fixed inset-0 z-[70] flex items-end justify-center sm:items-center">
      <div className="notify-backdrop absolute inset-0 bg-black/40" onClick={() => close(false)} />
      <div
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="notify-dialog-title"
        aria-describedby={message ? 'notify-dialog-message' : undefined}
        className="notify-dialog relative w-full max-w-sm rounded-t-sheet bg-surface p-6 shadow-raised sm:mx-4 sm:rounded-card"
      >
        <h2 id="notify-dialog-title" className="text-lg font-semibold text-ink">
          {title}
        </h2>
        {message && (
          <p id="notify-dialog-message" className="mt-2 whitespace-pre-line text-sm leading-relaxed text-ink-muted">
            {message}
          </p>
        )}
        <div className="mt-6 flex gap-2">
          {cancelText && (
            <Button variant="outline" fullWidth onClick={() => close(false)}>
              {cancelText}
            </Button>
          )}
          <Button
            ref={confirmRef}
            variant={tone === 'danger' ? 'danger' : 'primary'}
            fullWidth
            onClick={() => close(true)}
          >
            {confirmText}
          </Button>
        </div>
      </div>
    </div>
  );
}

/** 앱 최상단에 한 번만 둡니다. */
export default function NotificationHost() {
  return (
    <>
      <ToastViewport />
      <ConfirmDialog />
    </>
  );
}
