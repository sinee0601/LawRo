import { cn } from '../ui';
import BottomNav from '../BottomNav';
import SideNav from './SideNav';
import AppHeader from './AppHeader';
import useTranslation from '../../hooks/useTranslation';

// 본문 최대 폭. 폼·설정은 narrow, 목록·대시보드는 wide.
const widths = {
  narrow: 'max-w-2xl',
  default: 'max-w-4xl',
  wide: 'max-w-6xl',
};

/**
 * 로그인 후 모든 화면이 쓰는 공통 틀.
 * - 모바일: 상단 제목줄 + 하단 탭(BottomNav)
 * - PC(lg, 1024px 이상): 왼쪽 사이드바(SideNav) + 상단 제목줄, 하단 탭 없음
 *
 * fill: 본문이 화면 높이를 꽉 채우고 스스로 스크롤합니다 (챗봇처럼 입력창이 아래 붙는 화면).
 */
export default function AppLayout({
  title,
  subtitle,
  showBack = false,
  leading,
  actions,
  width = 'default',
  fill = false,
  className,
  children,
}) {
  const container = widths[width] ?? widths.default;
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-canvas">
      {/* 키보드 사용자가 메뉴를 건너뛰고 본문으로 바로 갈 수 있는 링크 (Tab 을 누르면 보입니다) */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-[60] focus:px-4 focus:py-2 focus:rounded-control focus:bg-primary focus:text-primary-foreground focus:shadow-raised"
      >
        {t('common.skipToContent')}
      </a>
      <SideNav />

      <div className={cn('lg:pl-64', fill && 'h-dvh flex flex-col')}>
        <AppHeader
          title={title}
          subtitle={subtitle}
          showBack={showBack}
          leading={leading}
          actions={actions}
          containerClassName={fill ? undefined : container}
        />

        {fill ? (
          <main id="main-content" tabIndex={-1} className={cn('flex-1 min-h-0 flex pb-16 lg:pb-0 focus:outline-none', className)}>{children}</main>
        ) : (
          <main
            id="main-content"
            tabIndex={-1}
            className={cn(
              'focus:outline-none',
              'mx-auto w-full px-4 sm:px-6 lg:px-8 pt-6 lg:pt-8 pb-24 lg:pb-12',
              container,
              className
            )}
          >
            {children}
          </main>
        )}
      </div>

      <BottomNav />
    </div>
  );
}
