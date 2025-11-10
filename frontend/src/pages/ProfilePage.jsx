import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { settingsAPI } from '../services/api';
import { User, Mail } from 'lucide-react';
import MobileHeader from '../components/MobileHeader';
import BottomNav from '../components/BottomNav';

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [editName, setEditName] = useState(false);
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSave = async () => {
    setIsSaving(true);
    setError('');
    try {
      await settingsAPI.updateProfile(fullName);
      alert('사용자 정보가 저장되었습니다.');
      setEditName(false);
    } catch (err) {
      setError(err.response?.data?.detail || '저장에 실패했습니다.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <MobileHeader title="내정보" showBack={true} />

      <main className="max-w-md mx-auto px-4 pt-20 pb-8">
        {/* 프로필 카드 */}
        <div className="bg-white rounded-3xl shadow-sm p-6 mb-6">
          {/* 프로필 아이콘 */}
          <div className="flex justify-center mb-6">
            <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center">
              <User className="w-10 h-10 text-primary-600" />
            </div>
          </div>

          {/* 이메일 (읽기 전용) */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-600 mb-2">이메일</label>
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl border border-gray-200">
              <Mail className="w-5 h-5 text-gray-400" />
              <p className="text-gray-900">{user?.email}</p>
            </div>
          </div>

          {/* 이름 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-600 mb-2">이름</label>
            {!editName ? (
              <div
                onClick={() => setEditName(true)}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-xl border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <p className="text-gray-900">{fullName || '이름 미등록'}</p>
                <span className="text-sm text-primary-600 font-medium">수정</span>
              </div>
            ) : (
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-4 py-3 border border-primary-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                placeholder="이름을 입력하세요"
              />
            )}
          </div>

          {/* 수정 버튼 */}
          {editName && (
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => {
                  setEditName(false);
                  setFullName(user?.full_name || '');
                }}
                className="px-4 py-3 bg-white border border-gray-300 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors"
              >
                취소
              </button>
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="px-4 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 disabled:opacity-50 transition-colors"
              >
                {isSaving ? '저장 중...' : '저장'}
              </button>
            </div>
          )}
        </div>

        {/* 계정 정보 */}
        <div className="bg-white rounded-3xl shadow-sm p-6">
          <h3 className="font-bold text-gray-900 mb-4">계정 정보</h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">가입 유형</span>
              <span className="text-gray-900 font-medium">
                {user?.provider === 'google' ? 'Google' :
                 user?.provider === 'kakao' ? 'Kakao' :
                 user?.provider === 'naver' ? 'Naver' :
                 'Email'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">가입일</span>
              <span className="text-gray-900 font-medium">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString('ko-KR') : '-'}
              </span>
            </div>
          </div>
        </div>
      </main>

      <BottomNav />
    </div>
  );
}
