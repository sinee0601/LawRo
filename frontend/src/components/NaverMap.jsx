import { useEffect, useRef, useState } from 'react';
import { MapPin } from 'lucide-react';

export default function NaverMap({ latitude, longitude, onLocationChange }) {
  const mapElement = useRef(null);
  const mapInstance = useRef(null);
  const markerInstance = useRef(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState(null);

  // 네이버 지도 API 로드
  useEffect(() => {
    const loadNaverMapAPI = () => {
      const ncpKeyId = import.meta.env.VITE_NAVER_MAP_CLIENT_ID;

      if (!ncpKeyId || ncpKeyId === 'YOUR_NAVER_MAP_CLIENT_ID') {
        setError('네이버 지도 Client ID가 설정되지 않았습니다');
        return;
      }

      // 이미 로드된 경우 스킵
      if (window.naver && window.naver.maps) {
        setIsLoaded(true);
        return;
      }

      // 인증 실패 처리
      window.navermap_authFailure = function () {
        setError('네이버 지도 API 인증에 실패했습니다. Client ID를 확인하세요.');
      };

      const script = document.createElement('script');
      script.src = `https://oapi.map.naver.com/openapi/v3/maps.js?ncpKeyId=${ncpKeyId}`;
      script.async = false; // 동기 로드로 변경
      script.defer = false;
      script.type = 'text/javascript';

      script.onload = () => {
        // 약간의 지연을 주어 naver 객체가 준비되도록 함
        setTimeout(() => {
          if (window.naver && window.naver.maps) {
            console.log('✅ 네이버 지도 API 로드 완료');
            setIsLoaded(true);
            initializeMap();
          } else {
            console.error('❌ naver.maps 객체를 찾을 수 없습니다');
            setError('지도 API 초기화 실패');
          }
        }, 100);
      };

      script.onerror = (err) => {
        console.error('❌ 지도 API 로드 실패:', err);
        setError('네이버 지도 API 로드 실패');
      };

      document.head.appendChild(script);

      return () => {
        // Cleanup
        if (document.head.contains(script)) {
          try {
            document.head.removeChild(script);
          } catch (e) {
            console.warn('스크립트 제거 실패');
          }
        }
      };
    };

    loadNaverMapAPI();
  }, []);

  // 지도 초기화
  const initializeMap = () => {
    try {
      if (!mapElement.current) {
        console.error('❌ 지도 컨테이너를 찾을 수 없습니다');
        return;
      }

      console.log('📍 지도 초기화 시작...');
      console.log('mapElement.current:', mapElement.current);
      console.log('window.naver.maps:', window.naver.maps);

      const defaultLat = latitude || 37.3595704;
      const defaultLng = longitude || 127.1052062;

      const mapOptions = {
        center: new window.naver.maps.LatLng(defaultLat, defaultLng),
        zoom: 15,
        minZoom: 8,
        maxZoom: 21,
        mapTypeControl: true,
      };

      console.log('🗺️ 지도 생성 중...', mapOptions);
      mapInstance.current = new window.naver.maps.Map(mapElement.current, mapOptions);
      console.log('✅ 지도 생성 완료');

      // 마커 추가
      addMarker(defaultLat, defaultLng);

      // 지도 클릭 이벤트 리스너
      window.naver.maps.Event.addListener(mapInstance.current, 'click', (e) => {
        const lat = e.coord.lat();
        const lng = e.coord.lng();
        console.log('🖱️ 지도 클릭:', lat, lng);
        updateMarkerPosition(lat, lng);
        onLocationChange?.({ latitude: lat, longitude: lng });
      });
    } catch (err) {
      console.error('❌ 지도 초기화 오류:', err);
      setError(`지도 초기화 실패: ${err.message}`);
    }
  };

  // 마커 추가
  const addMarker = (lat, lng) => {
    if (!mapInstance.current) return;

    if (markerInstance.current) {
      markerInstance.current.setMap(null);
    }

    markerInstance.current = new window.naver.maps.Marker({
      position: new window.naver.maps.LatLng(lat, lng),
      map: mapInstance.current,
      title: '근무 위치',
    });
  };

  // 마커 위치 업데이트
  const updateMarkerPosition = (lat, lng) => {
    if (markerInstance.current && mapInstance.current) {
      markerInstance.current.setPosition(new window.naver.maps.LatLng(lat, lng));
      mapInstance.current.setCenter(new window.naver.maps.LatLng(lat, lng));
    }
  };

  // 현재 위치로 이동
  const moveToCurrentLocation = () => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          updateMarkerPosition(lat, lng);
          onLocationChange?.({ latitude: lat, longitude: lng });
        },
        (err) => {
          setError('현재 위치를 가져올 수 없습니다');
          console.error('Geolocation error:', err);
        }
      );
    } else {
      setError('이 브라우저는 위치 정보를 지원하지 않습니다');
    }
  };

  if (error) {
    return (
      <div className="bg-gray-100 rounded-3xl aspect-video mb-6 flex items-center justify-center">
        <div className="text-center">
          <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-2" />
          <p className="text-sm text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!isLoaded) {
    return (
      <div className="bg-gray-200 rounded-3xl aspect-video mb-6 flex items-center justify-center">
        <div className="text-center">
          <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-2 animate-pulse" />
          <p className="text-sm text-gray-600">지도 로드 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative mb-6">
      {/* 지도 컨테이너 */}
      <div
        ref={mapElement}
        className="bg-gray-200 rounded-3xl aspect-video w-full"
        style={{ minHeight: '300px' }}
      />

      {/* 현재 위치 버튼 */}
      <button
        onClick={moveToCurrentLocation}
        className="absolute bottom-4 right-4 bg-white rounded-full p-2 shadow-lg hover:shadow-xl transition-shadow"
        title="현재 위치로 이동"
      >
        <MapPin className="w-6 h-6 text-primary-600" />
      </button>
    </div>
  );
}
