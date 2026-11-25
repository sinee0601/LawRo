import { NavLink, useLocation } from 'react-router-dom';
import { cn } from './ui';
import { NAV_ITEMS, isNavActive } from './layout/navItems';

/** 모바일·태블릿 하단 탭. PC(lg 이상)에서는 SideNav 가 대신합니다. */
export default function BottomNav() {
  const { pathname } = useLocation();

  return (
    <nav
      className="lg:hidden fixed bottom-0 inset-x-0 bg-surface border-t border-line shadow-lg z-40 pb-[env(safe-area-inset-bottom)]"
      aria-label="주 메뉴"
    >
      <div className="max-w-xl mx-auto flex justify-around items-center h-14 sm:h-16">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const active = isNavActive(item, pathname);
          return (
            <NavLink
              key={item.path}
              to={item.path}
              aria-current={active ? 'page' : undefined}
              className={cn(
                'flex flex-col items-center justify-center flex-1 h-full transition-colors',
                active ? 'text-primary-600 dark:text-primary-400' : 'text-ink-muted hover:text-ink'
              )}
            >
              <Icon className={cn('w-5 h-5 sm:w-6 sm:h-6', active && 'fill-current')} />
              <span className="text-[10px] sm:text-xs mt-0.5 sm:mt-1 leading-tight">{item.shortLabel ?? item.label}</span>
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
}
