import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { LogIn, LogOut } from 'lucide-react';
import useAuthStore from '../../store/authStore';
import { cn } from '../ui';
import { NAV_ITEMS, isNavActive } from './navItems';
import { loginPath } from '../../services/authRedirect';
import useTranslation from '../../hooks/useTranslation';


/** PC(lg 이상)에서 왼쪽에 고정되는 메뉴. 모바일에서는 BottomNav 가 대신합니다. */
export default function SideNav() {
  const { pathname, search } = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuthStore();
  const { t } = useTranslation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="hidden lg:flex fixed inset-y-0 left-0 z-40 w-64 flex-col bg-surface border-r border-line">
      <NavLink to="/contract" className="flex items-center gap-3 h-16 px-6 border-b border-line">
        <span className="w-9 h-9 rounded-control bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold">
          LR
        </span>
        <span className="text-lg font-bold text-ink">LawRo</span>
      </NavLink>

      <nav className="flex-1 overflow-y-auto p-3 space-y-1" aria-label={t('common.mainMenu')}>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const active = isNavActive(item, pathname);
          return (
            <NavLink
              key={item.path}
              to={item.path}
              aria-current={active ? 'page' : undefined}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-control text-sm font-medium transition-colors',
                active
                  ? 'bg-primary-soft text-primary-700 dark:text-primary-300'
                  : 'text-ink-muted hover:bg-surface-muted hover:text-ink'
              )}
            >
              <Icon className="w-5 h-5 shrink-0" />
              {t(item.label)}
            </NavLink>
          );
        })}
      </nav>

      <div className="p-3 border-t border-line">
        {isAuthenticated ? (
          <>
            {user?.email && <p className="px-3 pb-2 text-xs text-ink-subtle truncate">{user.email}</p>}
            <button
              type="button"
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-control text-sm font-medium text-ink-muted hover:bg-surface-muted hover:text-ink transition-colors"
            >
              <LogOut className="w-5 h-5 shrink-0" />
              {t('common.logout')}
            </button>
          </>
        ) : (
          <>
            <p className="px-3 pb-3 text-xs text-ink-muted leading-relaxed">
              {t('nav.guestHint')}
            </p>
            <NavLink
              to={loginPath(`${pathname}${search}`)}
              className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-control text-sm font-semibold bg-primary text-primary-foreground hover:bg-primary-hover transition-colors"
            >
              <LogIn className="w-4 h-4 shrink-0" />
              {t('common.login')}
            </NavLink>
          </>
        )}
      </div>
    </aside>
  );
}
