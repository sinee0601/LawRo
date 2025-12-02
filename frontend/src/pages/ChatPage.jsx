import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import useChatStore from '../store/chatStore';
import useAuthStore from '../store/authStore';
import { ArrowUp } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import BottomNav from '../components/BottomNav';
import MobileHeader from '../components/MobileHeader';

export default function ChatPage() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const {
    sessions,
    currentSessionId,
    createSession,
    sendMessage,
    isLoading
  } = useChatStore();

  const [input, setInput] = useState('');
  const [contractData, setContractData] = useState(null);
  const messagesEndRef = useRef(null);

  const currentSession = currentSessionId ? sessions[currentSessionId] : null;
  const messages = currentSession?.messages || [];

  // 세션이 없으면 새로 생성, 계약서 분석 데이터 확인
  useEffect(() => {
    // 계약서 분석 데이터 확인
    const savedContractData = localStorage.getItem('contractAnalysisData');
    if (savedContractData) {
      try {
        const data = JSON.parse(savedContractData);
        setContractData(data);
        // 한 번 사용 후 삭제
        localStorage.removeItem('contractAnalysisData');
      } catch (error) {
        console.error('Failed to parse contract data:', error);
      }
    }

    // 세션 생성
    if (!currentSessionId) {
      createSession();
    }
  }, [currentSessionId, createSession]);

  // 계약서 데이터가 있으면 자동으로 상담 시작
  useEffect(() => {
    if (contractData && messages.length === 0 && currentSessionId) {
      const analysisPrompt = `다음은 내가 분석 받은 계약서 정보입니다:

📋 계약서 기본 정보:
- 계약 유형: ${contractData.structuredResult?.contract_type || '미확인'}
- 계약 기간: ${contractData.structuredResult?.effective_date || '미명시'} ~ ${contractData.structuredResult?.termination_date || '미명시'}

🔍 주요 계약 조건:
${contractData.structuredResult?.key_terms?.map((term) => `- ${term}`).join('\n') || '없음'}

⚠️ 법률적 위험 요소:
${contractData.structuredResult?.risks?.map((risk) => `- ${risk}`).join('\n') || '없음'}

📊 초기 분석:
${contractData.chatbotAnalysis?.substring(0, 500) || '분석 대기 중'}

이 계약서에 대해 더 자세한 상담을 원합니다. 어떤 부분이 특히 우려되는지 알려주세요.`;

      // 약간의 딜레이 후 백그라운드에서 자동 전송 (사용자 입력 필드에는 표시 안 함)
      setTimeout(() => {
        sendMessage(analysisPrompt);
      }, 100);

      setContractData(null); // 한 번만 실행되도록
    }
  }, [contractData, messages.length, currentSessionId, sendMessage]);

  // 메시지 목록 자동 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const message = input.trim();
    setInput('');

    try {
      await sendMessage(message);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <MobileHeader title="상담 챗봇" showBack={false} />

      {/* 메시지 목록 */}
      <div className="flex-1 overflow-y-auto pt-14 pb-36">
        <div className="max-w-md mx-auto px-4 py-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center py-12">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <p className="text-gray-900 font-medium mb-2">안녕하세요, 법률/노동 상담 챗봇입니다.</p>
              <p className="text-sm text-gray-600 mb-6">상담을 시작하겠습니다. 원하시는 상담 내용을 작성해서 보내주세요.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg, index) => (
                <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'assistant' && (
                    <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center mr-2 flex-shrink-0">
                      <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                  )}
                  <div className={`max-w-[75%] px-4 py-3 rounded-2xl ${
                    msg.role === 'user'
                      ? 'bg-primary-600 text-white rounded-tr-sm'
                      : 'bg-white shadow-sm border border-gray-200 rounded-tl-sm'
                  }`}>
                    {msg.role === 'assistant' ? (
                      <div className="text-sm prose prose-sm max-w-none dark:prose-invert [&>*]:my-1 [&>h1]:text-lg [&>h2]:text-base [&>h3]:text-base [&>h4]:text-sm [&>p]:my-1 [&>ul]:my-1 [&>ol]:my-1 [&>li]:my-0.5">
                        <ReactMarkdown
                          components={{
                            h1: ({ node, ...props }) => <h1 className="font-bold text-lg my-2" {...props} />,
                            h2: ({ node, ...props }) => <h2 className="font-bold text-base my-2" {...props} />,
                            h3: ({ node, ...props }) => <h3 className="font-bold text-base my-2" {...props} />,
                            h4: ({ node, ...props }) => <h4 className="font-bold text-sm my-1.5" {...props} />,
                            p: ({ node, ...props }) => <p className="my-1" {...props} />,
                            strong: ({ node, ...props }) => <strong className="font-bold" {...props} />,
                            em: ({ node, ...props }) => <em className="italic" {...props} />,
                            ul: ({ node, ...props }) => <ul className="list-disc list-inside my-1 ml-2" {...props} />,
                            ol: ({ node, ...props }) => <ol className="list-decimal list-inside my-1 ml-2" {...props} />,
                            li: ({ node, ...props }) => <li className="my-0.5" {...props} />,
                            a: ({ node, ...props }) => <a className="text-primary-600 underline hover:text-primary-700" {...props} />,
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    )}
                  </div>
                  {msg.role === 'user' && (
                    <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center ml-2 flex-shrink-0">
                      <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center mr-2 flex-shrink-0">
                    <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <div className="px-4 py-3 rounded-2xl bg-white shadow-sm border border-gray-200 rounded-tl-sm">
                    <p className="text-sm text-gray-600">작성중</p>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* 입력 폼 */}
      <div className="fixed bottom-16 left-0 right-0 bg-white border-t shadow-lg">
        <div className="max-w-md mx-auto px-4 py-4">
          <form onSubmit={handleSend} className="flex items-end gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="메세지를 입력하세요"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-2xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none max-h-32"
              rows="1"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="w-10 h-10 bg-primary-600 hover:bg-primary-700 text-white rounded-full flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
            >
              <ArrowUp className="w-5 h-5" />
            </button>
          </form>
        </div>
      </div>

      <BottomNav />
    </div>
  );
}
