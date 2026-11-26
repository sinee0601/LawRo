





import { useState, useEffect, useRef } from 'react';
import { MapPin, Clock, Save, Trash2, Navigation } from 'lucide-react';
import { worktimeAPI } from '../services/api';
import AppLayout from '../components/layout/AppLayout';
import NaverMap from '../components/NaverMap';
import { Alert, Button, Card, EmptyState, Input, LoadingState, Sheet } from '../components/ui';
import { toast, confirm } from '../store/notifyStore';
import useTranslation from '../hooks/useTranslation';
import i18next from '../i18n/config';

// 근무지로 인정하는 반경 (m)
const WORKPLACE_RADIUS = 500;

export default function WorkTimePage() {
  const { t, language } = useTranslation();
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
    const { latitude, longitude } = currentLocation;
    if (!latitude || !workplace) return;

    const checkLocationStatus = async () => {
      try {
        const status = await worktimeAPI.checkLocationStatus(latitude, longitude);
        setLocationStatus(status);
      } catch (err) {
        console.error('위치 상태 확인 오류:', err);
      }
    };

    checkLocationStatus();
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
      setError(i18next.t('workTime.errors.load'));
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
          if (error.code === 3) {
            console.warn('위치 조회 타임아웃. 권한을 확인하거나 GPS를 켜세요.');
          }
          setError(i18next.t('workTime.errors.trackingPermission'));
        },
        {
          enableHighAccuracy: true,
          timeout: 30000,
          maximumAge: 5000,
        }
      );
    } else {
      setError(i18next.t('workTime.errors.trackingUnsupported'));
    }
  };

  const handleSaveWorkplace = async (latitude, longitude, address) => {
    try {
      await worktimeAPI.saveWorkplace(latitude, longitude, address, WORKPLACE_RADIUS);
      const workplaceData = await worktimeAPI.getWorkplace();
      setWorkplace(workplaceData.workplace);
      setShowWorkplaceModal(false);
      setMapLocation(null);
      setError(null);
    } catch (err) {
      setError(t('workTime.errors.saveWorkplace'));
      console.error(err);
    }
  };

  const handleToggleTracking = () => {
    if (!workplace) {
      setError(t('workTime.errors.registerFirst'));
      return;
    }

    if (!locationStatus?.is_within_workplace) {
      setError(t('workTime.errors.mustBeInside'));
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
      setError(t('workTime.errors.nothingToSave'));
      return;
    }

    try {
      const endTime = new Date();
      // Date 형식: YYYY-MM-DD (Backend와 일관성 유지)
      const date = currentSessionStart.toISOString().split('T')[0];

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
      setError(t('workTime.errors.saveRecord'));
      console.error(err);
    }
  };

  const handleDeleteRecord = async (recordId) => {
    const ok = await confirm({
      title: t('workTime.deleteTitle'),
      message: t('workTime.deleteMessage'),
      confirmText: t('common.delete'),
      tone: 'danger',
    });
    if (!ok) return;

    try {
      await worktimeAPI.deleteWorkRecord(recordId);

      // 기록 다시 로드
      const recordsData = await worktimeAPI.getWorkRecords();
      setWorkRecords(recordsData.records || []);

      setError(null);
    } catch (err) {
      setError(t('workTime.errors.deleteRecord'));
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
      return date.toLocaleString(language, {
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
      <AppLayout title={t('workTime.title')} width="wide">
        <LoadingState />
      </AppLayout>
    );
  }

  return (
    <AppLayout title={t('workTime.title')} subtitle={t('workTime.subtitle')} width="wide" className="space-y-6">
        {/* 에러 메시지 */}
        {error && (
          <Alert tone="danger">{error}</Alert>
        )}

        <div className="grid gap-6 lg:grid-cols-5 lg:items-start">
          {/* 모바일에서는 근무지 정보가 먼저, PC에서는 오른쪽 칸 */}
          <div className="space-y-6 lg:col-span-2 lg:order-2 lg:sticky lg:top-24">
            {/* 근무지 정보 카드 */}
            <Card>
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-ink">📍 {t('workTime.workplace')}</h3>
                {workplace && (
                  <button
                    onClick={() => setShowWorkplaceModal(true)}
                    className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
                  >
                    {t('common.change')}
                  </button>
                )}
              </div>

              {workplace ? (
                <div className="space-y-3 text-sm">
                  {workplace.address && (
                    <p className="text-ink">{workplace.address}</p>
                  )}
                  <p className="text-xs text-ink-muted font-mono">
                    📌 {workplace.latitude.toFixed(6)}, {workplace.longitude.toFixed(6)}
                  </p>
                  <p className="text-xs text-ink-muted">
                    {t('workTime.radius', { radius: workplace.radius_meters })}
                  </p>
                </div>
              ) : (
                <Button variant="secondary" size="lg" fullWidth onClick={() => setShowWorkplaceModal(true)}>
                  {t('workTime.register')}
                </Button>
              )}
            </Card>

            {/* 현재 위치 및 상태 */}
            {currentLocation.latitude && (
              <Card>
                <div className="flex items-center gap-2 mb-4">
                  <Navigation className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                  <h3 className="font-semibold text-ink">{t('workTime.myLocation')}</h3>
                </div>

                <div className="space-y-3">
                  <p className="text-xs text-ink-muted font-mono">
                    {currentLocation.latitude.toFixed(6)}, {currentLocation.longitude.toFixed(6)}
                  </p>

                  {locationStatus && (
                    <Alert
                      tone={locationStatus.is_within_workplace ? 'success' : 'warning'}
                      title={locationStatus.is_within_workplace ? t('workTime.inside') : t('workTime.outside')}
                    >
                      {t('workTime.distance', { distance: locationStatus.distance_meters.toFixed(0) })}
                    </Alert>
                  )}
                </div>
              </Card>
            )}
          </div>

          <div className="space-y-6 lg:col-span-3 lg:order-1">
            {/* 근무시간 측정 카드 */}
            <Card padding="lg">
              <div className="text-center mb-6">
                <h2 className="text-lg font-bold text-ink mb-4">{t('workTime.measure')}</h2>

                {/* 타이머 */}
                <div className="text-5xl sm:text-6xl font-bold text-ink mb-8 font-mono tabular-nums tracking-tight sm:tracking-wider whitespace-nowrap">
                  {String(time.hours).padStart(2, '0')}:{String(time.minutes).padStart(2, '0')}:{String(time.seconds).padStart(2, '0')}
                </div>

                {/* 상태 표시 */}
                {!workplace && (
                  <Alert tone="warning" className="mb-6 text-left">{t('workTime.needWorkplace')}</Alert>
                )}

                {workplace && !locationStatus?.is_within_workplace && (
                  <Alert tone="warning" className="mb-6 text-left">{t('workTime.needInside')}</Alert>
                )}

                {workplace && locationStatus?.is_within_workplace && (
                  <Alert tone="success" className="mb-6 text-left">{t('workTime.ready')}</Alert>
                )}

                {/* 측정 버튼 */}
                <div className="grid grid-cols-2 gap-3">
                  <Button
                    size="xl"
                    variant={isTracking ? 'danger' : 'primary'}
                    onClick={handleToggleTracking}
                    disabled={!workplace || !locationStatus?.is_within_workplace}
                    className="shadow-raised"
                  >
                    {isTracking ? t('workTime.stop') : t('workTime.start')}
                  </Button>
                  <Button
                    size="xl"
                    variant="outline"
                    onClick={handleSaveRecord}
                    disabled={!currentSessionStart || (time.hours === 0 && time.minutes === 0 && time.seconds === 0)}
                  >
                    <Save className="w-5 h-5" />
                    {t('common.save')}
                  </Button>
                </div>
              </div>
            </Card>

            {/* 근무 기록 */}
            <Card>
              <div className="flex items-center gap-2 mb-4">
                <Clock className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                <h3 className="font-bold text-ink">{t('workTime.records')}</h3>
                {workRecords.length > 0 && (
                  <span className="ml-auto text-sm font-medium text-primary-600 dark:text-primary-400">
                    {t('workTime.recordCount', { count: workRecords.length })}
                  </span>
                )}
              </div>

              {workRecords.length === 0 ? (
                <EmptyState icon={Clock} title={t('workTime.empty')} description={t('workTime.emptyHint')} />
              ) : (
                <div className="grid gap-3 sm:grid-cols-2">
                  {workRecords.map((record) => (
                    <div key={record.id} className="bg-canvas rounded-2xl p-4 border border-line">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="text-sm font-semibold text-ink">
                            {formatDate(record.start_time)}
                          </p>
                          <p className="text-lg font-bold text-primary-600 dark:text-primary-400 mt-1">
                            {formatDuration(record.duration_seconds)}
                          </p>
                          {record.location?.address && (
                            <p className="text-xs text-ink-muted mt-2">
                              📍 {record.location.address}
                            </p>
                          )}
                        </div>
                        <button
                          onClick={() => handleDeleteRecord(record.id)}
                          className="text-ink-subtle hover:text-danger transition-colors p-2 rounded-control focus-visible:outline-none focus-visible:shadow-focus"
                          title={t('common.delete')}
                          aria-label={t('common.delete')}
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        </div>

      {/* 근무지 등록 모달 */}
      {showWorkplaceModal && (
        <WorkplaceModal
          onSave={handleSaveWorkplace}
          onClose={() => setShowWorkplaceModal(false)}
          mapLocation={mapLocation}
          setMapLocation={setMapLocation}
        />
      )}

    </AppLayout>
  );
}

// ==================== 근무지 등록 모달 컴포넌트 ====================

function WorkplaceModal({ onSave, onClose, mapLocation, setMapLocation }) {
  const { t } = useTranslation();
  const [address, setAddress] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    if (!mapLocation) {
      toast.warning(t('workTime.modal.selectOnMap'));
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
    <Sheet
      title={t('workTime.modal.title')}
      onClose={onClose}
      footer={
        <>
          <Button size="lg" fullWidth onClick={handleSave} disabled={!mapLocation || isSaving}>
            {isSaving ? t('common.saving') : t('workTime.modal.submit')}
          </Button>
          <Button variant="outline" size="lg" fullWidth onClick={onClose}>
            {t('common.cancel')}
          </Button>
        </>
      }
    >
        <div className="space-y-4">
          {/* 네이버 지도 */}
          <NaverMap
            latitude={mapLocation?.latitude}
            longitude={mapLocation?.longitude}
            onLocationChange={(location) => setMapLocation(location)}
          />

          {/* 선택된 위치 정보 */}
          {mapLocation && (
            <div className="p-4 bg-primary-50 dark:bg-primary-500/10 border border-primary-200 dark:border-primary-500/30 rounded-xl">
              <p className="text-sm font-semibold text-primary-900 dark:text-primary-200 mb-2">✓ {t('workTime.modal.selected')}</p>
              <p className="text-xs text-primary-700 dark:text-primary-300 font-mono">
                {t('workTime.modal.latitude', { value: mapLocation.latitude.toFixed(6) })}<br />
                {t('workTime.modal.longitude', { value: mapLocation.longitude.toFixed(6) })}
              </p>
            </div>
          )}

          {/* 주소 입력 */}
          <Input
            label={t('workTime.modal.address')}
            type="text"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder={t('workTime.modal.addressPlaceholder')}
          />

          <p className="text-xs text-ink-muted">
            {t('workTime.modal.radiusNote', { radius: WORKPLACE_RADIUS })}
          </p>
        </div>
    </Sheet>
  );
}
