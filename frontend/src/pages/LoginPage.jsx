import { useState } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { Info } from 'lucide-react';
import useAuthStore from '../store/authStore';
import { Button, Input } from '../components/ui';
import { safeNext, signupPath } from '../services/authRedirect';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, isLoading, error, clearError, initializeLanguage } = useAuthStore();
  const [searchParams] = useSearchParams();
  // 로그인이 필요한 기능에서 넘어왔다면 로그인 후 그 화면으로 돌아갑니다.
  const nextParam = searchParams.get('next');
  const next = safeNext(nextParam);

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    clearError();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = await login(formData);
      // Initialize user's preferred language on login
      if (data.user) {
        initializeLanguage(data.user);
      }
      navigate(next, { replace: true });
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  return (
    <div className="min-h-screen bg-surface sm:bg-canvas flex flex-col">
      <main className="flex-1 flex flex-col justify-center w-full max-w-sm mx-auto px-6 py-12 sm:max-w-md sm:px-0">
        <div className="sm:bg-surface sm:rounded-card sm:shadow-card sm:p-10">
          {/* 브랜드 */}
          <div className="mb-10">
            <div className="w-12 h-12 rounded-2xl bg-primary flex items-center justify-center mb-6">
              <span className="text-2xl font-bold text-primary-foreground leading-none">L</span>
            </div>
            <h1 className="text-2xl font-bold text-ink tracking-tight">LawRo에 오신 것을 환영해요</h1>
            <p className="mt-2 text-[15px] text-ink-muted leading-relaxed">
              외국인 노동자를 위한 AI 법률 상담 서비스
            </p>
          </div>

          {nextParam && (
            <div className="mb-5 flex items-start gap-2 p-3 bg-primary-soft text-primary-800 dark:text-primary-200 rounded-control text-sm">
              <Info className="w-4 h-4 mt-0.5 shrink-0" aria-hidden="true" />
              <p>로그인이 필요한 기능이에요. 로그인하면 보던 화면으로 바로 돌아가요.</p>
            </div>
          )}

          {error && (
            <div
              role="alert"
              className="mb-5 p-3 bg-danger-soft border border-red-200 dark:border-red-500/30 text-red-700 dark:text-red-300 rounded-control text-sm"
            >
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              type="email"
              id="email"
              name="email"
              label="이메일"
              autoComplete="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="your@email.com"
              required
            />

            <div>
              <Input
                type="password"
                id="password"
                name="password"
                label="비밀번호"
                autoComplete="current-password"
                value={formData.password}
                onChange={handleChange}
                placeholder="비밀번호를 입력하세요"
                required
              />
              <div className="mt-2 text-right">
                <Link
                  to="/forgot-password"
                  className="text-sm text-ink-muted hover:text-primary-700 dark:hover:text-primary-300"
                >
                  비밀번호를 잊으셨나요?
                </Link>
              </div>
            </div>

            <Button type="submit" size="xl" fullWidth disabled={isLoading}>
              {isLoading ? '로그인 중...' : '로그인'}
            </Button>
          </form>

          <div className="flex items-center gap-4 my-8">
            <div className="flex-1 border-t border-line" />
            <span className="text-sm text-ink-subtle">또는 간편 로그인</span>
            <div className="flex-1 border-t border-line" />
          </div>

          <div className="flex justify-center gap-4">
            <button
              type="button"
              aria-label="카카오로 로그인"
              className="w-12 h-12 rounded-full bg-[#FEE500] flex items-center justify-center hover:brightness-95 transition focus-visible:outline-none focus-visible:shadow-focus"
            >
              <svg className="w-6 h-6" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  fill="#191919"
                  d="M12 3.5c-5.25 0-9.5 3.33-9.5 7.44 0 2.66 1.78 4.99 4.46 6.31l-.91 3.33c-.08.3.26.54.52.37l3.96-2.62c.48.05.97.08 1.47.08 5.25 0 9.5-3.33 9.5-7.44S17.25 3.5 12 3.5z"
                />
              </svg>
            </button>
            <button
              type="button"
              aria-label="Google로 로그인"
              className="w-12 h-12 rounded-full bg-surface border border-line-strong flex items-center justify-center hover:bg-surface-muted transition-colors focus-visible:outline-none focus-visible:shadow-focus"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" aria-hidden="true">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
            </button>
            <button
              type="button"
              aria-label="네이버로 로그인"
              className="w-12 h-12 rounded-full bg-[#03C75A] flex items-center justify-center hover:brightness-95 transition focus-visible:outline-none focus-visible:shadow-focus"
            >
              <span className="text-lg font-extrabold text-white leading-none">N</span>
            </button>
          </div>

          <p className="mt-10 text-center text-sm text-ink-muted">
            아직 계정이 없으신가요?{' '}
            <Link
              to={signupPath(nextParam)}
              className="font-semibold text-primary-700 hover:text-primary-800 dark:text-primary-300 dark:hover:text-primary-200"
            >
              회원가입
            </Link>
          </p>
          <p className="mt-3 text-center text-sm">
            <Link to="/contract" className="text-ink-muted underline-offset-4 hover:text-ink hover:underline">
              로그인 없이 둘러보기
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}
