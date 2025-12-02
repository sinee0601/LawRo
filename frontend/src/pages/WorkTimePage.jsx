import { useState, useEffect } from 'react';
import { MapPin, Clock, Save, Trash2 } from 'lucide-react';
import BottomNav from '../components/BottomNav';
import MobileHeader from '../components/MobileHeader';
import NaverMap from '../components/NaverMap';

export default function WorkTimePage() {
  const [isTracking, setIsTracking] = useState(false);
  const [time, setTime] = useState({ hours: 0, minutes: 0, seconds: 0 });
  const [location, setLocation] = useState({ latitude: null, longitude: null });
  const [workRecords, setWorkRecords] = useState([]);
  const [currentSessionStart, setCurrentSessionStart] = useState(null);

  // 타이머 로직
  useEffect(() => {
    let intervalId;

    if (isTracking) {
      intervalId = setInterval(() => {
        setTime((prevTime) => {
          let { hours, minutes, seconds } = prevTime;
          seconds += 1;

          if (seconds === 60) {
            seconds = 0;
            minutes += 1;
          }

          if (minutes === 60) {
            minutes = 0;
            hours += 1;
          }

          return { hours, minutes, seconds };
        });
      }, 1000);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isTracking]);

  const handleToggleTracking = () => {
    if (!isTracking) {
      // 측정 시작
      setCurrentSessionStart(new Date());
      setTime({ hours: 0, minutes: 0, seconds: 0 });

      // 현재 위치 가져오기
      if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            setLocation({
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
            });
          },
          (error) => {
            console.error('위치 정보 오류:', error);
          }
        );
      }
    }
    setIsTracking(!isTracking);
  };

  const handleSaveRecord = () => {
    if (currentSessionStart && (time.hours > 0 || time.minutes > 0 || time.seconds > 0)) {
      const newRecord = {
        id: Date.now(),
        startTime: currentSessionStart,
        duration: `${String(time.hours).padStart(2, '0')}:${String(time.minutes).padStart(2, '0')}:${String(time.seconds).padStart(2, '0')}`,
        location: location.latitude ? `${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}` : '위치 없음',
        date: currentSessionStart.toLocaleDateString('ko-KR'),
      };

      setWorkRecords([newRecord, ...workRecords]);
      resetSession();
    }
  };

  const handleDeleteRecord = (id) => {
    setWorkRecords(workRecords.filter((record) => record.id !== id));
  };

  const resetSession = () => {
    setTime({ hours: 0, minutes: 0, seconds: 0 });
    setLocation({ latitude: null, longitude: null });
    setCurrentSessionStart(null);
    setIsTracking(false);
  };

  const handleLocationChange = (newLocation) => {
    setLocation(newLocation);
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <MobileHeader title="근무 시간 측정" showBack={false} />

      <main className="max-w-md mx-auto px-4 pt-20 pb-8">
        {/* 네이버 지도 */}
        <NaverMap
          latitude={location.latitude}
          longitude={location.longitude}
          onLocationChange={handleLocationChange}
        />

        {/* 근무시간 측정 카드 */}
        <div className="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <div className="text-center mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">근무시간 측정</h2>

            {/* 타이머 */}
            <div className="text-6xl font-bold text-gray-900 mb-8 font-mono tracking-wider">
              {String(time.hours).padStart(2, '0')} : {String(time.minutes).padStart(2, '0')} : {String(time.seconds).padStart(2, '0')}
            </div>

            {/* 측정 버튼 */}
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={handleToggleTracking}
                className={`py-4 rounded-2xl font-semibold transition-all duration-200 ${
                  isTracking
                    ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg'
                    : 'bg-primary-600 hover:bg-primary-700 text-white shadow-lg'
                }`}
              >
                {isTracking ? '정지' : '측정'}
              </button>
              <button
                onClick={handleSaveRecord}
                disabled={!currentSessionStart || (time.hours === 0 && time.minutes === 0 && time.seconds === 0)}
                className="bg-gray-200 hover:bg-gray-300 text-gray-700 py-4 rounded-2xl font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <Save className="w-5 h-5" />
                저장
              </button>
            </div>
          </div>

          {/* 근무 위치 정보 */}
          <div className="border-t border-gray-200 pt-4">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-gray-600 font-semibold">근무 위치</span>
            </div>
            {location.latitude && location.longitude ? (
              <p className="text-sm text-primary-600 font-mono">
                위도: {location.latitude.toFixed(6)}<br />
                경도: {location.longitude.toFixed(6)}
              </p>
            ) : (
              <p className="text-xs text-gray-500">지도에서 위치를 선택하거나 측정을 시작하세요</p>
            )}
          </div>
        </div>

        {/* 근무 기록 */}
        <div className="bg-white rounded-3xl shadow-sm p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">근무 기록</h3>
          {workRecords.length === 0 ? (
            <div className="text-center py-8">
              <Clock className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500 text-sm">아직 근무 기록이 없습니다</p>
            </div>
          ) : (
            <div className="space-y-3">
              {workRecords.map((record) => (
                <div key={record.id} className="bg-gray-50 rounded-2xl p-4 border border-gray-200">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-gray-900">
                        {record.date}
                      </p>
                      <p className="text-lg font-bold text-primary-600 mt-1">
                        {record.duration}
                      </p>
                      <p className="text-xs text-gray-500 mt-2">
                        📍 {record.location}
                      </p>
                    </div>
                    <button
                      onClick={() => handleDeleteRecord(record.id)}
                      className="text-red-500 hover:text-red-700 transition-colors p-2"
                      title="삭제"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      <BottomNav />
    </div>
  );
}
