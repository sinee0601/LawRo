import { useState, useEffect } from 'react';
import {
  MapPin,
  Phone,
  Clock,
  Navigation2,
  Filter,
  Building2,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import BottomNav from '../components/BottomNav';
import SupportCenterMap from '../components/SupportCenterMap';
import EmergencyContacts from '../components/EmergencyContacts';
import { supportCenterAPI } from '../services/api';

// 기관 유형 한글 매핑
const centerTypeLabels = {
  labor_office: '노동청',
  legal_aid: '법률구조공단',
  foreign_support: '외국인력지원센터',
  welfare: '근로복지공단',
};

// 기관 유형별 색상
const centerTypeColors = {
  labor_office: 'bg-blue-100 text-blue-800 border-blue-200',
  legal_aid: 'bg-green-100 text-green-800 border-green-200',
  foreign_support: 'bg-red-100 text-red-800 border-red-200',
  welfare: 'bg-purple-100 text-purple-800 border-purple-200',
};

export default function SupportCenterPage() {

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
          setError('위치 정보를 가져올 수 없어 서울 기준으로 표시합니다.');
          fetchCenters(null);
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 5000 }
      );
    } else {
      if (!isSecureContext && window.location.protocol === 'http:') {
        setError('⚠️ HTTP 환경에서는 위치 정보를 사용할 수 없습니다. HTTPS 연결을 사용해주세요.');
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
      setError('지원 기관 정보를 불러올 수 없습니다');
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
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 flex items-center justify-center pb-20">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-primary-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">지원 기관 정보를 불러오는 중...</p>
        </div>
        <BottomNav />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 pb-20">
      {/* 헤더 */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-md mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Building2 className="w-7 h-7 text-primary-600" />
            법률 지원 기관
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            가까운 노동청, 법률구조공단 찾기
          </p>
        </div>
      </header>

      <div className="max-w-md mx-auto px-6 py-6 space-y-6">
        {/* 에러 메시지 */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-2xl p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* 필터 & 정렬 */}
        <div className="bg-white rounded-3xl p-4 shadow-sm space-y-3">
          {/* 유형 필터 */}
          <div>
            <label className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <Filter className="w-4 h-4" />
              기관 유형
            </label>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setFilterType('all')}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  filterType === 'all'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                전체
              </button>
              {Object.entries(centerTypeLabels).map(([type, label]) => (
                <button
                  key={type}
                  onClick={() => setFilterType(type)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                    filterType === type
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* 정렬 */}
          <div>
            <label className="text-sm font-semibold text-gray-700 mb-2 block">정렬</label>
            <div className="flex gap-2">
              <button
                onClick={() => setSortBy('distance')}
                className={`flex-1 px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                  sortBy === 'distance'
                    ? 'bg-primary-100 text-primary-700 border border-primary-300'
                    : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                }`}
                disabled={!userLocation}
              >
                거리순
              </button>
              <button
                onClick={() => setSortBy('name')}
                className={`flex-1 px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                  sortBy === 'name'
                    ? 'bg-primary-100 text-primary-700 border border-primary-300'
                    : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                }`}
              >
                이름순
              </button>
            </div>
          </div>

          {/* 결과 수 */}
          <p className="text-sm text-gray-600 text-center pt-2">
            총 <span className="font-bold text-primary-600">{filteredCenters.length}</span>개
            기관
          </p>
        </div>

        {/* 지도 */}
        <SupportCenterMap
          centers={filteredCenters}
          userLocation={userLocation}
          onCenterClick={setSelectedCenter}
        />

        {/* 지원 기관 리스트 */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-gray-800">지원 기관 목록</h2>

          {filteredCenters.length === 0 ? (
            <div className="bg-white rounded-3xl p-8 text-center">
              <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600">해당하는 지원 기관이 없습니다</p>
            </div>
          ) : (
            filteredCenters.map((center) => (
              <div
                key={center.id}
                className={`bg-white rounded-3xl p-5 shadow-sm transition-all ${
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
                    {centerTypeLabels[center.type]}
                  </span>
                  {center.distance && (
                    <span className="text-sm text-gray-500">
                      {center.distance.toFixed(1)} km
                    </span>
                  )}
                </div>

                {/* 기관명 */}
                <h3 className="text-lg font-bold text-gray-900 mb-2">{center.name}</h3>

                {/* 주소 */}
                <div className="flex items-start gap-2 text-sm text-gray-600 mb-2">
                  <MapPin className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  <span>{center.address}</span>
                </div>

                {/* 연락처 */}
                <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                  <Phone className="w-4 h-4 flex-shrink-0" />
                  <a href={`tel:${center.phone}`} className="text-primary-600 hover:underline">
                    {center.phone}
                  </a>
                </div>

                {/* 운영시간 */}
                <div className="flex items-center gap-2 text-sm text-gray-600 mb-3">
                  <Clock className="w-4 h-4 flex-shrink-0" />
                  <span>{center.hours.weekday}</span>
                </div>

                {/* 제공 서비스 */}
                {center.services && center.services.length > 0 && (
                  <div className="mb-3">
                    <p className="text-xs font-semibold text-gray-700 mb-1">제공 서비스:</p>
                    <div className="flex flex-wrap gap-1">
                      {center.services.map((service, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-gray-100 text-gray-700 rounded-lg text-xs"
                        >
                          {service}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* 액션 버튼 */}
                <div className="flex gap-2 mt-4">
                  <button
                    onClick={() => handleCall(center.phone)}
                    className="flex-1 bg-primary-600 hover:bg-primary-700 text-white font-medium py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 transition-colors"
                  >
                    <Phone className="w-4 h-4" />
                    전화하기
                  </button>
                  <button
                    onClick={() => handleNavigate(center)}
                    className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 transition-colors"
                  >
                    <Navigation2 className="w-4 h-4" />
                    길찾기
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* 긴급 연락처 */}
        {emergencyContacts.length > 0 && (
          <div className="mt-8">
            <EmergencyContacts contacts={emergencyContacts} />
          </div>
        )}
      </div>

      <BottomNav />
    </div>
  );
}
