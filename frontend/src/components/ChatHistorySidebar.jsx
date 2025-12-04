import React, { useEffect } from 'react';
import useChatStore from '../store/chatStore';
import { Plus, MessageSquareText, X, Trash2 } from 'lucide-react';

const ChatHistorySidebar = ({ onClose }) => {
  const {
    sessionList,
    currentSessionId,
    fetchSessionList,
    selectSession,
    createSession,
    deleteSession,
  } = useChatStore();

  useEffect(() => {
    fetchSessionList();
  }, [fetchSessionList]);

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

  const handleDelete = (e, sessionId) => {
    e.stopPropagation(); // Prevent session selection when clicking delete
    if (window.confirm('이 채팅 기록을 정말로 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
      deleteSession(sessionId);
    }
  };

  return (
    <div className="w-64 bg-gray-50 border-r border-gray-200 flex flex-col h-full">
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">채팅 기록</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="md:hidden w-8 h-8 flex items-center justify-center text-gray-600 hover:bg-gray-200 rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>
      <div className="p-2">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all"
        >
          <Plus size={16} />
          새로운 채팅
        </button>
      </div>
      <div className="flex-grow overflow-y-auto">
        <ul className="space-y-1 p-2">
          {sessionList.map((session) => (
            <li key={session.session_id} className="relative group">
              <button
                onClick={() => handleSelectSession(session.session_id)}
                className={`w-full text-left px-3 py-2.5 rounded-md text-sm transition-all flex items-start gap-3 ${
                  currentSessionId === session.session_id
                    ? 'bg-blue-100 text-blue-800'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`}
              >
                <MessageSquareText size={16} className="mt-0.5 shrink-0" />
                <div className="flex flex-col overflow-hidden pr-6">
                  <span className="font-medium truncate">{session.title}</span>
                  <span className={`text-xs ${
                    currentSessionId === session.session_id ? 'text-blue-600' : 'text-gray-400'
                  }`}>
                    {new Date(session.created_at).toLocaleDateString('ko-KR')}
                  </span>
                </div>
              </button>
              <button
                onClick={(e) => handleDelete(e, session.session_id)}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-md text-gray-400 hover:text-gray-800 hover:bg-gray-200 opacity-0 group-hover:opacity-100 transition-opacity"
                aria-label="Delete session"
              >
                <Trash2 size={14} />
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ChatHistorySidebar;
