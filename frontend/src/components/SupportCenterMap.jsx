import { useEffect, useRef, useState } from 'react';
import { MapPin, Navigation } from 'lucide-react';
import { toast, alertDialog } from '../store/notifyStore';
import useTranslation from '../hooks/useTranslation';
import i18next from '../i18n/config';

export default function SupportCenterMap({ centers, onCenterClick, userLocation }) {
  const { t } = useTranslation();
  const mapElement = useRef(null);
  const mapInstance = useRef(null);
  const markers = useRef([]);
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState(null);

  // 기관 유형별 마커 색상
  const getMarkerIcon = (centerType) => {
    const colors = {
      labor_office: '#1E40AF', // 파란색 - 노동청
      legal_aid: '#059669', // 초록색 - 법률구조공단
      foreign_support: '#DC2626', // 빨간색 - 외국인력지원센터
      welfare: '#7C3AED', // 보라색 - 근로복지공단
    };

    const color = colors[centerType] || '#6B7280';

    return {
      content: `<div style="
        background-color: ${color};
        border: 2px solid white;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      "></div>`,
      size: new window.naver.maps.Size(24, 24),
      anchor: new window.naver.maps.Point(12, 12),
    };
  };

  // 네이버 지도 API 로드 확인
  useEffect(() => {
    if (window.naver && window.naver.maps) {
      setIsLoaded(true);
      return;
    }

    if (window.naverMapReady) {
      setIsLoaded(true);
      return;
    }

    const handleNaverMapLoaded = () => setIsLoaded(true);
    const handleNaverMapError = (event) => {
      console.error('❌ 네이버 지도 API 로드 실패:', event.detail?.error);
      setError(event.detail?.error || i18next.t('map.authFailed'));
    };

    window.addEventListener('naverMapLoaded', handleNaverMapLoaded);
    window.addEventListener('naverMapError', handleNaverMapError);

    return () => {
      window.removeEventListener('naverMapLoaded', handleNaverMapLoaded);
      window.removeEventListener('naverMapError', handleNaverMapError);
    };
  }, []);

  // 지도 초기화
  useEffect(() => {
    if (!isLoaded || !mapElement.current || !window.naver || !window.naver.maps) return;
    if (mapInstance.current) return;

    try {
      // 사용자 위치 또는 서울 시청 기본 위치
      const defaultLat = userLocation?.latitude || 37.5665;
      const defaultLng = userLocation?.longitude || 126.978;

      const mapOptions = {
        center: new window.naver.maps.LatLng(defaultLat, defaultLng),
        zoom: 12,
        minZoom: 8,
        maxZoom: 18,
        mapTypeControl: true,
      };

      mapInstance.current = new window.naver.maps.Map(mapElement.current, mapOptions);

      // 사용자 위치 마커 (파란색)
      if (userLocation) {
        new window.naver.maps.Marker({
          position: new window.naver.maps.LatLng(userLocation.latitude, userLocation.longitude),
          map: mapInstance.current,
          icon: {
            content: `<div style="
              background-color: #3B82F6;
              border: 3px solid white;
              border-radius: 50%;
              width: 20px;
              height: 20px;
              box-shadow: 0 2px 6px rgba(59, 130, 246, 0.5);
            "></div>`,
            size: new window.naver.maps.Size(20, 20),
            anchor: new window.naver.maps.Point(10, 10),
          },
          title: i18next.t('map.myLocation'),
        });
      }
    } catch (err) {
      console.error('❌ 지도 초기화 오류:', err);
      setError(i18next.t('map.initFailed', { message: err.message }));
    }
  }, [isLoaded, userLocation]);

  // 지원 기관 마커 업데이트
  useEffect(() => {
    if (!mapInstance.current || !centers || centers.length === 0) return;

    // 기존 마커 제거
    markers.current.forEach((marker) => marker.setMap(null));
    markers.current = [];

    // 새 마커 추가
    centers.forEach((center) => {
      const marker = new window.naver.maps.Marker({
        position: new window.naver.maps.LatLng(
          center.location.latitude,
          center.location.longitude
        ),
        map: mapInstance.current,
        icon: getMarkerIcon(center.type),
        title: center.name,
      });

      // 마커 클릭 이벤트
      window.naver.maps.Event.addListener(marker, 'click', () => {
        onCenterClick?.(center);
        // 지도 중심 이동
        mapInstance.current.setCenter(
          new window.naver.maps.LatLng(center.location.latitude, center.location.longitude)
        );
      });

      markers.current.push(marker);
    });

    // 모든 마커가 보이도록 지도 범위 조정
    if (centers.length > 0) {
      const bounds = new window.naver.maps.LatLngBounds();
      centers.forEach((center) => {
        bounds.extend(
          new window.naver.maps.LatLng(center.location.latitude, center.location.longitude)
        );
      });
      // 사용자 위치도 포함
      if (userLocation) {
        bounds.extend(
          new window.naver.maps.LatLng(userLocation.latitude, userLocation.longitude)
        );
      }
      mapInstance.current.fitBounds(bounds, { top: 50, right: 50, bottom: 50, left: 50 });
    }
  }, [centers, onCenterClick, userLocation]);

  // 현재 위치로 이동
  const moveToCurrentLocation = () => {
    // HTTP 환경 체크
    const isSecureContext = window.isSecureContext;

    if (!isSecureContext && window.location.protocol === 'http:') {
      alertDialog({
        title: t('map.httpTitle'),
        message: t('map.httpMessage'),
      });
      return;
    }

    if (!('geolocation' in navigator)) {
      toast.error(t('map.noGeolocation'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        if (mapInstance.current) {
          mapInstance.current.setCenter(new window.naver.maps.LatLng(lat, lng));
          mapInstance.current.setZoom(14);
        }
      },
      (err) => {
        let message = '';

        switch (err.code) {
          case 1: // PERMISSION_DENIED
            message = t('map.permissionDenied');
            break;
          case 2: // POSITION_UNAVAILABLE
            message = t('map.positionUnavailable');
            break;
          case 3: // TIMEOUT
            message = t('map.timeout');
            break;
          default:
            message = t('map.errorCode', { code: err.code });
        }

        alertDialog({ title: t('map.locationErrorTitle'), message });
        console.error('Geolocation error:', err);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 5000 }
    );
  };

  if (error) {
    return (
      <div className="bg-surface-muted rounded-card aspect-video flex items-center justify-center">
        <div className="text-center">
          <MapPin className="w-12 h-12 text-ink-subtle mx-auto mb-2" />
          <p className="text-sm text-ink-muted">{error}</p>
        </div>
      </div>
    );
  }

  if (!isLoaded) {
    return (
      <div className="bg-line rounded-card aspect-video flex items-center justify-center">
        <div className="text-center">
          <MapPin className="w-12 h-12 text-ink-subtle mx-auto mb-2 animate-pulse" />
          <p className="text-sm text-ink-muted">{t('map.loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* 지도 컨테이너 (PC 에서는 목록 옆에 붙어 있도록 더 높게) */}
      <div
        ref={mapElement}
        className="bg-line rounded-card w-full h-[400px] lg:h-[560px]"
      />

      {/* 현재 위치 버튼 */}
      <button
        onClick={moveToCurrentLocation}
        className="absolute bottom-4 right-4 bg-surface rounded-full p-3 shadow-lg hover:shadow-xl transition-shadow"
        title={t('map.moveToMyLocation')}
        aria-label={t('map.moveToMyLocation')}
      >
        <Navigation className="w-5 h-5 text-primary-600 dark:text-primary-400" />
      </button>

      {/* 범례 */}
      <div className="absolute top-4 left-4 bg-surface rounded-2xl p-3 shadow-lg text-xs">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-3 h-3 rounded-full bg-[#1E40AF]"></div>
          <span>{t('support.legend.labor_office')}</span>
        </div>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-3 h-3 rounded-full bg-[#059669]"></div>
          <span>{t('support.legend.legal_aid')}</span>
        </div>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-3 h-3 rounded-full bg-[#DC2626]"></div>
          <span>{t('support.legend.foreign_support')}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-[#7C3AED]"></div>
          <span>{t('support.legend.welfare')}</span>
        </div>
      </div>
    </div>
  );
}
