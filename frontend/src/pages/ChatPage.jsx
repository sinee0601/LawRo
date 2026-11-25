import { useState, useEffect, useRef } from 'react';
import useChatStore from '../store/chatStore';
import { ArrowUp, Bot, User, Menu } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import BottomNav from '../components/BottomNav';
import MobileHeader from '../components/MobileHeader';
import ChatHistorySidebar from '../components/ChatHistorySidebar';
import { Button, Textarea } from '../components/ui';

export default function ChatPage() {
  const {
    sessions,
    currentSessionId,
    sendMessage,
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
    <div className="h-screen flex flex-col bg-canvas">
      {/* Mobile Header with Menu Button */}
      <div className="fixed top-0 left-0 right-0 h-14 bg-surface border-b border-line z-50 flex items-center px-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsSidebarOpen(true)}
          aria-label="대화 목록 열기"
          className="md:hidden"
        >
          <Menu className="w-6 h-6" />
        </Button>
        <h1 className="flex-1 text-center font-semibold text-ink md:text-left md:ml-4">상담 챗봇</h1>
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
            <div className="absolute left-0 top-0 bottom-0 w-80 max-w-[85vw] bg-surface shadow-xl">
              <ChatHistorySidebar onClose={() => setIsSidebarOpen(false)} />
            </div>
          </div>
        )}

        {/* Desktop Sidebar */}
        <div className="hidden md:flex md:flex-shrink-0">
          <ChatHistorySidebar />
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col relative bg-surface">
          {/* Message List */}
          <div className="flex-1 overflow-y-auto pb-32 md:pb-20">
            <div className="max-w-2xl mx-auto px-4 py-6">
              {isHistoryLoading ? (
                 <div className="flex items-center justify-center h-full text-ink-muted">
                   <p>대화 기록을 불러오는 중...</p>
                 </div>
              ) : messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center py-12">
                   <div className="w-16 h-16 bg-primary-50 dark:bg-primary-500/10 rounded-full flex items-center justify-center mb-4">
                     <Bot className="w-8 h-8 text-primary-600 dark:text-primary-400" />
                   </div>
                   <p className="text-ink font-medium mb-2">안녕하세요, 법률/노동 상담 챗봇입니다.</p>
                   <p className="text-sm text-ink-muted mb-6">새로운 채팅을 시작하거나, 왼쪽에서 이전 기록을 선택하세요.</p>
                 </div>
              ) : (
                <div className="space-y-6">
                  {messages.map((msg, index) => (
                    <div key={index} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      {msg.role === 'assistant' && (
                        <div className="w-8 h-8 sm:w-9 sm:h-9 bg-primary-50 dark:bg-primary-500/10 rounded-full flex items-center justify-center flex-shrink-0">
                          <Bot className="w-5 h-5 sm:w-6 sm:h-6 text-primary-600 dark:text-primary-400" />
                        </div>
                      )}
                      <div className={`max-w-[85%] sm:max-w-[75%] px-4 py-3 rounded-2xl break-words ${
                        msg.role === 'user'
                          ? 'bg-primary text-primary-foreground rounded-br-lg'
                          : 'bg-surface text-ink shadow-card border border-line rounded-bl-lg'
                      }`}>
                        <div className="prose prose-sm max-w-none text-inherit [&_p]:my-1">
                          <ReactMarkdown>{msg.content}</ReactMarkdown>
                        </div>
                      </div>
                      {msg.role === 'user' && (
                        <div className="w-8 h-8 sm:w-9 sm:h-9 bg-line-strong rounded-full flex items-center justify-center flex-shrink-0">
                          <User className="w-5 h-5 sm:w-6 sm:h-6 text-ink-muted" />
                        </div>
                      )}
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex gap-3 justify-start">
                      <div className="w-8 h-8 sm:w-9 sm:h-9 bg-primary-50 dark:bg-primary-500/10 rounded-full flex items-center justify-center flex-shrink-0">
                        <Bot className="w-5 h-5 sm:w-6 sm:h-6 text-primary-600 dark:text-primary-400" />
                      </div>
                      <div className="px-4 py-3 rounded-2xl bg-surface shadow-card border border-line">
                        <div className="flex items-center gap-2 text-sm text-ink-muted">
                          <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse"></div>
                          <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse delay-75"></div>
                          <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse delay-150"></div>
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
          <div className="fixed bottom-14 left-0 right-0 bg-surface/80 backdrop-blur-sm border-t border-line z-40 md:bottom-16">
            <div className="max-w-2xl mx-auto px-4 py-3">
              <form onSubmit={handleSend} className="flex items-end gap-2">
                <div className="flex-1">
                  <Textarea
                    variant="filled"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="메시지를 입력하세요..."
                    aria-label="메시지 입력"
                    className="block resize-none max-h-40"
                    rows="1"
                    disabled={isLoading || isHistoryLoading}
                  />
                </div>
                <Button
                  type="submit"
                  size="icon"
                  pill
                  aria-label="보내기"
                  disabled={!input.trim() || isLoading || isHistoryLoading}
                  className="flex-shrink-0"
                >
                  <ArrowUp className="w-5 h-5" />
                </Button>
              </form>
            </div>
          </div>
        </div>
      </div>
      <BottomNav />
    </div>
  );
}
