import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { settingsAPI } from '../services/api';
import { Lock, Eye, EyeOff, AlertCircle, CheckCircle } from 'lucide-react';
import { Card } from '../components/ui';
import AppLayout from '../components/layout/AppLayout';
import useTranslation from '../hooks/useTranslation';

const MIN_PASSWORD_LENGTH = 8;

export default function ChangePasswordPage() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { t } = useTranslation();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const validatePassword = () => {
    if (!currentPassword) {
      setError(t('password.currentRequired'));
      return false;
    }
    if (!newPassword) {
      setError(t('password.newRequired'));
      return false;
    }
    if (newPassword.length < MIN_PASSWORD_LENGTH) {
      setError(t('password.tooShort', { min: MIN_PASSWORD_LENGTH }));
      return false;
    }
    if (newPassword !== confirmPassword) {
      setError(t('password.mismatch'));
      return false;
    }
    if (currentPassword === newPassword) {
      setError(t('password.sameAsCurrent'));
      return false;
    }
    return true;
  };

  const handleChangePassword = async () => {
    setError('');
    if (!validatePassword()) return;

    setIsLoading(true);
    try {
      await settingsAPI.changePassword(user.email, currentPassword, newPassword);
      setSuccess(true);
      setTimeout(() => {
        navigate('/settings');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || t('password.failed'));
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <AppLayout title={t('password.title')} showBack width="narrow">
        <div className="flex flex-col items-center justify-center text-center py-20">
          <CheckCircle className="w-16 h-16 text-green-600 dark:text-green-400 mb-4" />
          <p className="text-lg font-bold text-ink mb-2">{t('password.successTitle')}</p>
          <p className="text-sm text-ink-muted">{t('password.successBody')}</p>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout title={t('password.title')} showBack width="narrow">
        <Card className="mb-6">
          <p className="text-sm text-ink-muted mb-6">
            {t('password.intro')}
          </p>

          {/* 에러 메시지 */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 text-red-700 dark:text-red-300 rounded-xl flex items-start gap-2">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          {/* 현재 비밀번호 */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-ink-muted mb-2">{t('password.current')}</label>
            <div className="relative">
              <input
                type={showPasswords.current ? 'text' : 'password'}
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="w-full px-4 py-3 pr-10 border border-line-strong rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                placeholder={t('password.currentPlaceholder')}
              />
              <button
                type="button"
                aria-label={showPasswords.current ? t('password.hide') : t('password.show')}
                onClick={() =>
                  setShowPasswords({ ...showPasswords, current: !showPasswords.current })
                }
                className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-subtle hover:text-ink-muted"
              >
                {showPasswords.current ? (
                  <EyeOff className="w-5 h-5" />
                ) : (
                  <Eye className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>

          {/* 새 비밀번호 */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-ink-muted mb-2">{t('password.new')}</label>
            <div className="relative">
              <input
                type={showPasswords.new ? 'text' : 'password'}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full px-4 py-3 pr-10 border border-line-strong rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                placeholder={t('password.newPlaceholder', { min: MIN_PASSWORD_LENGTH })}
              />
              <button
                type="button"
                aria-label={showPasswords.new ? t('password.hide') : t('password.show')}
                onClick={() =>
                  setShowPasswords({ ...showPasswords, new: !showPasswords.new })
                }
                className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-subtle hover:text-ink-muted"
              >
                {showPasswords.new ? (
                  <EyeOff className="w-5 h-5" />
                ) : (
                  <Eye className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>

          {/* 비밀번호 확인 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-ink-muted mb-2">
              {t('password.confirm')}
            </label>
            <div className="relative">
              <input
                type={showPasswords.confirm ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-3 pr-10 border border-line-strong rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                placeholder={t('password.confirmPlaceholder')}
              />
              <button
                type="button"
                aria-label={showPasswords.confirm ? t('password.hide') : t('password.show')}
                onClick={() =>
                  setShowPasswords({ ...showPasswords, confirm: !showPasswords.confirm })
                }
                className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-subtle hover:text-ink-muted"
              >
                {showPasswords.confirm ? (
                  <EyeOff className="w-5 h-5" />
                ) : (
                  <Eye className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>

          {/* 버튼 */}
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => navigate('/settings')}
              className="px-4 py-3 bg-surface border border-line-strong text-ink-muted rounded-xl font-medium hover:bg-surface-muted transition-colors"
            >
              {t('common.cancel')}
            </button>
            <button
              onClick={handleChangePassword}
              disabled={isLoading}
              className="px-4 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-hover disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
            >
              <Lock className="w-4 h-4" />
              {isLoading ? t('password.submitting') : t('password.submit')}
            </button>
          </div>
        </Card>
      </AppLayout>
  );
}
