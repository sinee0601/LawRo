import { NavLink, useLocation } from 'react-router-dom';
import { cn } from './ui';
import { NAV_ITEMS, isNavActive } from './layout/navItems';
import useTranslation from '../hooks/useTranslation';


/** 모바일·태블릿 하단 탭. PC(lg 이상)에서는 SideNav 가 대신합니다. */
export default function BottomNav() {
  const { pathname } = useLocation();
  const { t } = useTranslation();

  return (
    <nav
      className="lg:hidden fixed bottom-0 inset-x-0 bg-surface border-t border-line shadow-lg z-40 pb-[env(safe-area-inset-bottom)]"
      aria-label={t('common.mainMenu')}
    >
      <div className="max-w-xl mx-auto flex justify-around items-center h-16 px-1">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const active = isNavActive(item, pathname);
          return (
            <NavLink
              key={item.path}
              to={item.path}
              aria-current={active ? 'page' : undefined}
              className={cn(
                'group flex flex-col items-center justify-center gap-1 flex-1 h-full rounded-control transition-colors',
                'focus-visible:outline-none focus-visible:shadow-focus',
                active ? 'text-primary-700 dark:text-primary-300' : 'text-ink-muted hover:text-ink'
              )}
            >
              {/* 선택된 탭: 아이콘 뒤에 알약 모양 배경이 깔리고, 글자가 굵어집니다 */}
              <span
                aria-hidden="true"
                className={cn(
                  'flex items-center justify-center h-7 w-12 sm:h-8 sm:w-14 rounded-full transition-all duration-200 motion-reduce:transition-none',
                  active ? 'bg-primary-soft scale-100' : 'scale-90 group-hover:bg-surface-muted'
                )}
              >
                <Icon className="w-5 h-5 sm:w-6 sm:h-6" strokeWidth={active ? 2.4 : 2} />
              </span>
              <span className={cn('text-[10px] sm:text-xs leading-tight', active ? 'font-bold' : 'font-medium')}>
                {t(item.shortLabel ?? item.label)}
              </span>
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
}
