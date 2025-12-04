import { useState, useEffect, useRef } from 'react';
import useChatStore from '../store/chatStore';
import { ArrowUp, Bot, User, Menu } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import BottomNav from '../components/BottomNav';
import MobileHeader from '../components/MobileHeader';
import ChatHistorySidebar from '../components/ChatHistorySidebar';

export default function ChatPage() {
  const {
    sessions,
    currentSessionId,
    sendMessage,
    createSession,
    isLoading,
    isHistoryLoading,
  } = useChatStore();

  const [input, setInput] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const messagesEndRef = useRef(null);

  const currentSession = currentSessionId ? sessions[currentSessionId] : null;
  const messages = currentSession?.messages || [];

  // Auto-scroll to the latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 계약서 분석 결과가 있으면 자동으로 챗봇에 전송
  useEffect(() => {
    const handleContractAnalysis = async () => {
      const contractDataStr = localStorage.getItem('contractAnalysisData');
      if (!contractDataStr) return;

      try {
        const contractData = JSON.parse(contractDataStr);

        // localStorage에서 데이터 먼저 삭제 (중복 전송 방지)
        localStorage.removeItem('contractAnalysisData');

        // 새로운 세션 생성
        const newSessionId = await createSession();
        console.log('새 계약서 상담 세션 생성:', newSessionId);

        // 분석 결과를 기반으로 간결한 메시지 생성
        const structuredResult = contractData.structuredResult || {};
        const keyTerms = structuredResult.key_terms?.slice(0, 3) || []; // 최대 3개만

        let message = `📋 **계약서 분석 상담**\n\n`;
        message += `**[계약 정보]**\n`;
        message += `• 유형: ${structuredResult.contract_type || '미확인'}\n`;
        message += `• 기간: ${structuredResult.effective_date || '미확인'} ~ ${structuredResult.termination_date || '미확인'}\n`;

        if (keyTerms.length > 0) {
          message += `• 주요 조건:\n`;
          keyTerms.forEach(term => {
            message += `  - ${term}\n`;
          });
        }

        if (contractData.chatbotAnalysis) {
          message += `\n**[AI 분석 요약]**\n`;
          // AI 분석 내용을 200자로 제한
          const analysisPreview = contractData.chatbotAnalysis.length > 200
            ? contractData.chatbotAnalysis.substring(0, 200) + '...'
            : contractData.chatbotAnalysis;
          message += `${analysisPreview}\n`;
        }

        message += `\n위 계약서의 문제점과 주의사항을 자세히 설명해주세요.`;

        // 새 세션에 메시지 전송
        await sendMessage(message);
      } catch (error) {
        console.error('Failed to process contract analysis data:', error);
        localStorage.removeItem('contractAnalysisData');
      }
    };

    handleContractAnalysis();
  }, [createSession, sendMessage]);

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
      handleSend(e);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-100 overflow-x-hidden">
      {/* Mobile Header with Menu Button */}
      <div className="fixed top-0 left-0 right-0 h-14 bg-white border-b border-gray-200 z-50 flex items-center px-4">
        <button
          onClick={() => setIsSidebarOpen(true)}
          className="md:hidden w-10 h-10 flex items-center justify-center text-gray-700 hover:bg-gray-100 rounded-lg"
        >
          <Menu className="w-6 h-6" />
        </button>
        <h1 className="flex-1 text-center font-semibold text-gray-900 md:text-left md:ml-4">상담 챗봇</h1>
        <div className="w-10 md:hidden"></div>
      </div>

      <div className="flex flex-1 overflow-hidden pt-14 pb-14 sm:pb-0">
        {/* Mobile Sidebar Overlay */}
        {isSidebarOpen && (
          <div className="fixed inset-0 z-50 md:hidden">
            <div
              className="absolute inset-0 bg-black/50"
              onClick={() => setIsSidebarOpen(false)}
            ></div>
            <div className="absolute left-0 top-0 bottom-0 w-80 max-w-[85vw] bg-white shadow-xl">
              <ChatHistorySidebar onClose={() => setIsSidebarOpen(false)} />
            </div>
          </div>
        )}

        {/* Desktop Sidebar */}
        <div className="hidden md:flex md:flex-shrink-0">
          <ChatHistorySidebar />
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col relative bg-white overflow-x-hidden">
          {/* Message List */}
          <div className="flex-1 overflow-y-auto overflow-x-hidden pb-32 md:pb-20">
            <div className="max-w-2xl mx-auto px-4 py-6 overflow-x-hidden">
              {isHistoryLoading ? (
                 <div className="flex items-center justify-center h-full text-gray-500">
                   <p>대화 기록을 불러오는 중...</p>
                 </div>
              ) : messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center py-12">
                   <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                     <Bot className="w-8 h-8 text-blue-600" />
                   </div>
                   <p className="text-gray-900 font-medium mb-2">안녕하세요, 법률/노동 상담 챗봇입니다.</p>
                   <p className="text-sm text-gray-600 mb-6">새로운 채팅을 시작하거나, 왼쪽에서 이전 기록을 선택하세요.</p>
                 </div>
              ) : (
                <div className="space-y-6">
                  {messages.map((msg, index) => (
                    <div key={index} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      {msg.role === 'assistant' && (
                        <div className="w-8 h-8 sm:w-9 sm:h-9 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <Bot className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" />
                        </div>
                      )}
                      <div className={`max-w-[85%] sm:max-w-[75%] px-4 py-3 rounded-2xl break-words overflow-hidden ${
                        msg.role === 'user'
                          ? 'bg-blue-600 text-white rounded-br-lg'
                          : 'bg-white shadow-sm border border-gray-200 rounded-bl-lg'
                      }`}
                      style={{
                        overflowWrap: 'break-word',
                        wordBreak: 'break-word',
                        wordWrap: 'break-word'
                      }}>
                        <div className={`prose prose-sm max-w-none ${
                          msg.role === 'user' ? 'text-white' : 'text-gray-800'
                        } [&_p]:my-1 [&_pre]:overflow-x-auto [&_pre]:max-w-full [&_code]:break-words [&_*]:max-w-full [&_a]:break-all`}>
                          <ReactMarkdown>{msg.content}</ReactMarkdown>
                        </div>
                      </div>
                      {msg.role === 'user' && (
                        <div className="w-8 h-8 sm:w-9 sm:h-9 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
                          <User className="w-5 h-5 sm:w-6 sm:h-6 text-gray-600" />
                        </div>
                      )}
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex gap-3 justify-start">
                      <div className="w-8 h-8 sm:w-9 sm:h-9 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <Bot className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" />
                      </div>
                      <div className="px-4 py-3 rounded-2xl bg-white shadow-sm border border-gray-200">
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse delay-75"></div>
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse delay-150"></div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>
          </div>

          {/* Input Form */}
          <div className="fixed bottom-14 left-0 right-0 bg-white/80 backdrop-blur-sm border-t border-gray-200 z-40 md:bottom-16">
            <div className="max-w-2xl mx-auto px-4 py-3">
              <form onSubmit={handleSend} className="flex items-end gap-2">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="메시지를 입력하세요..."
                  className="flex-1 px-4 py-2.5 text-sm border-gray-300 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none max-h-40 bg-gray-50"
                  rows="1"
                  disabled={isLoading || isHistoryLoading}
                />
                <button
                  type="submit"
                  disabled={!input.trim() || isLoading || isHistoryLoading}
                  className="w-10 h-10 bg-blue-600 hover:bg-blue-700 text-white rounded-full flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
                >
                  <ArrowUp className="w-5 h-5" />
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
      <BottomNav />
    </div>
  );
}
