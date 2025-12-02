import { useState, useEffect, useRef } from 'react';
import { MapPin, Clock, Save, Trash2, AlertCircle, CheckCircle, Navigation, X } from 'lucide-react';
import { worktimeAPI } from '../services/api';
import BottomNav from '../components/BottomNav';
import MobileHeader from '../components/MobileHeader';
import NaverMap from '../components/NaverMap';

export default function WorkTimePage() {
  // ==================== 상태 관리 ====================
  const [isTracking, setIsTracking] = useState(false);
  const [time, setTime] = useState({ hours: 0, minutes: 0, seconds: 0 });
  const [currentLocation, setCurrentLocation] = useState({ latitude: null, longitude: null });
  const [workplace, setWorkplace] = useState(null);
  const [locationStatus, setLocationStatus] = useState(null);
  const [workRecords, setWorkRecords] = useState([]);
  const [currentSessionStart, setCurrentSessionStart] = useState(null);

  // UI 상태
  const [isLoading, setIsLoading] = useState(true);
  const [showWorkplaceModal, setShowWorkplaceModal] = useState(false);
  const [error, setError] = useState(null);
  const [mapLocation, setMapLocation] = useState(null);

  const watchIdRef = useRef(null);

  // ==================== 초기 로드 ====================
  useEffect(() => {
    initializeData();

    // 위치 추적 시작 (권한 허용 시)
    startLocationTracking();

    return () => {
      if (watchIdRef.current) {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
    };
  }, []);

  // ==================== 타이머 로직 ====================
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

  // ==================== 위치 상태 확인 ====================
  useEffect(() => {
    if (currentLocation.latitude && workplace) {
      checkLocationStatus();
    }
  }, [currentLocation, workplace]);

  // ==================== 함수들 ====================

  const initializeData = async () => {
    try {
      setIsLoading(true);

      // 근무지 정보 로드
      const workplaceData = await worktimeAPI.getWorkplace();
      if (workplaceData.workplace) {
        setWorkplace(workplaceData.workplace);
        if (!workplaceData.workplace) {
          setShowWorkplaceModal(true);
        }
      } else {
        setShowWorkplaceModal(true);
      }

      // 근무 기록 로드
      const recordsData = await worktimeAPI.getWorkRecords();
      setWorkRecords(recordsData.records || []);

      setError(null);
    } catch (err) {
      setError('데이터 로드 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const startLocationTracking = () => {
    if ('geolocation' in navigator) {
      watchIdRef.current = navigator.geolocation.watchPosition(
        (position) => {
          setCurrentLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          });
        },
        (error) => {
          console.error('위치 추적 오류:', error);
          setError('위치 추적 권한이 필요합니다.');
        },
        {
          enableHighAccuracy: true,
          timeout: 5000,
          maximumAge: 0,
        }
      );
    } else {
      setError('이 브라우저는 위치 추적을 지원하지 않습니다.');
    }
  };

  const checkLocationStatus = async () => {
    try {
      const status = await worktimeAPI.checkLocationStatus(
        currentLocation.latitude,
        currentLocation.longitude
      );
      setLocationStatus(status);
    } catch (err) {
      console.error('위치 상태 확인 오류:', err);
    }
  };

  const handleSaveWorkplace = async (latitude, longitude, address) => {
    try {
      const result = await worktimeAPI.saveWorkplace(latitude, longitude, address, 500);
      const workplaceData = await worktimeAPI.getWorkplace();
      setWorkplace(workplaceData.workplace);
      setShowWorkplaceModal(false);
      setMapLocation(null);
      setError(null);
    } catch (err) {
      setError('근무지 저장에 실패했습니다.');
      console.error(err);
    }
  };

  const handleToggleTracking = () => {
    if (!workplace) {
      setError('먼저 근무지를 등록해주세요.');
      return;
    }

    if (!locationStatus?.is_within_workplace) {
      setError('근무지 반경 내에 있어야 근무시간을 측정할 수 있습니다.');
      return;
    }

    if (!isTracking) {
      // 측정 시작
      setCurrentSessionStart(new Date());
      setTime({ hours: 0, minutes: 0, seconds: 0 });
    }

    setIsTracking(!isTracking);
  };

  const handleSaveRecord = async () => {
    if (!currentSessionStart || (time.hours === 0 && time.minutes === 0 && time.seconds === 0)) {
      setError('저장할 기록이 없습니다.');
      return;
    }

    try {
      const endTime = new Date();
      const date = currentSessionStart.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      });

      await worktimeAPI.saveWorkRecord(
        currentSessionStart.toISOString(),
        endTime.toISOString(),
        currentLocation,
        date
      );

      // 기록 다시 로드
      const recordsData = await worktimeAPI.getWorkRecords();
      setWorkRecords(recordsData.records || []);

      resetSession();
      setError(null);
    } catch (err) {
      setError('근무 기록 저장에 실패했습니다.');
      console.error(err);
    }
  };

  const handleDeleteRecord = async (recordId) => {
    if (!window.confirm('이 근무 기록을 삭제하시겠습니까?')) return;

    try {
      await worktimeAPI.deleteWorkRecord(recordId);

      // 기록 다시 로드
      const recordsData = await worktimeAPI.getWorkRecords();
      setWorkRecords(recordsData.records || []);

      setError(null);
    } catch (err) {
      setError('근무 기록 삭제에 실패했습니다.');
      console.error(err);
    }
  };

  const resetSession = () => {
    setTime({ hours: 0, minutes: 0, seconds: 0 });
    setCurrentSessionStart(null);
    setIsTracking(false);
  };

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('ko-KR', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateString;
    }
  };

  // ==================== 렌더링 ====================

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 pb-20">
        <MobileHeader title="근무 시간 기록" showBack={false} />
        <main className="max-w-md mx-auto px-4 pt-20 pb-8 flex items-center justify-center">
          <div className="animate-spin">
            <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full" />
          </div>
        </main>
        <BottomNav />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <MobileHeader title="근무 시간 기록" showBack={false} />

      <main className="max-w-md mx-auto px-4 pt-20 pb-8 space-y-6">
        {/* 에러 메시지 */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-2xl flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* 근무지 정보 카드 */}
        <div className="bg-white rounded-3xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-900">📍 근무지 정보</h3>
            {workplace && (
              <button
                onClick={() => setShowWorkplaceModal(true)}
                className="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                변경
              </button>
            )}
          </div>

          {workplace ? (
            <div className="space-y-3 text-sm">
              {workplace.address && (
                <p className="text-gray-700">{workplace.address}</p>
              )}
              <p className="text-xs text-gray-500 font-mono">
                📌 {workplace.latitude.toFixed(6)}, {workplace.longitude.toFixed(6)}
              </p>
              <p className="text-xs text-gray-500">
                반경: {workplace.radius_meters}m
              </p>
            </div>
          ) : (
            <button
              onClick={() => setShowWorkplaceModal(true)}
              className="w-full bg-primary-100 hover:bg-primary-200 text-primary-700 font-medium py-3 rounded-2xl transition-colors"
            >
              근무지 등록하기
            </button>
          )}
        </div>

        {/* 현재 위치 및 상태 */}
        {currentLocation.latitude && (
          <div className="bg-white rounded-3xl shadow-lg p-6">
            <div className="flex items-center gap-2 mb-4">
              <Navigation className="w-5 h-5 text-primary-600" />
              <h3 className="font-semibold text-gray-900">내 위치</h3>
            </div>

            <div className="space-y-3">
              <p className="text-xs text-gray-500 font-mono">
                {currentLocation.latitude.toFixed(6)}, {currentLocation.longitude.toFixed(6)}
              </p>

              {locationStatus && (
                <div className={`p-4 rounded-2xl ${
                  locationStatus.is_within_workplace
                    ? 'bg-green-50 border border-green-200'
                    : 'bg-orange-50 border border-orange-200'
                }`}>
                  <div className="flex items-center gap-2 mb-2">
                    {locationStatus.is_within_workplace ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-orange-600" />
                    )}
                    <span className={`font-medium ${
                      locationStatus.is_within_workplace
                        ? 'text-green-900'
                        : 'text-orange-900'
                    }`}>
                      {locationStatus.is_within_workplace ? '근무지 내' : '근무지 외'}
                    </span>
                  </div>
                  <p className={`text-sm ${
                    locationStatus.is_within_workplace
                      ? 'text-green-700'
                      : 'text-orange-700'
                  }`}>
                    거리: {locationStatus.distance_meters.toFixed(0)}m
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 근무시간 측정 카드 */}
        <div className="bg-white rounded-3xl shadow-lg p-8">
          <div className="text-center mb-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">근무시간 측정</h2>

            {/* 타이머 */}
            <div className="text-6xl font-bold text-gray-900 mb-8 font-mono tracking-wider">
              {String(time.hours).padStart(2, '0')}:{String(time.minutes).padStart(2, '0')}:{String(time.seconds).padStart(2, '0')}
            </div>

            {/* 상태 표시 */}
            {!workplace && (
              <div className="mb-6 p-3 bg-yellow-50 rounded-xl border border-yellow-200">
                <p className="text-sm text-yellow-700">근무지를 먼저 등록해주세요</p>
              </div>
            )}

            {workplace && !locationStatus?.is_within_workplace && (
              <div className="mb-6 p-3 bg-orange-50 rounded-xl border border-orange-200">
                <p className="text-sm text-orange-700">근무지 반경 내에 있어야 측정할 수 있습니다</p>
              </div>
            )}

            {workplace && locationStatus?.is_within_workplace && (
              <div className="mb-6 p-3 bg-green-50 rounded-xl border border-green-200">
                <p className="text-sm text-green-700">✓ 근무시간 측정 가능합니다</p>
              </div>
            )}

            {/* 측정 버튼 */}
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={handleToggleTracking}
                disabled={!workplace || !locationStatus?.is_within_workplace}
                className={`py-4 rounded-2xl font-semibold transition-all duration-200 ${
                  isTracking
                    ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg'
                    : workplace && locationStatus?.is_within_workplace
                    ? 'bg-primary-600 hover:bg-primary-700 text-white shadow-lg'
                    : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                }`}
              >
                {isTracking ? '정지' : '시작'}
              </button>
              <button
                onClick={handleSaveRecord}
                disabled={!currentSessionStart || (time.hours === 0 && time.minutes === 0 && time.seconds === 0)}
                className="bg-primary-600 hover:bg-primary-700 text-white disabled:bg-gray-200 disabled:text-gray-500 py-4 rounded-2xl font-semibold transition-colors disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <Save className="w-5 h-5" />
                저장
              </button>
            </div>
          </div>
        </div>

        {/* 근무 기록 */}
        <div className="bg-white rounded-3xl shadow-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Clock className="w-5 h-5 text-primary-600" />
            <h3 className="font-bold text-gray-900">근무 내역</h3>
            {workRecords.length > 0 && (
              <span className="ml-auto text-sm font-medium text-primary-600">
                {workRecords.length}건
              </span>
            )}
          </div>

          {workRecords.length === 0 ? (
            <div className="text-center py-8">
              <Clock className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500 text-sm">아직 근무 기록이 없습니다</p>
              <p className="text-xs text-gray-400 mt-2">
                근무를 시작하면 기록이 저장됩니다
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {workRecords.map((record) => (
                <div key={record.id} className="bg-gray-50 rounded-2xl p-4 border border-gray-200">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-gray-900">
                        {formatDate(record.start_time)}
                      </p>
                      <p className="text-lg font-bold text-primary-600 mt-1">
                        {formatDuration(record.duration_seconds)}
                      </p>
                      {record.location?.address && (
                        <p className="text-xs text-gray-500 mt-2">
                          📍 {record.location.address}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={() => handleDeleteRecord(record.id)}
                      className="text-red-400 hover:text-red-600 transition-colors p-2"
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

      {/* 근무지 등록 모달 */}
      {showWorkplaceModal && (
        <WorkplaceModal
          onSave={handleSaveWorkplace}
          onClose={() => setShowWorkplaceModal(false)}
          mapLocation={mapLocation}
          setMapLocation={setMapLocation}
        />
      )}

      <BottomNav />
    </div>
  );
}

// ==================== 근무지 등록 모달 컴포넌트 ====================

function WorkplaceModal({ onSave, onClose, mapLocation, setMapLocation }) {
  const [address, setAddress] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    if (!mapLocation) {
      alert('지도에서 위치를 선택해주세요');
      return;
    }

    setIsSaving(true);
    try {
      await onSave(mapLocation.latitude, mapLocation.longitude, address);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end">
      <div className="bg-white w-full rounded-t-3xl max-h-[90vh] overflow-y-auto">
        {/* 헤더 */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-gray-900">근무지 등록</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* 콘텐츠 */}
        <div className="p-6 space-y-4">
          {/* 네이버 지도 */}
          <NaverMap
            latitude={mapLocation?.latitude}
            longitude={mapLocation?.longitude}
            onLocationChange={(location) => setMapLocation(location)}
          />

          {/* 선택된 위치 정보 */}
          {mapLocation && (
            <div className="p-4 bg-primary-50 border border-primary-200 rounded-xl">
              <p className="text-sm font-semibold text-primary-900 mb-2">✓ 위치 선택됨</p>
              <p className="text-xs text-primary-700 font-mono">
                위도: {mapLocation.latitude.toFixed(6)}<br />
                경도: {mapLocation.longitude.toFixed(6)}
              </p>
            </div>
          )}

          {/* 주소 입력 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              근무지 주소 (선택사항)
            </label>
            <input
              type="text"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="예: 서울 강남구 테헤란로 123"
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <p className="text-xs text-gray-500">
            근무지로부터 500m 반경 내에서만 근무시간을 측정할 수 있습니다.
          </p>
        </div>

        {/* 하단 버튼 */}
        <div className="sticky bottom-0 bg-white border-t border-gray-200 p-4 space-y-3">
          <button
            onClick={handleSave}
            disabled={!mapLocation || isSaving}
            className="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-3 rounded-xl transition-colors disabled:bg-gray-300"
          >
            {isSaving ? '저장 중...' : '근무지 등록'}
          </button>
          <button
            onClick={onClose}
            className="w-full bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 font-medium py-3 rounded-xl transition-colors"
          >
            취소
          </button>
        </div>
      </div>
    </div>
  );
}
