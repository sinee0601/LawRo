import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useChatStore from '../store/chatStore';
import { Loader } from 'lucide-react';

export default function ChatInitializer() {
  const navigate = useNavigate();
  const { startSessionWithAnalysis } = useChatStore();

  useEffect(() => {
    const initializeChat = async () => {
      const analysisDataString = localStorage.getItem('pendingAnalysisForChat');
      const userLanguage = localStorage.getItem('userLanguage') || 'korean';

      if (analysisDataString) {
        try {
          const analysisData = JSON.parse(analysisDataString);
          // 분석 데이터로 새 세션을 시작하고 완료될 때까지 기다립니다.
          await startSessionWithAnalysis(analysisData, userLanguage);
        } catch (error) {
          console.error('Failed to initialize chat with analysis data:', error);
          // 에러가 발생하더라도 일반 채팅 페이지로 이동합니다.
        } finally {
          // 성공 여부와 관계없이 localStorage에서 데이터를 삭제합니다.
          localStorage.removeItem('pendingAnalysisForChat');
        }
      }
      
      // 설정이 완료되면 채팅 페이지로 리디렉션합니다.
      navigate('/chat', { replace: true });
    };

    initializeChat();
  }, [navigate, startSessionWithAnalysis]);

  // 이 컴포넌트는 초기화 중에만 표시됩니다.
  return (
    <div className="fixed inset-0 flex flex-col items-center justify-center bg-white z-[100]">
      <Loader className="w-12 h-12 animate-spin text-primary-600 mb-4" />
      <p className="text-lg font-semibold text-gray-800">상담을 준비 중입니다...</p>
      <p className="text-sm text-gray-600">잠시만 기다려주세요.</p>
    </div>
  );
}
