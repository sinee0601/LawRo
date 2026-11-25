import { Info, AlertCircle } from 'lucide-react';
import { Card } from '../components/ui';
import AppLayout from '../components/layout/AppLayout';
import { toast } from '../store/notifyStore';
import useTranslation from '../hooks/useTranslation';


export default function AboutPage() {
  const { t } = useTranslation();
  const handleComingSoon = () => {
    toast.info(t('common.comingSoon'));
  };

  return (
    <AppLayout title={t('about.title')} showBack width="narrow">
        {/* 로고 및 기본 정보 */}
        <Card padding="lg" className="mb-6 text-center">
          <div className="w-24 h-24 bg-primary-100 dark:bg-primary-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-4xl font-bold text-primary-600 dark:text-primary-400">LR</span>
          </div>
          <h1 className="text-2xl font-bold text-ink mb-2">LawRo</h1>
          <p className="text-sm text-ink-muted mb-4">
            {t('about.tagline')}
          </p>
          <p className="text-xs text-ink-muted">{t('common.version', { version: '1.0.0' })}</p>
        </Card>

        {/* 소개 섹션 */}
        <Card className="mb-6">
          <h2 className="text-lg font-bold text-ink mb-4 flex items-center gap-2">
            <Info className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            {t('about.introTitle')}
          </h2>
          <p className="text-sm text-ink-muted leading-relaxed mb-4">
            {t('about.introBody')}
          </p>
          <ul className="space-y-2 text-sm text-ink-muted">
            <li className="flex items-start gap-2">
              <span className="text-primary-600 dark:text-primary-400 font-bold mt-0.5">•</span>
              <span>{t('about.point1')}</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary-600 dark:text-primary-400 font-bold mt-0.5">•</span>
              <span>{t('about.point2')}</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary-600 dark:text-primary-400 font-bold mt-0.5">•</span>
              <span>{t('about.point3')}</span>
            </li>
          </ul>
        </Card>

        {/* 주요 기능 */}
        <Card className="mb-6">
          <h2 className="text-lg font-bold text-ink mb-4">{t('about.featuresTitle')}</h2>
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="p-3 bg-blue-50 dark:bg-blue-500/10 rounded-lg">
              <p className="font-medium text-blue-900 dark:text-blue-200 text-sm mb-1">{t('about.chatTitle')}</p>
              <p className="text-xs text-blue-800 dark:text-blue-200">
                {t('about.chatBody')}
              </p>
            </div>
            <div className="p-3 bg-green-50 dark:bg-green-500/10 rounded-lg">
              <p className="font-medium text-green-900 dark:text-green-200 text-sm mb-1">{t('about.contractTitle')}</p>
              <p className="text-xs text-green-800 dark:text-green-200">
                {t('about.contractBody')}
              </p>
            </div>
            <div className="p-3 bg-purple-50 dark:bg-purple-500/10 rounded-lg">
              <p className="font-medium text-purple-900 dark:text-purple-200 text-sm mb-1">{t('about.languagesTitle')}</p>
              <p className="text-xs text-purple-800 dark:text-purple-200">
                {t('about.languagesBody')}
              </p>
            </div>
          </div>
        </Card>

        {/* 업데이트 예정 기능 */}
        <div className="bg-yellow-50 dark:bg-yellow-500/10 border border-yellow-200 dark:border-yellow-500/30 rounded-2xl p-4 mb-6 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-yellow-900 dark:text-yellow-200 mb-1">{t('about.upcomingTitle')}</p>
            <ul className="text-xs text-yellow-800 dark:text-yellow-200 space-y-1">
              <li>• {t('about.upcoming1')}</li>
              <li>• {t('about.upcoming2')}</li>
              <li>• {t('about.upcoming3')}</li>
            </ul>
          </div>
        </div>

        {/* 문의 섹션 */}
        <Card>
          <h2 className="text-lg font-bold text-ink mb-4">{t('about.contactTitle')}</h2>
          <p className="text-sm text-ink-muted mb-4">
            {t('about.contactBody')}
          </p>
          <button
            onClick={handleComingSoon}
            className="w-full bg-primary-600 hover:bg-primary-hover text-white font-medium py-3 rounded-xl transition-colors"
          >
            {t('about.contact')}
          </button>
        </Card>
      </AppLayout>
  );
}
