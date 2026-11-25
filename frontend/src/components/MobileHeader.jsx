import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function MobileHeader({ title, showBack = false }) {
  const navigate = useNavigate();

  return (
    <header className="fixed top-0 left-0 right-0 bg-surface border-b border-line shadow-sm z-40">
      <div className="max-w-md mx-auto flex items-center justify-between h-14 px-4">
        {showBack ? (
          <button
            onClick={() => navigate(-1)}
            className="p-2 -ml-2 hover:bg-surface-muted rounded-full transition-colors"
          >
            <ArrowLeft className="w-6 h-6 text-ink-muted" />
          </button>
        ) : (
          <div className="w-10" />
        )}

        <h1 className="text-lg font-bold text-ink">{title}</h1>

        <div className="w-10" />
      </div>
    </header>
  );
}
