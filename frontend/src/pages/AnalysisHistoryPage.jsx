import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { contractAPI } from '../services/api';
import { Trash2, FileText, Calendar, AlertCircle, CheckCircle, X, Plus } from 'lucide-react';
import MobileHeader from '../components/MobileHeader';
import BottomNav from '../components/BottomNav';
import { Button, Card } from '../components/ui';
import { toast, confirm } from '../store/notifyStore';
import ContractAnalysisResult from '../components/ContractAnalysisResult';

export default function AnalysisHistoryPage() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [analyses, setAnalyses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);

  const userId = user?.uid || localStorage.getItem('userId') || 'default_user';

  // Firestore에서 분석 히스토리 조회
  useEffect(() => {
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
  }, [userId]);

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

  return (
    <div className="min-h-screen bg-canvas pb-20">
      <MobileHeader title="분석 내역" showBack={false} />

      <main className="max-w-md mx-auto px-4 pt-20 pb-8">
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
          <Card padding="none" className="p-12 text-center">
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
          <div className="space-y-4">
            {analyses.map((analysis) => (
              <Card key={analysis.id}>
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
                <div className="grid grid-cols-2 gap-3">
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
      </main>

      {/* 분석 상세 보기 모달 */}
      {selectedAnalysis && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-end">
          <div className="bg-surface w-full rounded-t-sheet max-h-[90vh] overflow-y-auto">
            {/* 모달 헤더 */}
            <div className="sticky top-0 bg-surface border-b border-line p-4 flex items-center justify-between">
              <h2 className="text-lg font-bold text-ink">분석 상세 보기</h2>
              <button
                onClick={() => setSelectedAnalysis(null)}
                className="text-ink-subtle hover:text-ink-muted"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* 모달 콘텐츠 */}
            <div className="p-6 space-y-6">
              <ContractAnalysisResult
                structured={selectedAnalysis.analysis_result}
                chatbotText={selectedAnalysis.chatbot_analysis?.analysis}
              />

              {/* 분석 일시 */}
              <div className="pt-4 border-t border-line text-xs text-ink-muted">
                분석 일시:{' '}
                {new Date(selectedAnalysis.created_at).toLocaleString('ko-KR')}
              </div>
            </div>

            {/* 모달 하단 버튼 */}
            <div className="sticky bottom-0 bg-surface border-t border-line p-4 space-y-3">
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
            </div>
          </div>
        </div>
      )}

      {/* 플로팅 버튼: 새 계약서 분석 */}
      {!isLoading && analyses.length > 0 && (
        <Button
          size="lg"
          pill
          onClick={() => navigate('/contract/new')}
          className="fixed bottom-24 right-6 z-40 shadow-raised transition-transform hover:scale-105"
          title="새 계약서 분석하기"
        >
          <FileText className="w-5 h-5" />
          <span>계약서 분석</span>
        </Button>
      )}

      <BottomNav />
    </div>
  );
}
