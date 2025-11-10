import { useState } from 'react';
import { MapPin, Clock, Play, Pause } from 'lucide-react';
import BottomNav from '../components/BottomNav';
import MobileHeader from '../components/MobileHeader';

export default function WorkTimePage() {
  const [isTracking, setIsTracking] = useState(false);
  const [time, setTime] = useState({ hours: 0, minutes: 0, seconds: 0 });
  const [location, setLocation] = useState('위치 정보를 가져오는 중...');

  const handleToggleTracking = () => {
    if (!isTracking) {
      // 위치 정보 가져오기
      if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            setLocation(`위도: ${position.coords.latitude.toFixed(4)}, 경도: ${position.coords.longitude.toFixed(4)}`);
          },
          (error) => {
            setLocation('위치 정보를 가져올 수 없습니다');
          }
        );
      }
    }
    setIsTracking(!isTracking);
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <MobileHeader title="근무 시간 측정" showBack={false} />

      <main className="max-w-md mx-auto px-4 pt-20 pb-8">
        {/* 지도 영역 (placeholder) */}
        <div className="bg-gray-200 rounded-3xl aspect-video mb-6 flex items-center justify-center relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-primary-200 to-primary-400 opacity-30"></div>
          <div className="relative z-10 text-center">
            <MapPin className="w-12 h-12 text-primary-700 mx-auto mb-2" />
            <p className="text-sm text-gray-700">{location}</p>
          </div>
        </div>

        <div className="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <div className="text-center mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">근무시간 측정</h2>

            {/* 타이머 */}
            <div className="text-6xl font-bold text-gray-900 mb-8 font-mono">
              {String(time.hours).padStart(2, '0')} : {String(time.minutes).padStart(2, '0')} : {String(time.seconds).padStart(2, '0')}
            </div>

            {/* 측정 버튼 */}
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={handleToggleTracking}
                className={`py-4 rounded-2xl font-semibold transition-colors ${
                  isTracking
                    ? 'bg-red-500 hover:bg-red-600 text-white'
                    : 'bg-primary-600 hover:bg-primary-700 text-white'
                }`}
              >
                {isTracking ? '정지' : '측정'}
              </button>
              <button
                disabled={isTracking}
                className="bg-gray-200 hover:bg-gray-300 text-gray-700 py-4 rounded-2xl font-semibold transition-colors disabled:opacity-50"
              >
                저장
              </button>
            </div>
          </div>

          {/* 근무 위치 정보 */}
          <div className="border-t border-gray-200 pt-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">근무 위치</span>
              <button className="text-primary-600 hover:text-primary-700">근무 위치 등록</button>
            </div>
            <p className="text-xs text-gray-500 mt-2">{location}</p>
          </div>
        </div>

        {/* 근무 기록 */}
        <div className="bg-white rounded-3xl shadow-sm p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">근무 기록</h3>
          <div className="text-center py-8">
            <Clock className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 text-sm">아직 근무 기록이 없습니다</p>
          </div>
        </div>
      </main>

      <BottomNav />
    </div>
  );
}
