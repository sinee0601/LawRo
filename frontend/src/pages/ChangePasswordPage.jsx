import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { settingsAPI } from '../services/api';
import { Lock, Eye, EyeOff, AlertCircle, CheckCircle } from 'lucide-react';
import MobileHeader from '../components/MobileHeader';
import BottomNav from '../components/BottomNav';

export default function ChangePasswordPage() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const validatePassword = () => {
    if (!currentPassword) {
      setError('현재 비밀번호를 입력해주세요.');
      return false;
    }
    if (!newPassword) {
      setError('새 비밀번호를 입력해주세요.');
      return false;
    }
    if (newPassword.length < 8) {
      setError('새 비밀번호는 8자 이상이어야 합니다.');
      return false;
    }
    if (newPassword !== confirmPassword) {
      setError('새 비밀번호가 일치하지 않습니다.');
      return false;
    }
    if (currentPassword === newPassword) {
      setError('새 비밀번호는 현재 비밀번호와 달라야 합니다.');
      return false;
    }
    return true;
  };

  const handleChangePassword = async () => {
    setError('');
    if (!validatePassword()) return;

    setIsLoading(true);
    try {
      await settingsAPI.changePassword(user.email, currentPassword, newPassword);
      setSuccess(true);
      setTimeout(() => {
        navigate('/settings');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || '비밀번호 변경에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 pb-20 flex flex-col items-center justify-center">
        <MobileHeader title="비밀번호 변경" showBack={true} />
        <div className="flex flex-col items-center justify-center flex-1 px-4">
          <CheckCircle className="w-16 h-16 text-green-600 mb-4" />
          <p className="text-lg font-bold text-gray-900 mb-2">비밀번호가 변경되었습니다</p>
          <p className="text-sm text-gray-600">잠시 후 설정 페이지로 이동합니다.</p>
        </div>
        <BottomNav />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <MobileHeader title="비밀번호 변경" showBack={true} />

      <main className="max-w-md mx-auto px-4 pt-20 pb-8">
        <div className="bg-white rounded-3xl shadow-sm p-6 mb-6">
          <p className="text-sm text-gray-600 mb-6">
            보안을 위해 강력한 비밀번호를 설정해주세요.
          </p>

          {/* 에러 메시지 */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl flex items-start gap-2">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          {/* 현재 비밀번호 */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-600 mb-2">현재 비밀번호</label>
            <div className="relative">
              <input
                type={showPasswords.current ? 'text' : 'password'}
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                placeholder="현재 비밀번호 입력"
              />
              <button
                onClick={() =>
                  setShowPasswords({ ...showPasswords, current: !showPasswords.current })
                }
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPasswords.current ? (
                  <EyeOff className="w-5 h-5" />
                ) : (
                  <Eye className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>

          {/* 새 비밀번호 */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-600 mb-2">새 비밀번호</label>
            <div className="relative">
              <input
                type={showPasswords.new ? 'text' : 'password'}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                placeholder="새 비밀번호 입력 (8자 이상)"
              />
              <button
                onClick={() =>
                  setShowPasswords({ ...showPasswords, new: !showPasswords.new })
                }
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPasswords.new ? (
                  <EyeOff className="w-5 h-5" />
                ) : (
                  <Eye className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>

          {/* 비밀번호 확인 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-600 mb-2">
              새 비밀번호 확인
            </label>
            <div className="relative">
              <input
                type={showPasswords.confirm ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                placeholder="새 비밀번호 다시 입력"
              />
              <button
                onClick={() =>
                  setShowPasswords({ ...showPasswords, confirm: !showPasswords.confirm })
                }
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPasswords.confirm ? (
                  <EyeOff className="w-5 h-5" />
                ) : (
                  <Eye className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>

          {/* 버튼 */}
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => navigate('/settings')}
              className="px-4 py-3 bg-white border border-gray-300 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors"
            >
              취소
            </button>
            <button
              onClick={handleChangePassword}
              disabled={isLoading}
              className="px-4 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
            >
              <Lock className="w-4 h-4" />
              {isLoading ? '변경 중...' : '변경'}
            </button>
          </div>
        </div>
      </main>

      <BottomNav />
    </div>
  );
}
