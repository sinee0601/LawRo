import { useState } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { toast } from '../store/notifyStore';
import { ArrowLeft } from 'lucide-react';
import { Alert, Button, Input, cn } from '../components/ui';
import { loginPath, safeNext } from '../services/authRedirect';
import useTranslation from '../hooks/useTranslation';
import { LANGUAGES, toServerCode } from '../i18n/languages';

const EMAIL_DOMAINS = ['gmail.com', 'naver.com', 'kakao.com'];

// 가입 시 실제로 검사하는 규칙 (Firebase Auth 최소 길이와 같음)
const MIN_PASSWORD_LENGTH = 6;

export default function SignupPage() {
  const navigate = useNavigate();
  const { signup, isLoading, error, clearError, initializeLanguage, setLanguage } = useAuthStore();
  const [searchParams] = useSearchParams();
  const nextParam = searchParams.get('next');
  const { t, language } = useTranslation();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    // 지금 앱에서 쓰는 언어를 기본으로 고릅니다.
    preferred_language: toServerCode(language),
  });

  const [validationError, setValidationError] = useState('');
  const passwordOk = formData.password.length >= MIN_PASSWORD_LENGTH;

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    clearError();
    setValidationError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // 비밀번호 확인
    if (formData.password !== formData.confirmPassword) {
      setValidationError(t('auth.signup.passwordMismatch'));
      return;
    }

    // 비밀번호 길이 확인
    if (!passwordOk) {
      setValidationError(t('auth.signup.passwordMinError', { min: MIN_PASSWORD_LENGTH }));
      return;
    }

    try {
      const data = await signup({
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        preferred_language: formData.preferred_language,
      });
      // 가입하면 바로 로그인된 상태가 되므로, 로그인이 필요해 넘어왔던 화면(없으면 첫 화면)으로 갑니다.
      if (data?.user) initializeLanguage(data.user);
      toast.success(t('auth.signup.success'));
      navigate(safeNext(nextParam), { replace: true });
    } catch (err) {
      console.error('Signup failed:', err);
    }
  };

  const emailLocal = formData.email.split('@')[0];
  const emailDomain = formData.email.includes('@') ? formData.email.split('@').slice(1).join('@') : '';
  const knownDomain = EMAIL_DOMAINS.includes(emailDomain) ? emailDomain : '';

  // 도메인을 고르면 '@' 앞부분은 그대로 두고 뒤만 바꿉니다.
  const handleDomainChange = (e) => {
    const domain = e.target.value;
    if (!domain) return;
    setFormData({ ...formData, email: `${emailLocal}@${domain}` });
    clearError();
    setValidationError('');
  };

  return (
    <div className="min-h-screen bg-surface sm:bg-canvas">
      <main className="w-full max-w-sm mx-auto px-6 py-8 sm:max-w-md sm:px-0 sm:py-12">
        <div className="flex items-center gap-2 mb-8">
          <Link
            to={loginPath(nextParam)}
            aria-label={t('auth.signup.backToLogin')}
            className="w-10 h-10 -ml-2 flex items-center justify-center rounded-full text-ink-muted hover:bg-surface-muted hover:text-ink"
          >
            <ArrowLeft className="w-6 h-6" />
          </Link>
          <h1 className="text-2xl font-bold text-ink tracking-tight">{t('auth.signup.title')}</h1>
        </div>

        <div className="sm:bg-surface sm:rounded-card sm:shadow-card sm:p-10 space-y-6">
          {(error || validationError) && (
            <Alert tone="danger">{error || validationError}</Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              type="text"
              id="full_name"
              name="full_name"
              label={t('auth.signup.name')}
              autoComplete="name"
              value={formData.full_name}
              onChange={handleChange}
              placeholder={t('auth.signup.namePlaceholder')}
              required
            />

            <fieldset>
              <legend className="block text-sm font-medium text-ink mb-2">{t('auth.signup.language')}</legend>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {LANGUAGES.map((lang) => (
                  <button
                    key={lang.code}
                    type="button"
                    aria-pressed={formData.preferred_language === lang.code}
                    onClick={() => {
                      setFormData({ ...formData, preferred_language: lang.code });
                      // 고른 언어로 바로 화면을 바꿔 나머지 항목을 읽기 쉽게 합니다.
                      setLanguage(lang.code);
                    }}
                    className={cn(
                      'px-3 py-3 rounded-control font-medium transition-colors flex items-center justify-center gap-2 min-w-0',
                      formData.preferred_language === lang.code
                        ? 'bg-primary text-primary-foreground ring-2 ring-primary-300 dark:ring-primary-500/50'
                        : 'bg-surface-muted text-ink-muted hover:bg-line'
                    )}
                  >
                    <span className="text-lg">{lang.flag}</span>
                    <span className="text-xs truncate">{lang.name}</span>
                  </button>
                ))}
              </div>
            </fieldset>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-ink mb-2">
                {t('auth.signup.email')}
              </label>
              {/* 좁은 화면에서도 넘치지 않도록 입력창은 줄어들고 도메인 선택은 고정 폭 */}
              <div className="flex gap-2">
                <Input
                  type="email"
                  id="email"
                  name="email"
                  autoComplete="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="min-w-0"
                  placeholder={t('auth.signup.emailPlaceholder')}
                  required
                />
                <select
                  aria-label={t('auth.signup.emailDomain')}
                  value={knownDomain}
                  onChange={handleDomainChange}
                  className="w-32 sm:w-36 shrink-0 px-3 py-3 text-sm text-ink border border-line-strong rounded-control outline-none focus:shadow-focus focus:border-primary-500"
                >
                  <option value="">{t('auth.signup.customDomain')}</option>
                  {EMAIL_DOMAINS.map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
              </div>
              {formData.email && !formData.email.includes('@') && (
                <p className="text-sm text-warning mt-1">{t('auth.signup.emailFormat')}</p>
              )}
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label htmlFor="verify_code" className="text-sm font-medium text-ink">
                  {t('auth.signup.code')}
                </label>
                <button
                  type="button"
                  onClick={() => toast.info(t('auth.signup.codeComingSoon'))}
                  className="text-primary-600 dark:text-primary-400 text-sm font-medium"
                >
                  {t('auth.signup.sendCode')}
                </button>
              </div>
              {/* 인증 API 가 아직 없어서 '인증 완료' 상태를 보여주지 않는다. 연동되면 실제 결과로 표시할 것. */}
              <Input
                type="text"
                inputMode="numeric"
                id="verify_code"
                name="verify_code"
                placeholder={t('auth.signup.codePlaceholder')}
                hint={t('auth.signup.codeHint')}
              />
            </div>

            <div>
              <Input
                type="password"
                id="password"
                name="password"
                label={t('auth.signup.password')}
                autoComplete="new-password"
                value={formData.password}
                onChange={handleChange}
                placeholder={t('auth.signup.passwordPlaceholder', { min: MIN_PASSWORD_LENGTH })}
                required
              />
              {formData.password && (
                passwordOk ? (
                  <p className="text-sm text-success mt-1">{t('auth.signup.passwordOk')}</p>
                ) : (
                  <p className="text-sm text-warning mt-1">
                    {t('auth.signup.passwordTooShort', { min: MIN_PASSWORD_LENGTH, current: formData.password.length })}
                  </p>
                )
              )}
            </div>

            <div>
              <Input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                label={t('auth.signup.confirmPassword')}
                autoComplete="new-password"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder={t('auth.signup.confirmPlaceholder')}
                required
              />
              {formData.confirmPassword && (
                formData.password === formData.confirmPassword ? (
                  <p className="text-sm text-success mt-1">{t('auth.signup.passwordMatch')}</p>
                ) : (
                  <p className="text-sm text-warning mt-1">{t('auth.signup.passwordMismatch')}</p>
                )
              )}
            </div>

            <Button type="submit" size="xl" fullWidth disabled={isLoading} className="mt-6">
              {isLoading ? t('auth.signup.submitting') : t('auth.signup.submit')}
            </Button>
          </form>

          <p className="text-center text-sm text-ink-muted">
            {t('auth.signup.haveAccount')}{' '}
            <Link to={loginPath(nextParam)} className="font-medium text-primary-600 dark:text-primary-400 hover:underline">
              {t('auth.signup.loginLink')}
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}
