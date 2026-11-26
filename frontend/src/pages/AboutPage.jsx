import { Info } from 'lucide-react';
import { Alert, Button, Card } from '../components/ui';
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
            {[
              ['about.chatTitle', 'about.chatBody'],
              ['about.contractTitle', 'about.contractBody'],
              ['about.languagesTitle', 'about.languagesBody'],
            ].map(([title, body]) => (
              <div key={title} className="p-4 bg-surface-muted rounded-control">
                <p className="font-semibold text-ink text-sm mb-1">{t(title)}</p>
                <p className="text-xs text-ink-muted leading-relaxed">{t(body)}</p>
              </div>
            ))}
          </div>
        </Card>

        {/* 업데이트 예정 기능 */}
        <Alert tone="warning" title={t('about.upcomingTitle')} className="mb-6">
          <ul className="space-y-1">
            <li>• {t('about.upcoming1')}</li>
            <li>• {t('about.upcoming2')}</li>
            <li>• {t('about.upcoming3')}</li>
          </ul>
        </Alert>

        {/* 문의 섹션 */}
        <Card>
          <h2 className="text-lg font-bold text-ink mb-4">{t('about.contactTitle')}</h2>
          <p className="text-sm text-ink-muted mb-4">
            {t('about.contactBody')}
          </p>
          <Button size="lg" fullWidth onClick={handleComingSoon}>
            {t('about.contact')}
          </Button>
        </Card>
      </AppLayout>
  );
}
