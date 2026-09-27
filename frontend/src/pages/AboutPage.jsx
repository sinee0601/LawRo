import { Info, AlertCircle } from 'lucide-react';
import MobileHeader from '../components/MobileHeader';
import BottomNav from '../components/BottomNav';

export default function AboutPage() {

  const handleComingSoon = () => {
    alert('이 기능은 추후 업데이트 예정입니다. 기다려주세요!');
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <MobileHeader title="앱 설명" showBack={true} />

      <main className="max-w-md mx-auto px-4 pt-20 pb-8">
        {/* 로고 및 기본 정보 */}
        <div className="bg-white rounded-3xl shadow-sm p-8 mb-6 text-center">
          <div className="w-24 h-24 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-4xl font-bold text-primary-600">LR</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">LawRo</h1>
          <p className="text-sm text-gray-600 mb-4">
            외국인 노동자를 위한 AI 법률 상담 플랫폼
          </p>
          <p className="text-xs text-gray-500">Version 1.0.0</p>
        </div>

        {/* 소개 섹션 */}
        <div className="bg-white rounded-3xl shadow-sm p-6 mb-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Info className="w-5 h-5 text-primary-600" />
            LawRo 소개
          </h2>
          <p className="text-sm text-gray-700 leading-relaxed mb-4">
            LawRo는 외국인 노동자를 위한 AI 기반 법률 상담 및 계약서 분석 플랫폼입니다.
          </p>
          <ul className="space-y-2 text-sm text-gray-700">
            <li className="flex items-start gap-2">
              <span className="text-primary-600 font-bold mt-0.5">•</span>
              <span>RAG 기반 AI 챗봇으로 법률 질문에 답변합니다</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary-600 font-bold mt-0.5">•</span>
              <span>OCR과 AI로 계약서를 분석하고 위험 요소를 탐지합니다</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary-600 font-bold mt-0.5">•</span>
              <span>6개 언어를 지원합니다</span>
            </li>
          </ul>
        </div>

        {/* 주요 기능 */}
        <div className="bg-white rounded-3xl shadow-sm p-6 mb-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">주요 기능</h2>
          <div className="space-y-3">
            <div className="p-3 bg-blue-50 rounded-lg">
              <p className="font-medium text-blue-900 text-sm mb-1">법률 상담 챗봇</p>
              <p className="text-xs text-blue-800">
                근로법, 계약서 등 법률 관련 질문에 AI가 답변합니다
              </p>
            </div>
            <div className="p-3 bg-green-50 rounded-lg">
              <p className="font-medium text-green-900 text-sm mb-1">계약서 분석</p>
              <p className="text-xs text-green-800">
                이미지 업로드로 계약서를 OCR 인식하고 법률적 위험을 분석합니다
              </p>
            </div>
            <div className="p-3 bg-purple-50 rounded-lg">
              <p className="font-medium text-purple-900 text-sm mb-1">다국어 지원</p>
              <p className="text-xs text-purple-800">
                한국어, 영어, 중국어, 베트남어, 일본어, 태국어를 지원합니다
              </p>
            </div>
          </div>
        </div>

        {/* 업데이트 예정 기능 */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-2xl p-4 mb-6 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-yellow-900 mb-1">추가 예정 기능</p>
            <ul className="text-xs text-yellow-800 space-y-1">
              <li>• 근무시간 추적</li>
              <li>• 법률 상담 내역 저장</li>
              <li>• PDF 내보내기</li>
            </ul>
          </div>
        </div>

        {/* 문의 섹션 */}
        <div className="bg-white rounded-3xl shadow-sm p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">문의 및 피드백</h2>
          <p className="text-sm text-gray-700 mb-4">
            LawRo에 대한 문의사항이나 피드백은 언제든지 환영합니다.
          </p>
          <button
            onClick={handleComingSoon}
            className="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-3 rounded-xl transition-colors"
          >
            문의하기
          </button>
        </div>
      </main>

      <BottomNav />
    </div>
  );
}
