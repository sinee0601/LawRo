import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { contractAPI } from '../services/api';
import { Trash2, FileText, Calendar, AlertCircle, Plus, ShieldCheck, MessageCircle, ArrowRight } from 'lucide-react';
import AppLayout from '../components/layout/AppLayout';
import { Alert, Button, Card, EmptyState, LoadingState, Sheet } from '../components/ui';
import { toast, confirm } from '../store/notifyStore';
import ContractAnalysisResult from '../components/ContractAnalysisResult';
import useTranslation from '../hooks/useTranslation';
import i18next from '../i18n/config';

export default function AnalysisHistoryPage() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuthStore();
  const { t, language } = useTranslation();
  const [analyses, setAnalyses] = useState([]);
  const userId = user?.uid || localStorage.getItem('userId');
  // 사용자 id 가 없으면 불러오지 않으므로 처음부터 로딩 상태로 두지 않습니다 (스피너가 계속 도는 문제 방지).
  const [isLoading, setIsLoading] = useState(isAuthenticated && !!userId);
  const [error, setError] = useState(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);

  // Firestore에서 분석 히스토리 조회
  useEffect(() => {
    // 비로그인 방문자는 불러올 내역이 없습니다 (아래에서 소개 화면을 보여줍니다).
    if (!isAuthenticated || !userId) return;

    const loadAnalysisHistory = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const data = await contractAPI.getAnalysisHistory(userId);
        setAnalyses(data.analyses || []);
      } catch (err) {
        setError(err.response?.data?.detail || i18next.t('contract.history.loadFailed'));
        console.error('Failed to load analysis history:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadAnalysisHistory();
  }, [isAuthenticated, userId]);

  const handleDelete = async (analysisId) => {
    const ok = await confirm({
      title: t('contract.history.deleteTitle'),
      message: t('contract.history.deleteMessage'),
      confirmText: t('common.delete'),
      tone: 'danger',
    });
    if (!ok) return;

    try {
      // API로 삭제 요청
      await contractAPI.deleteAnalysis(analysisId);

      // UI에서 제거
      setAnalyses((prev) =>
        prev.filter((analysis) => analysis.id !== analysisId)
      );
    } catch (error) {
      toast.error(t('contract.history.deleteFailed'));
      console.error('Delete failed:', error);
    }
  };

  const handleRetouchAnalysis = (analysis) => {
    // 분석 결과를 담아서 ChatPage로 이동
    const contractData = {
      structuredResult: analysis.analysis_result,
      chatbotAnalysis: analysis.chatbot_analysis?.analysis,
      sessionId: analysis.chatbot_analysis?.session_id,
      timestamp: analysis.created_at,
    };

    localStorage.setItem('contractAnalysisData', JSON.stringify(contractData));
    navigate('/chat');
  };

  if (!isAuthenticated) {
    return <GuestContractIntro onStart={() => navigate('/contract/new')} onAsk={() => navigate('/chat')} />;
  }

  return (
    <AppLayout
      title={t('contract.history.title')}
      subtitle={t('contract.history.subtitle')}
      width="wide"
      actions={
        analyses.length > 0 && (
          <Button size="sm" onClick={() => navigate('/contract/new')} className="hidden lg:inline-flex">
            <Plus className="w-4 h-4" />
            {t('contract.history.newAnalysis')}
          </Button>
        )
      }
    >
        {isLoading ? (
          <LoadingState />
        ) : error ? (
          <Alert tone="danger">{error}</Alert>
        ) : analyses.length === 0 ? (
          <Card className="max-w-xl mx-auto">
            <EmptyState
              icon={FileText}
              title={t('contract.history.emptyTitle')}
              description={t('contract.history.emptyBody')}
              action={
                <Button onClick={() => navigate('/contract/new')}>
                  {t('contract.history.emptyCta')}
                </Button>
              }
            />
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {analyses.map((analysis) => (
              <Card key={analysis.id} className="flex flex-col">
                {/* 헤더 */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-start gap-3 flex-1">
                    <FileText className="w-6 h-6 text-primary-600 dark:text-primary-400 mt-1 flex-shrink-0" />
                    <div className="flex-1">
                      <p className="text-xs text-ink-muted flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {new Date(analysis.created_at).toLocaleString(language, {
                          year: 'numeric',
                          month: '2-digit',
                          day: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDelete(analysis.id)}
                    aria-label={t('contract.history.deleteLabel')}
                    title={t('contract.history.deleteLabel')}
                    className="text-ink-subtle hover:text-danger transition-colors p-2 -m-2 rounded-control focus-visible:outline-none focus-visible:shadow-focus"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>

                {/* 계약 정보 */}
                <div className="bg-canvas rounded-xl p-4 mb-4 space-y-2 text-sm">
                  {analysis.analysis_result?.parties && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-ink-muted">{t('analysis.partyA')}</span>
                        <span className="font-medium text-ink">
                          {analysis.analysis_result.parties.party_a || t('common.notSpecified')}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-ink-muted">{t('analysis.partyB')}</span>
                        <span className="font-medium text-ink">
                          {analysis.analysis_result.parties.party_b || t('common.notSpecified')}
                        </span>
                      </div>
                    </>
                  )}
                  <div className="flex justify-between">
                    <span className="text-ink-muted">{t('analysis.period')}</span>
                    <span className="font-medium text-ink text-xs">
                      {analysis.analysis_result?.effective_date || t('common.notSpecified')} ~{' '}
                      {analysis.analysis_result?.termination_date || t('common.notSpecified')}
                    </span>
                  </div>
                </div>

                {/* 분석 요약 */}
                {analysis.analysis_result?.risks &&
                  analysis.analysis_result.risks.length > 0 && (
                    <div className="mb-4">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertCircle className="w-4 h-4 text-danger" aria-hidden="true" />
                        <span className="text-xs font-semibold text-ink">
                          {t('contract.history.risks', { count: analysis.analysis_result.risks.length })}
                        </span>
                      </div>
                      <div className="space-y-1">
                        {analysis.analysis_result.risks
                          .slice(0, 2)
                          .map((risk, idx) => (
                            <p
                              key={idx}
                              className="text-xs text-ink line-clamp-2"
                            >
                              • {risk}
                            </p>
                          ))}
                      </div>
                    </div>
                  )}

                {/* 액션 버튼 */}
                <div className="grid grid-cols-2 gap-3 mt-auto">
                  <Button variant="outline" size="sm" onClick={() => setSelectedAnalysis(analysis)}>
                    {t('contract.history.viewDetail')}
                  </Button>
                  <Button size="sm" onClick={() => handleRetouchAnalysis(analysis)}>
                    {t('contract.history.consult')}
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}

      {/* 분석 상세 보기 모달 */}
      {selectedAnalysis && (
        <Sheet
          title={t('contract.history.detailTitle')}
          onClose={() => setSelectedAnalysis(null)}
          footer={
            <>
              <Button
                size="lg"
                fullWidth
                onClick={() => {
                  handleRetouchAnalysis(selectedAnalysis);
                  setSelectedAnalysis(null);
                }}
              >
                {t('contract.history.consultWithThis')}
              </Button>
              <Button variant="outline" size="lg" fullWidth onClick={() => setSelectedAnalysis(null)}>
                {t('common.close')}
              </Button>
            </>
          }
        >
          <div className="space-y-6">
            <ContractAnalysisResult
              structured={selectedAnalysis.analysis_result}
              chatbotText={selectedAnalysis.chatbot_analysis?.analysis}
            />

            {/* 분석 일시 */}
            <div className="pt-4 border-t border-line text-xs text-ink-muted">
              {t('contract.history.analyzedAt', { date: new Date(selectedAnalysis.created_at).toLocaleString(language) })}
            </div>
          </div>
        </Sheet>
      )}

      {/* 플로팅 버튼: 새 계약서 분석 (모바일·태블릿. PC 는 제목줄 버튼) */}
      {!isLoading && analyses.length > 0 && (
        <Button
          size="lg"
          pill
          onClick={() => navigate('/contract/new')}
          className="lg:hidden fixed bottom-24 right-6 z-30 shadow-raised transition-transform hover:scale-105"
          title={t('contract.history.emptyCta')}
        >
          <FileText className="w-5 h-5" />
          <span>{t('contract.history.fab')}</span>
        </Button>
      )}

    </AppLayout>
  );
}

const GUEST_FEATURES = [
  { icon: FileText, key: 'upload' },
  { icon: ShieldCheck, key: 'risk' },
  { icon: MessageCircle, key: 'ask' },
];

/** 비로그인 방문자가 계약서 분석 탭에 들어왔을 때 보여주는 소개 화면. 분석을 시작하면 로그인으로 넘어갑니다. */
function GuestContractIntro({ onStart, onAsk }) {
  const { t } = useTranslation();
  return (
    <AppLayout title={t('contract.intro.title')} subtitle={t('contract.intro.subtitle')} width="default">
      <Card padding="none" className="p-6 sm:p-10 max-w-2xl mx-auto">
        <div className="w-14 h-14 rounded-2xl bg-primary-soft flex items-center justify-center mb-6">
          <FileText className="w-7 h-7 text-primary-600 dark:text-primary-400" aria-hidden="true" />
        </div>
        <h2 className="text-2xl font-bold text-ink tracking-tight">{t('contract.intro.heading')}</h2>
        <p className="mt-2 text-[15px] text-ink-muted leading-relaxed">
          {t('contract.intro.body')}
        </p>

        <ul className="mt-8 space-y-5">
          {GUEST_FEATURES.map((feature) => {
            const Icon = feature.icon;
            return (
              <li key={feature.key} className="flex gap-4">
                <div className="w-10 h-10 rounded-full bg-surface-muted flex items-center justify-center shrink-0">
                  <Icon className="w-5 h-5 text-ink-muted" aria-hidden="true" />
                </div>
                <div>
                  <p className="font-medium text-ink">{t(`contract.intro.${feature.key}Title`)}</p>
                  <p className="text-sm text-ink-muted mt-0.5">{t(`contract.intro.${feature.key}Body`)}</p>
                </div>
              </li>
            );
          })}
        </ul>

        <div className="mt-10 flex flex-col sm:flex-row gap-3">
          <Button size="lg" onClick={onStart} className="sm:flex-1">
            {t('contract.intro.start')}
            <ArrowRight className="w-4 h-4" />
          </Button>
          <Button size="lg" variant="outline" onClick={onAsk} className="sm:flex-1">
            {t('contract.intro.askFirst')}
          </Button>
        </div>
        <p className="mt-4 text-xs text-ink-subtle text-center sm:text-left">
          {t('contract.intro.note')}
        </p>
      </Card>
    </AppLayout>
  );
}
