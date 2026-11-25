import { FileText, MessageCircle, Clock, Settings, Building2 } from 'lucide-react';

// 하단 탭(모바일)과 사이드바(PC)가 같은 메뉴를 씁니다.
// match: 이 경로들(과 그 하위 경로)에 있을 때 메뉴를 활성으로 표시합니다.
export const NAV_ITEMS = [
  { path: '/contract', icon: FileText, label: '계약서 분석', match: ['/contract', '/analysis-history'] },
  { path: '/chat', icon: MessageCircle, label: '챗봇' },
  { path: '/support-center', icon: Building2, label: '지원 기관', shortLabel: '지원' },
  { path: '/work-time', icon: Clock, label: '근무시간' },
  {
    path: '/settings',
    icon: Settings,
    label: '설정',
    match: ['/settings', '/profile', '/change-password', '/language', '/theme', '/about', '/privacy'],
  },
];

export function isNavActive(item, pathname) {
  return (item.match || [item.path]).some((p) => pathname === p || pathname.startsWith(`${p}/`));
}
