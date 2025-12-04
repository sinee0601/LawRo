import { useNavigate, useLocation } from 'react-router-dom';
import { FileText, MessageCircle, Clock, Settings, Building2 } from 'lucide-react';

export default function BottomNav() {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { path: '/contract', icon: FileText, label: '계약서 분석' },
    { path: '/chat', icon: MessageCircle, label: '챗봇' },
    { path: '/support-center', icon: Building2, label: '지원' },
    { path: '/work-time', icon: Clock, label: '근무시간' },
    { path: '/settings', icon: Settings, label: '설정' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50">
      <div className="max-w-md mx-auto flex justify-around items-center h-16">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`flex flex-col items-center justify-center flex-1 h-full transition-colors ${
                isActive
                  ? 'text-primary-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon className={`w-6 h-6 ${isActive ? 'fill-current' : ''}`} />
              <span className="text-xs mt-1">{item.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
