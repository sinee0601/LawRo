import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { contractAPI } from '../services/api';
import { Trash2, FileText, Calendar, AlertCircle, CheckCircle, X, Plus } from 'lucide-react';
import MobileHeader from '../components/MobileHeader';
import BottomNav from '../components/BottomNav';

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
    if (!window.confirm('이 분석 결과를 삭제하시겠습니까?')) return;

    try {
      // API로 삭제 요청
      await contractAPI.deleteAnalysis(analysisId);

      // UI에서 제거
      setAnalyses((prev) =>
        prev.filter((analysis) => analysis.id !== analysisId)
      );
    } catch (error) {
      alert('삭제에 실패했습니다.');
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
    <div className="min-h-screen bg-gray-50 pb-20">
      <MobileHeader title="분석 내역" showBack={false} />

      <main className="max-w-md mx-auto px-4 pt-20 pb-8">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin">
              <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full" />
            </div>
          </div>
        ) : error ? (
          <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl">
            <AlertCircle className="w-5 h-5 mb-2" />
            {error}
          </div>
        ) : analyses.length === 0 ? (
          <div className="bg-white rounded-3xl shadow-lg p-12 text-center">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-900 font-medium mb-2">분석 내역이 없습니다</p>
            <p className="text-sm text-gray-600">
              계약서를 분석하면 내역이 저장됩니다.
            </p>
            <button
              onClick={() => navigate('/contract/new')}
              className="mt-6 bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-6 rounded-xl transition-colors"
            >
              새 계약서 분석하기
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {analyses.map((analysis) => (
              <div
                key={analysis.id}
                className="bg-white rounded-3xl shadow-lg p-6"
              >
                {/* 헤더 */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-start gap-3 flex-1">
                    <FileText className="w-6 h-6 text-primary-600 mt-1 flex-shrink-0" />
                    <div className="flex-1">
                      <p className="text-xs text-gray-500 flex items-center gap-1">
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
                    className="text-gray-400 hover:text-red-600 transition-colors"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>

                {/* 계약 정보 */}
                <div className="bg-gray-50 rounded-xl p-4 mb-4 space-y-2 text-sm">
                  {analysis.analysis_result?.parties && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-gray-600">갑(사용자):</span>
                        <span className="font-medium text-gray-900">
                          {analysis.analysis_result.parties.party_a || '미명시'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">을(근로자):</span>
                        <span className="font-medium text-gray-900">
                          {analysis.analysis_result.parties.party_b || '미명시'}
                        </span>
                      </div>
                    </>
                  )}
                  <div className="flex justify-between">
                    <span className="text-gray-600">계약 기간:</span>
                    <span className="font-medium text-gray-900 text-xs">
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
                        <AlertCircle className="w-4 h-4 text-red-600" />
                        <span className="text-xs font-semibold text-gray-900">
                          주의 사항 {analysis.analysis_result.risks.length}개
                        </span>
                      </div>
                      <div className="space-y-1">
                        {analysis.analysis_result.risks
                          .slice(0, 2)
                          .map((risk, idx) => (
                            <p
                              key={idx}
                              className="text-xs text-gray-700 line-clamp-2"
                            >
                              • {risk}
                            </p>
                          ))}
                      </div>
                    </div>
                  )}

                {/* 액션 버튼 */}
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => setSelectedAnalysis(analysis)}
                    className="bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 font-medium py-2 rounded-xl transition-colors text-sm"
                  >
                    상세 보기
                  </button>
                  <button
                    onClick={() => handleRetouchAnalysis(analysis)}
                    className="bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 rounded-xl transition-colors text-sm"
                  >
                    상담하기
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* 분석 상세 보기 모달 */}
      {selectedAnalysis && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end">
          <div className="bg-white w-full rounded-t-3xl max-h-[90vh] overflow-y-auto">
            {/* 모달 헤더 */}
            <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
              <h2 className="text-lg font-bold text-gray-900">분석 상세 보기</h2>
              <button
                onClick={() => setSelectedAnalysis(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* 모달 콘텐츠 */}
            <div className="p-6 space-y-6">
              {/* 계약서 기본 정보 */}
              {selectedAnalysis.analysis_result && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">📋 계약서 정보</h3>
                  <div className="space-y-2 text-sm bg-gray-50 p-4 rounded-xl">
                    <div className="flex justify-between">
                      <span className="text-gray-600">계약 유형:</span>
                      <span className="font-medium text-gray-900">
                        {selectedAnalysis.analysis_result.contract_type || '미확인'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">계약 기간:</span>
                      <span className="font-medium text-gray-900 text-xs">
                        {selectedAnalysis.analysis_result.effective_date || '미명시'} ~{' '}
                        {selectedAnalysis.analysis_result.termination_date || '미명시'}
                      </span>
                    </div>
                    {selectedAnalysis.analysis_result.parties && (
                      <>
                        <div className="flex justify-between">
                          <span className="text-gray-600">갑(사용자):</span>
                          <span className="font-medium text-gray-900">
                            {selectedAnalysis.analysis_result.parties.party_a || '미명시'}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">을(근로자):</span>
                          <span className="font-medium text-gray-900">
                            {selectedAnalysis.analysis_result.parties.party_b || '미명시'}
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              )}

              {/* 주요 조건 */}
              {selectedAnalysis.analysis_result?.key_terms &&
                selectedAnalysis.analysis_result.key_terms.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3">✅ 주요 계약 조건</h3>
                    <div className="space-y-2">
                      {selectedAnalysis.analysis_result.key_terms.map((term, idx) => (
                        <div
                          key={idx}
                          className="flex items-start gap-2 p-3 bg-blue-50 rounded-lg"
                        >
                          <CheckCircle className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
                          <p className="text-sm text-gray-900">{term}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              {/* 법률적 위험 요소 */}
              {selectedAnalysis.analysis_result?.risks &&
                selectedAnalysis.analysis_result.risks.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3">⚠️ 법률적 위험 요소</h3>
                    <div className="space-y-2">
                      {selectedAnalysis.analysis_result.risks.map((risk, idx) => (
                        <div
                          key={idx}
                          className="flex items-start gap-2 p-3 bg-red-50 border-l-4 border-red-500 rounded-lg"
                        >
                          <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
                          <p className="text-sm text-gray-900">{risk}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              {/* 챗봇 상세 분석 */}
              {selectedAnalysis.chatbot_analysis?.analysis && (
                <div>
                  {(() => {
                    const analysisText = selectedAnalysis.chatbot_analysis.analysis;
                    try {
                      // Try to parse as JSON
                      const jsonMatch = analysisText.match(/\{[\s\S]*\}/);
                      if (jsonMatch) {
                        const parsed = JSON.parse(jsonMatch[0]);

                        return (
                          <div className="space-y-4">
                            {/* Score Section */}
                            {parsed.totalScore && (
                              <div className="p-4 bg-gradient-to-r from-primary-50 to-primary-100 rounded-xl">
                                <div className="flex items-center justify-between">
                                  <span className="text-sm font-semibold text-gray-900">종합 안전도</span>
                                  <div className="flex items-center gap-2">
                                    <div className="text-2xl font-bold text-primary-600">{parsed.totalScore}</div>
                                    <span className="text-xs text-gray-600">/100</span>
                                  </div>
                                </div>
                                <div className="mt-2 w-full bg-gray-300 rounded-full h-2">
                                  <div
                                    className="bg-primary-600 h-2 rounded-full transition-all"
                                    style={{ width: `${Math.min(parsed.totalScore, 100)}%` }}
                                  />
                                </div>
                              </div>
                            )}

                            {/* Summary */}
                            {parsed.summary && (
                              <div className="p-4 bg-blue-50 rounded-xl">
                                <h4 className="text-sm font-semibold text-gray-900 mb-2">📋 요약</h4>
                                <p className="text-sm text-gray-800 leading-relaxed">{parsed.summary}</p>
                              </div>
                            )}

                            {/* Aware (주의 사항) */}
                            {parsed.aware && Array.isArray(parsed.aware) && parsed.aware.length > 0 && (
                              <div className="p-4 bg-yellow-50 border-l-4 border-yellow-500 rounded-xl">
                                <h4 className="text-sm font-semibold text-gray-900 mb-3">⚠️ 주의 사항</h4>
                                <ul className="space-y-2">
                                  {parsed.aware.map((item, idx) => (
                                    <li key={idx} className="flex gap-2 text-sm text-gray-800">
                                      <span className="flex-shrink-0 font-bold text-yellow-600">•</span>
                                      <span>{item}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Highlights */}
                            {parsed.highlights && Array.isArray(parsed.highlights) && parsed.highlights.length > 0 && (
                              <div className="p-4 bg-green-50 rounded-xl">
                                <h4 className="text-sm font-semibold text-gray-900 mb-3">✅ 긍정 요소</h4>
                                <ul className="space-y-2">
                                  {parsed.highlights.map((item, idx) => (
                                    <li key={idx} className="flex gap-2 text-sm text-gray-800">
                                      <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
                                      <span>{item}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Legal Interpretation */}
                            {parsed.legalInterpretation && Array.isArray(parsed.legalInterpretation) && parsed.legalInterpretation.length > 0 && (
                              <div className="p-4 bg-purple-50 rounded-xl">
                                <h4 className="text-sm font-semibold text-gray-900 mb-3">⚖️ 법률 해석</h4>
                                <div className="space-y-3">
                                  {parsed.legalInterpretation.map((item, idx) => (
                                    <div key={idx} className="border-l-2 border-purple-400 pl-3">
                                      <p className="text-xs font-semibold text-gray-900 mb-1">{item.issue}</p>
                                      <p className="text-sm text-gray-800">{item.interpretation}</p>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        );
                      }
                    } catch {
                      // If JSON parsing fails, show as plain text
                    }

                    // Fallback to plain text display
                    return (
                      <div className="p-4 bg-primary-50 rounded-xl">
                        <h3 className="font-semibold text-gray-900 mb-2 text-sm">📋 법률 전문가 분석</h3>
                        <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
                          {analysisText}
                        </p>
                      </div>
                    );
                  })()}
                </div>
              )}

              {/* 분석 일시 */}
              <div className="pt-4 border-t border-gray-200 text-xs text-gray-500">
                분석 일시:{' '}
                {new Date(selectedAnalysis.created_at).toLocaleString('ko-KR')}
              </div>
            </div>

            {/* 모달 하단 버튼 */}
            <div className="sticky bottom-0 bg-white border-t border-gray-200 p-4 space-y-3">
              <button
                onClick={() => {
                  handleRetouchAnalysis(selectedAnalysis);
                  setSelectedAnalysis(null);
                }}
                className="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-3 rounded-xl transition-colors"
              >
                이 분석으로 상담하기
              </button>
              <button
                onClick={() => setSelectedAnalysis(null)}
                className="w-full bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 font-medium py-3 rounded-xl transition-colors"
              >
                닫기
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 플로팅 버튼: 새 계약서 분석 */}
      {!isLoading && analyses.length > 0 && (
        <button
          onClick={() => navigate('/contract/new')}
          className="fixed bottom-24 right-6 bg-primary-600 hover:bg-primary-700 text-white rounded-full px-6 py-4 shadow-2xl transition-all hover:scale-105 z-40 flex items-center gap-2 font-medium"
          title="새 계약서 분석하기"
        >
          <FileText className="w-5 h-5" />
          <span>계약서 분석</span>
        </button>
      )}

      <BottomNav />
    </div>
  );
}
