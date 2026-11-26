import { FileText, MessageCircle, Clock, Settings, Building2 } from 'lucide-react';

// 하단 탭(모바일)과 사이드바(PC)가 같은 메뉴를 씁니다. label 은 번역 키입니다.
// match: 이 경로들(과 그 하위 경로)에 있을 때 메뉴를 활성으로 표시합니다.
export const NAV_ITEMS = [
  { path: '/contract', icon: FileText, label: 'nav.contract', shortLabel: 'nav.contractShort', match: ['/contract', '/analysis-history'] },
  { path: '/chat', icon: MessageCircle, label: 'nav.chat' },
  { path: '/support-center', icon: Building2, label: 'nav.support', shortLabel: 'nav.supportShort' },
  { path: '/work-time', icon: Clock, label: 'nav.workTime', shortLabel: 'nav.workTimeShort' },
  {
    path: '/settings',
    icon: Settings,
    label: 'nav.settings',
    match: ['/settings', '/profile', '/change-password', '/language', '/theme', '/about', '/privacy'],
  },
];

export function isNavActive(item, pathname) {
  return (item.match || [item.path]).some((p) => pathname === p || pathname.startsWith(`${p}/`));
}
