import { useNavigate } from 'react-router-dom';
import { Shield } from 'lucide-react';
import { Alert, Button, Card } from '../components/ui';
import AppLayout from '../components/layout/AppLayout';
import useTranslation from '../hooks/useTranslation';

// 최종 수정일. 표시 형식은 선택한 언어를 따릅니다.
const LAST_UPDATED = new Date(2024, 10, 10);

// 각 조항: 제목, 안내문(intro) 또는 본문(body), 항목 목록(items) 키
const SECTIONS = [
  { n: 1, intro: true, items: true },
  { n: 2, intro: true, items: true },
  { n: 3, body: true },
  { n: 4, body: true },
  { n: 5, body: true },
  { n: 6, intro: true, items: true },
  { n: 7, body: true },
];

export default function PrivacyPage() {
  const navigate = useNavigate();
  const { t, language } = useTranslation();

  return (
    <AppLayout title={t('privacy.title')} showBack width="narrow">
        {/* 헤더 */}
        <Card className="mb-6">
          <div className="flex items-center gap-3 mb-4">
            <Shield className="w-6 h-6 text-primary-600 dark:text-primary-400" />
            <h1 className="text-lg font-bold text-ink">{t('privacy.title')}</h1>
          </div>
          <p className="text-sm text-ink-muted">
            {t('privacy.lastUpdated', {
              date: LAST_UPDATED.toLocaleDateString(language, { year: 'numeric', month: 'long', day: 'numeric' }),
            })}
          </p>
        </Card>

        {/* 내용 */}
        <Card className="mb-6">
          <div className="space-y-6 text-sm text-ink-muted">
            {SECTIONS.map(({ n, intro, body, items }) => (
              <section key={n}>
                <h2 className="font-bold text-ink mb-2">{t(`privacy.s${n}Title`)}</h2>
                {intro && <p className="text-xs text-ink-muted mb-2">{t(`privacy.s${n}Intro`)}</p>}
                {body && <p className="text-xs text-ink-muted">{t(`privacy.s${n}Body`)}</p>}
                {items && (
                  <ul className="space-y-1 text-xs text-ink-muted">
                    {t(`privacy.s${n}Items`, { returnObjects: true }).map((item) => (
                      <li key={item}>• {item}</li>
                    ))}
                  </ul>
                )}
              </section>
            ))}
          </div>
        </Card>

        {/* 정보 안내 */}
        <Alert tone="info" className="mb-6">{t('privacy.notice')}</Alert>

        {/* 동의 버튼 */}
        <Button size="lg" fullWidth onClick={() => navigate('/settings')}>
          {t('privacy.done')}
        </Button>
      </AppLayout>
  );
}
