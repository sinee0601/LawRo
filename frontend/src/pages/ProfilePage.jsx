import { useState } from 'react';
import useAuthStore from '../store/authStore';
import { settingsAPI } from '../services/api';
import { User, Mail } from 'lucide-react';
import { Card } from '../components/ui';
import AppLayout from '../components/layout/AppLayout';
import { toast } from '../store/notifyStore';
import useTranslation from '../hooks/useTranslation';


export default function ProfilePage() {
  const { user } = useAuthStore();
  const { t, language } = useTranslation();
  const [editName, setEditName] = useState(false);
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSave = async () => {
    setIsSaving(true);
    setError('');
    try {
      await settingsAPI.updateProfile(fullName);
      toast.success(t('profile.saved'));
      setEditName(false);
    } catch (err) {
      setError(err.response?.data?.detail || t('profile.saveFailed'));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <AppLayout title={t('profile.title')} showBack width="narrow">
        {/* 프로필 카드 */}
        <Card className="mb-6">
          {/* 프로필 아이콘 */}
          <div className="flex justify-center mb-6">
            <div className="w-20 h-20 bg-primary-100 dark:bg-primary-500/20 rounded-full flex items-center justify-center">
              <User className="w-10 h-10 text-primary-600 dark:text-primary-400" />
            </div>
          </div>

          {/* 이메일 (읽기 전용) */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-ink-muted mb-2">{t('profile.email')}</label>
            <div className="flex items-center gap-3 p-3 bg-canvas rounded-xl border border-line">
              <Mail className="w-5 h-5 text-ink-subtle" />
              <p className="text-ink">{user?.email}</p>
            </div>
          </div>

          {/* 이름 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-ink-muted mb-2">{t('profile.name')}</label>
            {!editName ? (
              <div
                onClick={() => setEditName(true)}
                className="flex items-center justify-between p-3 bg-canvas rounded-xl border border-line cursor-pointer hover:bg-surface-muted transition-colors"
              >
                <p className="text-ink">{fullName || t('profile.noName')}</p>
                <span className="text-sm text-primary-600 dark:text-primary-400 font-medium">{t('common.edit')}</span>
              </div>
            ) : (
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-4 py-3 border border-primary-300 dark:border-primary-500/40 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                placeholder={t('profile.namePlaceholder')}
              />
            )}
          </div>

          {editName && error && (
            <p role="alert" className="text-sm text-red-600 mb-3">
              {error}
            </p>
          )}

          {/* 수정 버튼 */}
          {editName && (
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => {
                  setEditName(false);
                  setFullName(user?.full_name || '');
                  setError('');
                }}
                className="px-4 py-3 bg-surface border border-line-strong text-ink-muted rounded-xl font-medium hover:bg-surface-muted transition-colors"
              >
                {t('common.cancel')}
              </button>
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="px-4 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-hover disabled:opacity-50 transition-colors"
              >
                {isSaving ? t('common.saving') : t('common.save')}
              </button>
            </div>
          )}
        </Card>

        {/* 계정 정보 */}
        <Card>
          <h3 className="font-bold text-ink mb-4">{t('profile.accountInfo')}</h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-ink-muted">{t('profile.signupType')}</span>
              <span className="text-ink font-medium">
                {user?.provider === 'google' ? 'Google' :
                 user?.provider === 'kakao' ? 'Kakao' :
                 user?.provider === 'naver' ? 'Naver' :
                 t('profile.emailProvider')}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-ink-muted">{t('profile.joinedAt')}</span>
              <span className="text-ink font-medium">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString(language) : '-'}
              </span>
            </div>
          </div>
        </Card>
      </AppLayout>
  );
}
