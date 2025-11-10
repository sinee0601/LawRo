import { useNavigate } from 'react-router-dom';
import { Shield } from 'lucide-react';
import MobileHeader from '../components/MobileHeader';
import BottomNav from '../components/BottomNav';

export default function PrivacyPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <MobileHeader title="개인정보 처리 방침" showBack={true} />

      <main className="max-w-md mx-auto px-4 pt-20 pb-8">
        {/* 헤더 */}
        <div className="bg-white rounded-3xl shadow-sm p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <Shield className="w-6 h-6 text-primary-600" />
            <h1 className="text-lg font-bold text-gray-900">개인정보 처리 방침</h1>
          </div>
          <p className="text-sm text-gray-600">
            최종 수정일: 2024년 11월 10일
          </p>
        </div>

        {/* 내용 */}
        <div className="bg-white rounded-3xl shadow-sm p-6 mb-6">
          <div className="space-y-6 text-sm text-gray-700">
            {/* 수집하는 정보 */}
            <section>
              <h2 className="font-bold text-gray-900 mb-2">1. 수집하는 개인정보</h2>
              <p className="text-xs text-gray-600 mb-2">
                LawRo는 다음과 같은 개인정보를 수집합니다:
              </p>
              <ul className="space-y-1 text-xs text-gray-700">
                <li>• 이메일 주소</li>
                <li>• 이름</li>
                <li>• 선호 언어 및 테마 설정</li>
                <li>• 채팅 히스토리 및 계약서 분석 기록</li>
              </ul>
            </section>

            {/* 정보 사용 */}
            <section>
              <h2 className="font-bold text-gray-900 mb-2">2. 개인정보 사용 목적</h2>
              <p className="text-xs text-gray-600 mb-2">
                수집한 개인정보는 다음 목적으로만 사용합니다:
              </p>
              <ul className="space-y-1 text-xs text-gray-700">
                <li>• 서비스 제공 및 개선</li>
                <li>• 사용자 계정 관리</li>
                <li>• 맞춤형 법률 상담 제공</li>
                <li>• 기술적 문제 해결</li>
              </ul>
            </section>

            {/* 정보 보호 */}
            <section>
              <h2 className="font-bold text-gray-900 mb-2">3. 개인정보 보호</h2>
              <p className="text-xs text-gray-700">
                LawRo는 업계 표준 보안 기술을 사용하여 개인정보를 보호합니다. 사용자의 비밀번호는 암호화되어 저장됩니다.
              </p>
            </section>

            {/* 제3자 공유 */}
            <section>
              <h2 className="font-bold text-gray-900 mb-2">4. 개인정보 제3자 공유</h2>
              <p className="text-xs text-gray-700">
                LawRo는 사용자의 명시적 동의 없이 개인정보를 제3자와 공유하지 않습니다. 단, 법적 요청이 있는 경우는 예외입니다.
              </p>
            </section>

            {/* 보관 기간 */}
            <section>
              <h2 className="font-bold text-gray-900 mb-2">5. 정보 보관 기간</h2>
              <p className="text-xs text-gray-700">
                개인정보는 계정 활성 기간 동안 보관되며, 계정 삭제 시 완전히 삭제됩니다. 법적 의무가 있는 경우는 관련 법령에 따라 보관합니다.
              </p>
            </section>

            {/* 사용자 권리 */}
            <section>
              <h2 className="font-bold text-gray-900 mb-2">6. 사용자의 권리</h2>
              <p className="text-xs text-gray-600 mb-2">
                사용자는 다음의 권리를 가집니다:
              </p>
              <ul className="space-y-1 text-xs text-gray-700">
                <li>• 개인정보 조회 및 수정</li>
                <li>• 개인정보 삭제 요청</li>
                <li>• 서비스 탈퇴</li>
              </ul>
            </section>

            {/* 문의 */}
            <section>
              <h2 className="font-bold text-gray-900 mb-2">7. 문의</h2>
              <p className="text-xs text-gray-700">
                개인정보 처리 방침에 대한 문의는 앱 내 "문의하기" 기능을 통해 주시면 됩니다.
              </p>
            </section>
          </div>
        </div>

        {/* 정보 안내 */}
        <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4 mb-6">
          <p className="text-xs text-blue-900">
            이 개인정보 처리 방침은 법적 구속력을 갖는 정식 문서입니다. 서비스 이용으로 본 방침에 동의하신 것으로 간주됩니다.
          </p>
        </div>

        {/* 동의 버튼 */}
        <button
          onClick={() => navigate('/settings')}
          className="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-3 rounded-xl transition-colors"
        >
          확인하고 돌아가기
        </button>
      </main>

      <BottomNav />
    </div>
  );
}
