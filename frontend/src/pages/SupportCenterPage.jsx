import { useState, useEffect } from 'react';
import {
  MapPin,
  Phone,
  Clock,
  Navigation2,
  Filter,
  Building2,
} from 'lucide-react';
import AppLayout from '../components/layout/AppLayout';
import { Alert, Button, Card, LoadingState } from '../components/ui';
import SupportCenterMap from '../components/SupportCenterMap';
import EmergencyContacts from '../components/EmergencyContacts';
import { supportCenterAPI } from '../services/api';
import useTranslation from '../hooks/useTranslation';
import i18next from '../i18n/config';

// 기관 유형 (이름은 support.types.* 번역 키)
const CENTER_TYPES = ['labor_office', 'legal_aid', 'foreign_support', 'welfare'];

// 기관 유형별 색상
const centerTypeColors = {
  labor_office: 'bg-blue-100 dark:bg-blue-500/20 text-blue-800 dark:text-blue-200 border-blue-200 dark:border-blue-500/30',
  legal_aid: 'bg-green-100 dark:bg-green-500/20 text-green-800 dark:text-green-200 border-green-200 dark:border-green-500/30',
  foreign_support: 'bg-red-100 dark:bg-red-500/20 text-red-800 dark:text-red-200 border-red-200 dark:border-red-500/30',
  welfare: 'bg-purple-100 dark:bg-purple-500/20 text-purple-800 dark:text-purple-200 border-purple-200 dark:border-purple-500/30',
};

export default function SupportCenterPage() {
  const { t } = useTranslation();
  const [centers, setCenters] = useState([]);
  const [emergencyContacts, setEmergencyContacts] = useState([]);
  const [filteredCenters, setFilteredCenters] = useState([]);
  const [selectedCenter, setSelectedCenter] = useState(null);
  const [userLocation, setUserLocation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 필터 상태
  const [filterType, setFilterType] = useState('all');
  const [sortBy, setSortBy] = useState('distance'); // distance, name

  // 현재 위치 가져오기
  useEffect(() => {
    const isSecureContext = window.isSecureContext;

    if ('geolocation' in navigator && isSecureContext) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const location = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          };
          setUserLocation(location);
          fetchCenters(location);
        },
        (err) => {
          console.error('위치 조회 오류:', err);
          // 기본 위치 사용 안내
          setError(i18next.t('support.locationFallback'));
          fetchCenters(null);
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 5000 }
      );
    } else {
      if (!isSecureContext && window.location.protocol === 'http:') {
        setError(i18next.t('support.httpWarning'));
      }
      fetchCenters(null);
    }
  }, []);

  // 지원 기관 데이터 가져오기
  const fetchCenters = async (location) => {
    try {
      setLoading(true);
      setError(null);

      let result;
      if (location) {
        // 현재 위치 기반 검색
        result = await supportCenterAPI.getNearby(
          location.latitude,
          location.longitude,
          20 // 20km 반경
        );
      } else {
        // 전체 검색
        result = await supportCenterAPI.searchCenters({
          limit: 50,
        });
      }

      setCenters(result.centers || []);
      setFilteredCenters(result.centers || []);
      setEmergencyContacts(result.emergency_contacts || []);
    } catch (err) {
      console.error('지원 기관 조회 오류:', err);
      setError(i18next.t('support.loadFailed'));
    } finally {
      setLoading(false);
    }
  };

  // 필터링 및 정렬
  useEffect(() => {
    let filtered = [...centers];

    // 유형 필터
    if (filterType !== 'all') {
      filtered = filtered.filter((center) => center.type === filterType);
    }

    // 정렬
    if (sortBy === 'distance' && userLocation) {
      filtered.sort((a, b) => (a.distance || Infinity) - (b.distance || Infinity));
    } else if (sortBy === 'name') {
      filtered.sort((a, b) => a.name.localeCompare(b.name));
    }

    setFilteredCenters(filtered);
  }, [filterType, sortBy, centers, userLocation]);

  // 길찾기
  const handleNavigate = (center) => {
    const url = `https://map.naver.com/v5/directions/-/-/-/car?c=${center.location.longitude},${center.location.latitude},15,0,0,0,dh`;
    window.open(url, '_blank');
  };

  // 전화 걸기
  const handleCall = (phone) => {
    window.location.href = `tel:${phone}`;
  };

  if (loading) {
    return (
      <AppLayout title={t('support.title')} width="wide">
        <LoadingState label={t('support.loading')} />
      </AppLayout>
    );
  }

  return (
    <AppLayout
      title={t('support.title')}
      subtitle={t('support.subtitle')}
      width="wide"
      className="space-y-6"
    >
        {/* 에러 메시지 */}
        {error && (
          <Alert tone="danger">{error}</Alert>
        )}

        {/* 필터 & 정렬 */}
        <Card padding="sm" className="space-y-3 lg:space-y-0 lg:flex lg:items-end lg:gap-8">
          {/* 유형 필터 */}
          <div>
            <label className="text-sm font-semibold text-ink-muted mb-2 flex items-center gap-2">
              <Filter className="w-4 h-4" />
              {t('support.filterType')}
            </label>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setFilterType('all')}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  filterType === 'all'
                    ? 'bg-primary-600 text-white'
                    : 'bg-surface-muted text-ink-muted hover:bg-line'
                }`}
              >
                {t('support.all')}
              </button>
              {CENTER_TYPES.map((type) => (
                <button
                  key={type}
                  onClick={() => setFilterType(type)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                    filterType === type
                      ? 'bg-primary-600 text-white'
                      : 'bg-surface-muted text-ink-muted hover:bg-line'
                  }`}
                >
                  {t(`support.types.${type}`)}
                </button>
              ))}
            </div>
          </div>

          {/* 정렬 */}
          <div>
            <label className="text-sm font-semibold text-ink-muted mb-2 block">{t('support.sort')}</label>
            <div className="flex gap-2 lg:w-64">
              <button
                onClick={() => setSortBy('distance')}
                className={`flex-1 px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                  sortBy === 'distance'
                    ? 'bg-primary-100 dark:bg-primary-500/20 text-primary-700 dark:text-primary-300 border border-primary-300 dark:border-primary-500/40'
                    : 'bg-canvas text-ink-muted hover:bg-surface-muted'
                }`}
                disabled={!userLocation}
              >
                {t('support.byDistance')}
              </button>
              <button
                onClick={() => setSortBy('name')}
                className={`flex-1 px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                  sortBy === 'name'
                    ? 'bg-primary-100 dark:bg-primary-500/20 text-primary-700 dark:text-primary-300 border border-primary-300 dark:border-primary-500/40'
                    : 'bg-canvas text-ink-muted hover:bg-surface-muted'
                }`}
              >
                {t('support.byName')}
              </button>
            </div>
          </div>

          {/* 결과 수 */}
          <p className="text-sm text-ink-muted text-center pt-2 lg:pt-0 lg:ml-auto lg:pb-2">
            {t('support.total', { count: filteredCenters.length })}
          </p>
        </Card>

        {/* PC: 왼쪽 지도(스크롤해도 고정), 오른쪽 목록 */}
        <div className="grid gap-6 lg:grid-cols-2 lg:items-start">
        {/* 지도 */}
        <div className="lg:sticky lg:top-24">
          <SupportCenterMap
            centers={filteredCenters}
            userLocation={userLocation}
            onCenterClick={setSelectedCenter}
          />
        </div>

        {/* 지원 기관 리스트 */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-ink">{t('support.listTitle')}</h2>

          {filteredCenters.length === 0 ? (
            <Card padding="lg" className="text-center">
              <MapPin className="w-12 h-12 text-ink-subtle mx-auto mb-3" />
              <p className="text-ink-muted">{t('support.empty')}</p>
            </Card>
          ) : (
            filteredCenters.map((center) => (
              <Card
                key={center.id}
                padding="none"
                className={`p-5 transition-all ${
                  selectedCenter?.id === center.id ? 'ring-2 ring-primary-500' : ''
                }`}
              >
                {/* 기관 유형 배지 */}
                <div className="flex items-start justify-between mb-3">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold border ${
                      centerTypeColors[center.type]
                    }`}
                  >
                    {CENTER_TYPES.includes(center.type) ? t(`support.types.${center.type}`) : center.type}
                  </span>
                  {center.distance && (
                    <span className="text-sm text-ink-muted">
                      {center.distance.toFixed(1)} km
                    </span>
                  )}
                </div>

                {/* 기관명 */}
                <h3 className="text-lg font-bold text-ink mb-2">{center.name}</h3>

                {/* 주소 */}
                <div className="flex items-start gap-2 text-sm text-ink-muted mb-2">
                  <MapPin className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  <span>{center.address}</span>
                </div>

                {/* 연락처 */}
                <div className="flex items-center gap-2 text-sm text-ink-muted mb-2">
                  <Phone className="w-4 h-4 flex-shrink-0" />
                  <a href={`tel:${center.phone}`} className="text-primary-600 dark:text-primary-400 hover:underline">
                    {center.phone}
                  </a>
                </div>

                {/* 운영시간 */}
                <div className="flex items-center gap-2 text-sm text-ink-muted mb-3">
                  <Clock className="w-4 h-4 flex-shrink-0" />
                  <span>{center.hours.weekday}</span>
                </div>

                {/* 제공 서비스 */}
                {center.services && center.services.length > 0 && (
                  <div className="mb-3">
                    <p className="text-xs font-semibold text-ink-muted mb-1">{t('support.services')}</p>
                    <div className="flex flex-wrap gap-1">
                      {center.services.map((service, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-surface-muted text-ink-muted rounded-lg text-xs"
                        >
                          {service}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* 액션 버튼 */}
                <div className="flex gap-2 mt-4">
                  <Button className="flex-1" onClick={() => handleCall(center.phone)}>
                    <Phone className="w-4 h-4" aria-hidden="true" />
                    {t('support.call')}
                  </Button>
                  <Button variant="outline" className="flex-1" onClick={() => handleNavigate(center)}>
                    <Navigation2 className="w-4 h-4" aria-hidden="true" />
                    {t('support.directions')}
                  </Button>
                </div>
              </Card>
            ))
          )}
        </div>
        </div>

        {/* 긴급 연락처 */}
        {emergencyContacts.length > 0 && (
          <div className="pt-2">
            <EmergencyContacts contacts={emergencyContacts} />
          </div>
        )}
    </AppLayout>
  );
}
