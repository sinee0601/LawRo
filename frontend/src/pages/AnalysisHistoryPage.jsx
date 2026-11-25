import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { contractAPI } from '../services/api';
import { Trash2, FileText, Calendar, AlertCircle, Plus, ShieldCheck, MessageCircle, ArrowRight } from 'lucide-react';
import AppLayout from '../components/layout/AppLayout';
import { Button, Card, Sheet } from '../components/ui';
import { toast, confirm } from '../store/notifyStore';
import ContractAnalysisResult from '../components/ContractAnalysisResult';

export default function AnalysisHistoryPage() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuthStore();
  const [analyses, setAnalyses] = useState([]);
  const [isLoading, setIsLoading] = useState(isAuthenticated);
  const [error, setError] = useState(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);

  const userId = user?.uid || localStorage.getItem('userId');

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
        setError(err.message || '분석 히스토리를 불러오는 중 오류가 발생했습니다.');
        console.error('Failed to load analysis history:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadAnalysisHistory();
  }, [isAuthenticated, userId]);

  const handleDelete = async (analysisId) => {
    const ok = await confirm({
      title: '이 분석 결과를 삭제할까요?',
      message: '삭제한 결과는 되돌릴 수 없어요.',
      confirmText: '삭제',
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
      toast.error('삭제에 실패했어요. 잠시 후 다시 시도해 주세요.');
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
      title="분석 내역"
      subtitle="지금까지 분석한 근로계약서"
      width="wide"
      actions={
        analyses.length > 0 && (
          <Button size="sm" onClick={() => navigate('/contract/new')} className="hidden lg:inline-flex">
            <Plus className="w-4 h-4" />
            새 계약서 분석
          </Button>
        )
      }
    >
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin">
              <div className="w-8 h-8 border-4 border-primary-200 dark:border-primary-500/30 border-t-primary-600 rounded-full" />
            </div>
          </div>
        ) : error ? (
          <div className="p-4 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 text-red-700 dark:text-red-300 rounded-xl">
            <AlertCircle className="w-5 h-5 mb-2" />
            {error}
          </div>
        ) : analyses.length === 0 ? (
          <Card padding="none" className="p-12 text-center max-w-xl mx-auto">
            <FileText className="w-16 h-16 text-line-strong mx-auto mb-4" />
            <p className="text-ink font-medium mb-2">분석 내역이 없습니다</p>
            <p className="text-sm text-ink-muted">
              계약서를 분석하면 내역이 저장됩니다.
            </p>
            <Button onClick={() => navigate('/contract/new')} className="mt-6">
              새 계약서 분석하기
            </Button>
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
                        {new Date(analysis.created_at).toLocaleDateString('ko-KR', {
                          year: 'numeric',
                          month: '2-digit',
                          day: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit'
                        }).replace(/\. /g, '.').replace(/\. /, ' ')}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDelete(analysis.id)}
                    className="text-ink-subtle hover:text-red-600 dark:hover:text-red-400 transition-colors"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>

                {/* 계약 정보 */}
                <div className="bg-canvas rounded-xl p-4 mb-4 space-y-2 text-sm">
                  {analysis.analysis_result?.parties && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-ink-muted">갑(사용자):</span>
                        <span className="font-medium text-ink">
                          {analysis.analysis_result.parties.party_a || '미명시'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-ink-muted">을(근로자):</span>
                        <span className="font-medium text-ink">
                          {analysis.analysis_result.parties.party_b || '미명시'}
                        </span>
                      </div>
                    </>
                  )}
                  <div className="flex justify-between">
                    <span className="text-ink-muted">계약 기간:</span>
                    <span className="font-medium text-ink text-xs">
                      {analysis.analysis_result?.effective_date || '미명시'} ~{' '}
                      {analysis.analysis_result?.termination_date || '미명시'}
                    </span>
                  </div>
                </div>

                {/* 분석 요약 */}
                {analysis.analysis_result?.risks &&
                  analysis.analysis_result.risks.length > 0 && (
                    <div className="mb-4">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400" />
                        <span className="text-xs font-semibold text-ink">
                          주의 사항 {analysis.analysis_result.risks.length}개
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
                    상세 보기
                  </Button>
                  <Button size="sm" onClick={() => handleRetouchAnalysis(analysis)}>
                    상담하기
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}

      {/* 분석 상세 보기 모달 */}
      {selectedAnalysis && (
        <Sheet
          title="분석 상세 보기"
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
                이 분석으로 상담하기
              </Button>
              <Button variant="outline" size="lg" fullWidth onClick={() => setSelectedAnalysis(null)}>
                닫기
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
              분석 일시: {new Date(selectedAnalysis.created_at).toLocaleString('ko-KR')}
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
          title="새 계약서 분석하기"
        >
          <FileText className="w-5 h-5" />
          <span>계약서 분석</span>
        </Button>
      )}

    </AppLayout>
  );
}

const GUEST_FEATURES = [
  { icon: FileText, title: '사진이나 PDF로 올리기', body: '종이 계약서는 사진으로 찍어 올리면 돼요.' },
  { icon: ShieldCheck, title: '위험한 조항 찾기', body: '근로기준법과 다르거나 빠진 내용을 쉬운 말로 알려드려요.' },
  { icon: MessageCircle, title: '챗봇에게 이어서 묻기', body: '분석 결과를 바탕으로 궁금한 점을 바로 물어볼 수 있어요.' },
];

/** 비로그인 방문자가 계약서 분석 탭에 들어왔을 때 보여주는 소개 화면. 분석을 시작하면 로그인으로 넘어갑니다. */
function GuestContractIntro({ onStart, onAsk }) {
  return (
    <AppLayout title="계약서 분석" subtitle="서명하기 전에 근로계약서를 확인해 보세요" width="default">
      <Card padding="none" className="p-6 sm:p-10 max-w-2xl mx-auto">
        <div className="w-14 h-14 rounded-2xl bg-primary-soft flex items-center justify-center mb-6">
          <FileText className="w-7 h-7 text-primary-600 dark:text-primary-400" aria-hidden="true" />
        </div>
        <h2 className="text-2xl font-bold text-ink tracking-tight">근로계약서, 서명 전에 확인하세요</h2>
        <p className="mt-2 text-[15px] text-ink-muted leading-relaxed">
          계약서를 올리면 AI가 내용을 읽고 문제가 될 수 있는 부분을 짚어 드려요.
        </p>

        <ul className="mt-8 space-y-5">
          {GUEST_FEATURES.map((feature) => {
            const Icon = feature.icon;
            return (
              <li key={feature.title} className="flex gap-4">
                <div className="w-10 h-10 rounded-full bg-surface-muted flex items-center justify-center shrink-0">
                  <Icon className="w-5 h-5 text-ink-muted" aria-hidden="true" />
                </div>
                <div>
                  <p className="font-medium text-ink">{feature.title}</p>
                  <p className="text-sm text-ink-muted mt-0.5">{feature.body}</p>
                </div>
              </li>
            );
          })}
        </ul>

        <div className="mt-10 flex flex-col sm:flex-row gap-3">
          <Button size="lg" onClick={onStart} className="sm:flex-1">
            계약서 분석 시작하기
            <ArrowRight className="w-4 h-4" />
          </Button>
          <Button size="lg" variant="outline" onClick={onAsk} className="sm:flex-1">
            챗봇에게 먼저 물어보기
          </Button>
        </div>
        <p className="mt-4 text-xs text-ink-subtle text-center sm:text-left">
          분석 결과는 계정에 저장돼요. 분석을 시작하면 로그인 화면으로 이동해요.
        </p>
      </Card>
    </AppLayout>
  );
}
