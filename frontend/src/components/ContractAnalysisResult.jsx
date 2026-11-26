import { useState } from 'react';
import {
  AlertCircle,
  AlertTriangle,
  CheckCircle,
  ChevronDown,
  FileText,
  Gauge,
  Scale,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { cn } from './ui';
import useTranslation from '../hooks/useTranslation';

// 챗봇 분석(analysis)은 JSON 문자열로 오지만, 앞뒤에 설명문이나 ```json 코드블록이 붙을 수 있다.
// 가장 바깥 { ... } 만 잘라 파싱하고, 실패하면 null 을 돌려 평문으로 보여준다.
function parseChatbotAnalysis(text) {
  if (typeof text !== 'string') return null;
  const match = text.match(/\{[\s\S]*\}/);
  if (!match) return null;
  try {
    const parsed = JSON.parse(match[0]);
    return parsed && typeof parsed === 'object' ? parsed : null;
  } catch {
    return null;
  }
}

// 분석 프롬프트(backend/prompts/analysis_request_template.txt) 기준:
// totalScore 는 높을수록 위험. 0~1 안전, 1~8 주의, 9 이상 위험.
const LEVELS = {
  safe: {
    labelKey: 'analysis.levels.safe',
    className: 'bg-success-soft text-success border-success/30',
    Icon: ShieldCheck,
  },
  caution: {
    labelKey: 'analysis.levels.caution',
    className: 'bg-warning-soft text-warning border-warning/30',
    Icon: AlertTriangle,
  },
  danger: {
    labelKey: 'analysis.levels.danger',
    className: 'bg-danger-soft text-danger border-danger/30',
    Icon: AlertCircle,
  },
};

function levelFromScore(score) {
  if (score < 1) return 'safe';
  if (score < 9) return 'caution';
  return 'danger';
}

const asList = (value) => (Array.isArray(value) ? value.filter(Boolean) : []);
const isShortLabel = (value) => typeof value === 'string' && value.trim().length > 0 && value.trim().length <= 12;

function Section({ icon: Icon, title, tone = 'default', children }) {
  const tones = {
    default: 'bg-canvas border-line',
    primary: 'bg-primary-soft border-primary-200 dark:border-primary-500/30',
    success: 'bg-success-soft border-success/25',
    warning: 'bg-warning-soft border-warning/25',
    danger: 'bg-danger-soft border-danger/25',
  };
  const iconTones = {
    default: 'text-ink-muted',
    primary: 'text-primary-600 dark:text-primary-400',
    success: 'text-success',
    warning: 'text-warning',
    danger: 'text-danger',
  };
  return (
    <section className={cn('rounded-2xl border p-4', tones[tone])}>
      <h3 className="flex items-center gap-2 text-sm font-semibold text-ink mb-3">
        {Icon && <Icon className={cn('w-4 h-4 flex-shrink-0', iconTones[tone])} />}
        {title}
      </h3>
      {children}
    </section>
  );
}

function BulletList({ items, icon: Icon, iconClassName }) {
  return (
    <ul className="space-y-2">
      {items.map((item, idx) => (
        <li key={idx} className="flex gap-2 text-sm text-ink leading-relaxed">
          {Icon ? (
            <Icon className={cn('w-4 h-4 flex-shrink-0 mt-0.5', iconClassName)} />
          ) : (
            <span className={cn('flex-shrink-0 font-bold', iconClassName)}>•</span>
          )}
          <span>{typeof item === 'string' ? item : JSON.stringify(item)}</span>
        </li>
      ))}
    </ul>
  );
}

function InfoRow({ label, value }) {
  return (
    <div className="flex justify-between gap-4">
      <dt className="text-ink-muted flex-shrink-0">{label}</dt>
      <dd className="font-medium text-ink text-right break-words min-w-0">{value}</dd>
    </div>
  );
}

function ScoreCard({ score, awareLabel }) {
  const { t } = useTranslation();
  const level = LEVELS[levelFromScore(score)];
  const { Icon } = level;
  return (
    <div className={cn('rounded-2xl border p-4', level.className)}>
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Gauge className="w-5 h-5" />
          <span className="text-sm font-semibold text-ink">{t('analysis.score')}</span>
        </div>
        <span className="inline-flex items-center gap-1 rounded-full bg-surface/70 px-2.5 py-1 text-xs font-semibold">
          <Icon className="w-3.5 h-3.5" />
          {awareLabel || t(level.labelKey)}
        </span>
      </div>
      <div className="mt-3 flex items-baseline gap-1">
        <span className="text-3xl font-bold">{Number.isInteger(score) ? score : score.toFixed(1)}</span>
        <span className="text-xs text-ink-muted">{t('analysis.points')}</span>
      </div>
      <p className="mt-1 text-xs text-ink-muted">{t('analysis.scoreGuide')}</p>
    </div>
  );
}

function ChatbotAnalysis({ text }) {
  const { t } = useTranslation();
  const parsed = parseChatbotAnalysis(text);

  if (!parsed) {
    return (
      <Section icon={Scale} title={t('analysis.expert')} tone="primary">
        <p className="text-sm text-ink whitespace-pre-wrap leading-relaxed">{text}</p>
      </Section>
    );
  }

  const score = Number(parsed.totalScore);
  const hasScore = parsed.totalScore !== undefined && parsed.totalScore !== null && parsed.totalScore !== '' && Number.isFinite(score);

  // aware 는 프롬프트상 "위험/주의/안전" 등급이지만, 문장 목록으로 오는 경우도 있다.
  const awareItems = asList(parsed.aware);
  const awareLabel = isShortLabel(parsed.aware)
    ? parsed.aware.trim()
    : awareItems.length === 1 && isShortLabel(awareItems[0])
      ? awareItems[0].trim()
      : null;
  const awareNotes = awareLabel ? [] : awareItems;

  const highlights = asList(parsed.highlights);
  const interpretations = asList(parsed.legalInterpretation);

  return (
    <div className="space-y-3">
      {hasScore && <ScoreCard score={score} awareLabel={awareLabel} />}

      {parsed.summary && (
        <Section icon={FileText} title={t('analysis.summary')} tone="primary">
          <p className="text-sm text-ink leading-relaxed">{parsed.summary}</p>
        </Section>
      )}

      {awareNotes.length > 0 && (
        <Section icon={AlertTriangle} title={t('analysis.cautions')} tone="warning">
          <BulletList items={awareNotes} iconClassName="text-warning" />
        </Section>
      )}

      {highlights.length > 0 && (
        <Section icon={Sparkles} title={t('analysis.highlights')}>
          <BulletList items={highlights} icon={CheckCircle} iconClassName="text-primary-600 dark:text-primary-400" />
        </Section>
      )}

      {interpretations.length > 0 && (
        <Section icon={Scale} title={t('analysis.interpretation')}>
          <div className="space-y-3">
            {interpretations.map((item, idx) => (
              <div key={idx} className="border-l-2 border-primary-400 pl-3">
                {item.issue && <p className="text-xs font-semibold text-ink mb-1">{item.issue}</p>}
                <p className="text-sm text-ink leading-relaxed">
                  {typeof item === 'string' ? item : item.interpretation}
                </p>
              </div>
            ))}
          </div>
        </Section>
      )}

      {parsed.deepAnalysis && (
        <Section icon={FileText} title={t('analysis.deepAnalysis')}>
          <p className="text-sm text-ink whitespace-pre-wrap leading-relaxed">{parsed.deepAnalysis}</p>
        </Section>
      )}
    </div>
  );
}

/**
 * 계약서 분석 결과.
 * structured: OCR + 파싱 결과 (contract_type, parties, effective_date, key_terms, risks, extracted_text ...)
 * chatbotText: 챗봇 법률 분석 원문 (보통 totalScore, summary 등을 담은 JSON 문자열)
 */
export default function ContractAnalysisResult({ structured, chatbotText }) {
  const { t } = useTranslation();
  const [showText, setShowText] = useState(false);
  const keyTerms = asList(structured?.key_terms);
  const risks = asList(structured?.risks);
  const hasAnything = structured || chatbotText;

  if (!hasAnything) {
    return (
      <div className="rounded-2xl border border-line bg-canvas p-6 text-center text-sm text-ink-muted">
        {t('analysis.loadFailed')}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {chatbotText && <ChatbotAnalysis text={chatbotText} />}

      {structured && (
        <Section icon={FileText} title={t('analysis.contractInfo')}>
          <dl className="space-y-2 text-sm">
            <InfoRow label={t('analysis.contractType')} value={structured.contract_type || t('common.unknown')} />
            <InfoRow
              label={t('analysis.period')}
              value={`${structured.effective_date || t('common.notSpecified')} ~ ${structured.termination_date || t('common.notSpecified')}`}
            />
            {structured.parties && (
              <>
                <InfoRow label={t('analysis.partyA')} value={structured.parties.party_a || t('common.notSpecified')} />
                <InfoRow label={t('analysis.partyB')} value={structured.parties.party_b || t('common.notSpecified')} />
              </>
            )}
            {structured.payment_terms && <InfoRow label={t('analysis.payment')} value={structured.payment_terms} />}
          </dl>
        </Section>
      )}

      {risks.length > 0 && (
        <Section icon={AlertCircle} title={t('analysis.risks', { count: risks.length })} tone="danger">
          <BulletList items={risks} icon={AlertCircle} iconClassName="text-danger" />
        </Section>
      )}

      {keyTerms.length > 0 && (
        <Section icon={CheckCircle} title={t('analysis.keyTerms')}>
          <BulletList items={keyTerms} icon={CheckCircle} iconClassName="text-primary-600 dark:text-primary-400" />
        </Section>
      )}

      {structured?.extracted_text && (
        <div className="rounded-2xl border border-line">
          <button
            type="button"
            onClick={() => setShowText((v) => !v)}
            aria-expanded={showText}
            className="flex w-full items-center justify-between px-4 py-3 text-sm font-medium text-ink-muted hover:text-ink"
          >
            {showText ? t('analysis.ocrHide') : t('analysis.ocrShow')}
            <ChevronDown className={cn('w-4 h-4 transition-transform', showText && 'rotate-180')} />
          </button>
          {showText && (
            <div className="border-t border-line px-4 py-3 max-h-60 overflow-y-auto">
              <p className="text-xs text-ink-muted mb-2">{t('analysis.ocrNote')}</p>
              <pre className="text-xs text-ink whitespace-pre-wrap font-mono leading-relaxed">
                {structured.extracted_text}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
