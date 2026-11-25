import { useEffect } from 'react';
import { X } from 'lucide-react';
import { cn } from './cn';

const sizes = {
  md: 'sm:max-w-lg',
  lg: 'sm:max-w-2xl',
};

/**
 * 모바일에서는 아래에서 올라오는 시트, 넓은 화면(sm 이상)에서는 가운데 대화상자.
 * footer 에 버튼을 넣으면 하단에 고정됩니다 (모바일 세로, 넓은 화면 가로 배치).
 */
export default function Sheet({ title, onClose, footer, size = 'lg', children }) {
  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose?.();
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    window.addEventListener('keydown', onKey);
    return () => {
      document.body.style.overflow = prevOverflow;
      window.removeEventListener('keydown', onKey);
    };
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center sm:justify-center sm:p-6">
      <div className="absolute inset-0 bg-black/50 notify-backdrop" onClick={onClose} aria-hidden="true" />
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className={cn(
          'notify-dialog relative w-full max-h-[90vh] flex flex-col bg-surface shadow-raised',
          'rounded-t-sheet sm:rounded-card',
          sizes[size]
        )}
      >
        <div className="shrink-0 flex items-center justify-between gap-3 border-b border-line px-5 py-4">
          <h2 className="text-lg font-bold text-ink">{title}</h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="닫기"
            className="w-9 h-9 -mr-2 flex items-center justify-center rounded-full text-ink-subtle hover:bg-surface-muted hover:text-ink-muted"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="flex-1 min-h-0 overflow-y-auto p-5 sm:p-6">{children}</div>

        {footer && (
          <div className="shrink-0 border-t border-line p-4 flex flex-col gap-3 sm:flex-row-reverse sm:justify-start sm:[&>*]:w-auto">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
