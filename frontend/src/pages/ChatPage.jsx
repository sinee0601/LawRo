import { useState, useEffect, useRef } from 'react';
import useChatStore from '../store/chatStore';
import useAuthStore from '../store/authStore';
import useRequireLogin from '../hooks/useRequireLogin';
import { ArrowUp, Bot, User, Menu } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import AppLayout from '../components/layout/AppLayout';
import ChatHistorySidebar from '../components/ChatHistorySidebar';
import { Button, Textarea } from '../components/ui';

// 세션이 없을 때 매 렌더마다 새 배열이 생기지 않도록 고정된 빈 배열을 씁니다.
const EMPTY_MESSAGES = [];

// 비로그인 상태에서 보내려던 메시지를 로그인하고 돌아올 때까지 잠시 보관합니다.
const DRAFT_KEY = 'lawro:chat-draft';

function readDraft() {
  try {
    return sessionStorage.getItem(DRAFT_KEY) ?? '';
  } catch {
    return '';
  }
}

function writeDraft(value) {
  try {
    if (value) sessionStorage.setItem(DRAFT_KEY, value);
    else sessionStorage.removeItem(DRAFT_KEY);
  } catch {
    // 저장소를 쓸 수 없는 환경이면 초안 보관만 건너뜁니다.
  }
}

export default function ChatPage() {
  const {
    sessions,
    currentSessionId,
    sendMessage,
    isLoading,
    isHistoryLoading,
  } = useChatStore();

  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const requireLogin = useRequireLogin();
  const [input, setInput] = useState(readDraft);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const messagesEndRef = useRef(null);

  const currentSession = currentSessionId ? sessions[currentSessionId] : null;
  const messages = currentSession?.messages ?? EMPTY_MESSAGES;

  // 로그인 후 돌아왔다면 보관해 둔 초안을 입력창에 채웠으니 보관함은 비웁니다.
  useEffect(() => {
    if (isAuthenticated) writeDraft('');
  }, [isAuthenticated]);

  // Auto-scroll to the latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    // 비로그인이면 쓰던 메시지를 보관하고 로그인으로 보냅니다. 로그인 후 이 화면으로 돌아와 입력창에 다시 채워져요.
    if (!isAuthenticated) {
      writeDraft(input);
      requireLogin('/chat');
      return;
    }

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
    <AppLayout
      title="상담 챗봇"
      fill
      leading={
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsSidebarOpen(true)}
          aria-label="대화 목록 열기"
          className="md:hidden -ml-2"
        >
          <Menu className="w-6 h-6" />
        </Button>
      }
    >
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
        <div className="flex-1 min-w-0 flex flex-col bg-surface">
          {/* Message List */}
          <div className="flex-1 min-h-0 overflow-y-auto">
            <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6">
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
                   <p className="text-sm text-ink-muted mb-6">
                     {isAuthenticated
                       ? '새로운 채팅을 시작하거나, 왼쪽에서 이전 기록을 선택하세요.'
                       : '근로계약, 임금, 근무시간처럼 궁금한 점을 적어 보세요. 메시지를 보내면 로그인 화면으로 이동해요.'}
                   </p>
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
                        <div className={`prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1 prose-ol:my-1 prose-li:my-0.5 prose-headings:mt-3 prose-headings:mb-1 prose-pre:my-2 ${
                          msg.role === 'user' ? 'prose-invert' : ''
                        }`}>
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
          <div className="shrink-0 bg-surface border-t border-line">
            <div className="max-w-3xl mx-auto px-4 sm:px-6 py-3">
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
    </AppLayout>
  );
}
