import { create } from 'zustand';

// 토스트와 확인 모달의 상태를 한곳에서 관리합니다.
// 화면은 components/feedback/NotificationHost.jsx 가 그립니다.

let nextId = 1;

const useNotifyStore = create((set, get) => ({
  toasts: [],
  dialog: null, // { title, message, confirmText, cancelText, tone, resolve }

  pushToast: ({ type = 'info', message, duration = 3000 }) => {
    const id = nextId++;
    set((s) => ({ toasts: [...s.toasts.slice(-2), { id, type, message }] }));
    if (duration > 0) setTimeout(() => get().dismissToast(id), duration);
    return id;
  },

  dismissToast: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),

  openDialog: (options) =>
    new Promise((resolve) => {
      // 이미 열린 모달이 있으면 취소로 닫고 새 모달을 엽니다.
      get().dialog?.resolve(false);
      set({ dialog: { ...options, resolve } });
    }),

  closeDialog: (result) => {
    const { dialog } = get();
    if (!dialog) return;
    dialog.resolve(result);
    set({ dialog: null });
  },
}));

const show = (type, defaultDuration) => (message, options = {}) =>
  useNotifyStore.getState().pushToast({ type, message, duration: defaultDuration, ...options });

/**
 * 화면 하단에 잠깐 떴다 사라지는 알림.
 * toast.success('저장했습니다'), toast.error('실패했습니다'), toast.info('준비 중입니다')
 */
export const toast = {
  success: show('success', 3000),
  error: show('error', 4500),
  info: show('info', 3000),
  warning: show('warning', 4500),
};

/**
 * window.confirm 대신 쓰는 확인 모달. 확인을 누르면 true, 취소하면 false 로 끝나는 Promise 를 돌려줍니다.
 * const ok = await confirm({ title: '삭제할까요?', message: '되돌릴 수 없어요.', confirmText: '삭제', tone: 'danger' });
 */
export const confirm = ({
  title,
  message = '',
  confirmText = '확인',
  cancelText = '취소',
  tone = 'primary',
}) => useNotifyStore.getState().openDialog({ title, message, confirmText, cancelText, tone });

/**
 * 버튼 하나짜리 안내 모달. 사용자가 꼭 읽어야 하는 긴 안내에 씁니다.
 */
export const alertDialog = ({ title, message = '', confirmText = '확인' }) =>
  useNotifyStore.getState().openDialog({ title, message, confirmText, cancelText: null, tone: 'primary' });

export default useNotifyStore;
