import React, { useEffect } from 'react';
import useChatStore from '../store/chatStore';
import useAuthStore from '../store/authStore';
import useRequireLogin from '../hooks/useRequireLogin';
import { Plus, MessageSquareText, X, Trash2, LogIn } from 'lucide-react';
import { confirm } from '../store/notifyStore';
import { Button } from './ui';

const ChatHistorySidebar = ({ onClose }) => {
  const {
    sessionList,
    currentSessionId,
    fetchSessionList,
    selectSession,
    createSession,
    deleteSession,
  } = useChatStore();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const requireLogin = useRequireLogin();

  // 대화 기록은 계정에 저장되므로 로그인했을 때만 불러옵니다.
  useEffect(() => {
    if (isAuthenticated) fetchSessionList();
  }, [isAuthenticated, fetchSessionList]);

  const handleNewChat = async () => {
    try {
      await createSession();
      onClose?.(); // Close sidebar on mobile after creating new chat
    } catch (error) {
      console.error("Failed to create new session:", error);
    }
  };

  const handleSelectSession = (sessionId) => {
    selectSession(sessionId);
    onClose?.(); // Close sidebar on mobile after selecting session
  };

  const handleDelete = async (e, sessionId) => {
    e.stopPropagation(); // Prevent session selection when clicking delete
    const ok = await confirm({
      title: '이 채팅 기록을 삭제할까요?',
      message: '삭제한 기록은 되돌릴 수 없어요.',
      confirmText: '삭제',
      tone: 'danger',
    });
    if (ok) {
      deleteSession(sessionId);
    }
  };

  return (
    <div className="w-64 bg-canvas border-r border-line flex flex-col h-full">
      <div className="h-14 px-4 border-b border-line flex items-center justify-between">
        <h2 className="text-lg font-semibold text-ink">채팅 기록</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="md:hidden w-8 h-8 flex items-center justify-center text-ink-muted hover:bg-line rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {!isAuthenticated ? (
        <div className="flex-grow p-4">
          <div className="rounded-card bg-surface border border-line p-4 text-center">
            <MessageSquareText className="w-8 h-8 text-ink-subtle mx-auto mb-3" aria-hidden="true" />
            <p className="text-sm font-medium text-ink">로그인하면 대화가 저장돼요</p>
            <p className="mt-1 text-xs text-ink-muted">지난 상담 내용을 언제든 다시 볼 수 있어요.</p>
            <Button size="sm" variant="outline" fullWidth className="mt-4" onClick={() => requireLogin('/chat')}>
              <LogIn size={16} />
              로그인
            </Button>
          </div>
        </div>
      ) : (
        <>
          <div className="p-2">
            <Button size="sm" fullWidth onClick={handleNewChat}>
              <Plus size={16} />
              새로운 채팅
            </Button>
          </div>
          <div className="flex-grow overflow-y-auto">
            <ul className="space-y-1 p-2">
              {sessionList.map((session) => (
                <li key={session.session_id} className="relative group">
                  <button
                    onClick={() => handleSelectSession(session.session_id)}
                    className={`w-full text-left px-3 py-2.5 rounded-control text-sm transition-all flex items-start gap-3 ${
                      currentSessionId === session.session_id
                        ? 'bg-primary-soft text-primary-800 dark:text-primary-200'
                        : 'text-ink-muted hover:bg-surface-muted hover:text-ink'
                    }`}
                  >
                    <MessageSquareText size={16} className="mt-0.5 shrink-0" />
                    <div className="flex flex-col overflow-hidden pr-6">
                      <span className="font-medium truncate">{session.title}</span>
                      <span className={`text-xs ${
                        currentSessionId === session.session_id ? 'text-primary-600 dark:text-primary-400' : 'text-ink-subtle'
                      }`}>
                        {new Date(session.created_at).toLocaleDateString('ko-KR')}
                      </span>
                    </div>
                  </button>
                  <button
                    onClick={(e) => handleDelete(e, session.session_id)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-md text-ink-subtle hover:text-ink hover:bg-line opacity-100 md:opacity-0 md:group-hover:opacity-100 focus:opacity-100 transition-opacity"
                    aria-label="Delete session"
                  >
                    <Trash2 size={14} />
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
};

export default ChatHistorySidebar;
