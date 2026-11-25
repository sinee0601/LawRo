import { useId } from 'react';
import { cn } from './cn';

const base =
  'w-full text-ink placeholder:text-ink-subtle outline-none transition-shadow ' +
  'focus:shadow-focus disabled:opacity-60 disabled:cursor-not-allowed';

const variants = {
  // 흰 배경 + 테두리 (폼)
  outline: 'bg-surface border border-line-strong rounded-control px-4 py-3 focus:border-primary-500',
  // 회색 배경, 테두리 없음 (채팅 입력창 등)
  filled: 'bg-surface-muted border border-transparent rounded-2xl px-4 py-2.5 text-sm focus:bg-surface focus:border-primary-500',
};

function Field({ label, hint, id, children }) {
  if (!label && !hint) return children;
  return (
    <div>
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-ink mb-2">
          {label}
        </label>
      )}
      {children}
      {hint && <p className="mt-2 text-xs text-ink-muted">{hint}</p>}
    </div>
  );
}

/** 한 줄 입력창. label, hint 를 주면 라벨과 도움말을 함께 그립니다. */
export default function Input({ variant = 'outline', label, hint, id, className, ...props }) {
  const autoId = useId();
  const inputId = id || autoId;
  return (
    <Field label={label} hint={hint} id={inputId}>
      <input id={inputId} className={cn(base, variants[variant], className)} {...props} />
    </Field>
  );
}

/** 여러 줄 입력창. Input 과 같은 variant 를 씁니다. */
export function Textarea({ variant = 'outline', label, hint, id, className, ...props }) {
  const autoId = useId();
  const inputId = id || autoId;
  return (
    <Field label={label} hint={hint} id={inputId}>
      <textarea id={inputId} className={cn(base, variants[variant], className)} {...props} />
    </Field>
  );
}
