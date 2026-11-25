import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { cn } from '../ui';
import useTranslation from '../../hooks/useTranslation';


/**
 * 화면 상단 제목줄. 스크롤해도 위에 붙어 있습니다.
 * 모바일: 가운데 제목 + 왼쪽 뒤로가기. PC: 왼쪽 정렬된 큰 제목 + 오른쪽 actions.
 * leading 을 주면 뒤로가기 버튼 자리에 대신 그립니다 (예: 챗봇의 대화 목록 버튼). 모바일 전용이라 PC 에서는 숨깁니다.
 */
export default function AppHeader({ title, subtitle, showBack = false, leading, actions, containerClassName }) {
  const navigate = useNavigate();
  const { t } = useTranslation();

  const left = leading ?? (showBack ? (
    <button
      type="button"
      onClick={() => navigate(-1)}
      aria-label={t('common.back')}
      className="w-10 h-10 -ml-2 flex items-center justify-center rounded-full text-ink-muted hover:bg-surface-muted transition-colors"
    >
      <ArrowLeft className="w-6 h-6" />
    </button>
  ) : null);

  return (
    <header className="sticky top-0 z-30 bg-surface/90 backdrop-blur border-b border-line">
      <div className={cn('mx-auto flex items-center gap-2 h-14 lg:h-16 px-4 sm:px-6 lg:px-8', containerClassName)}>
        {/* 모바일에서는 제목이 가운데 오도록 양쪽 폭을 맞춥니다 */}
        <div className={cn('w-10 shrink-0 flex items-center', (!left || leading) && 'lg:hidden')}>{left}</div>

        <div className="flex-1 min-w-0 text-center lg:text-left">
          <h1 className="text-lg lg:text-xl font-bold text-ink truncate">{title}</h1>
          {subtitle && <p className="hidden lg:block text-xs text-ink-muted truncate">{subtitle}</p>}
        </div>

        <div className={cn('shrink-0 flex items-center justify-end gap-2', actions ? 'min-w-10' : 'w-10 lg:hidden')}>
          {actions}
        </div>
      </div>
    </header>
  );
}
