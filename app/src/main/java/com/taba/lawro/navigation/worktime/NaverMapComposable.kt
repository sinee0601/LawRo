package com.taba.lawro.navigation.worktime

import android.annotation.SuppressLint
import android.content.Context
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import com.naver.maps.map.MapView
import com.naver.maps.map.CameraUpdate
import com.naver.maps.geometry.LatLng
import com.naver.maps.map.overlay.Marker
import com.naver.maps.map.overlay.OverlayImage
import android.location.Location


@SuppressLint("MissingPermission")
@Composable
fun NaverMapComposable(
    context: Context,
    latitude: Double = 37.5665,
    longitude: Double = 126.9780,
    zoom: Double = 15.0,
    marker: LatLng? = null,
    currentLocation: Location? = null,
    onMapReady: ((com.naver.maps.map.NaverMap) -> Unit)? = null
) {
    val mapView = remember { MapView(context) }
    val workplaceMarker = remember { mutableStateOf<Marker?>(null) }
    val currentLocationMarker = remember { mutableStateOf<Marker?>(null) }
    var naverMapInstance by remember { mutableStateOf<com.naver.maps.map.NaverMap?>(null) }

    DisposableEffect(Unit) {
        mapView.onCreate(null)
        mapView.onStart()
        mapView.onResume()
        onDispose {
            mapView.onPause()
            mapView.onStop()
            mapView.onDestroy()
        }
    }

    AndroidView(
        factory = { mapView },
        modifier = Modifier
            .fillMaxSize()
            .offset(y = 40.dp)
    ) {
        mapView.getMapAsync { naverMap ->
            naverMapInstance = naverMap // 인스턴스 저장 (중요)
            
            // 초기 카메라 위치 설정
            val initialPosition = marker ?: LatLng(latitude, longitude)
            naverMap.moveCamera(CameraUpdate.scrollTo(initialPosition))
            naverMap.moveCamera(CameraUpdate.zoomTo(zoom))
            
            onMapReady?.invoke(naverMap)
        }
    }

    // 📌 근무지 마커 처리
    LaunchedEffect(marker, naverMapInstance) {
        val map = naverMapInstance
        if (map != null) {
            workplaceMarker.value?.map = null // 기존 마커 제거

            if (marker != null) {
                val newMarker = Marker().apply {
                    position = marker
                    icon = OverlayImage.fromResource(android.R.drawable.ic_dialog_map) // 근무지 마커 아이콘
                    captionText = "근무지"
                    this.map = map
                }
                workplaceMarker.value = newMarker

                // 카메라 이동 - 확실하게 등록된 근무지로 이동
                map.moveCamera(CameraUpdate.scrollTo(marker))
                map.moveCamera(CameraUpdate.zoomTo(zoom))
            } else {
                workplaceMarker.value = null
            }
        }
    }
    
    // 📌 현재 위치 마커 처리
    LaunchedEffect(currentLocation) {
        val map = naverMapInstance
        if (map != null && currentLocation != null) {
            currentLocationMarker.value?.map = null // 기존 마커 제거
            
            val currentLatLng = LatLng(currentLocation.latitude, currentLocation.longitude)
            val newLocationMarker = Marker().apply {
                position = currentLatLng
                icon = OverlayImage.fromResource(android.R.drawable.ic_menu_mylocation) // 현재 위치 마커 아이콘
                captionText = "내 위치"
                this.map = map
            }
            currentLocationMarker.value = newLocationMarker
        } else if (map != null && currentLocation == null) {
            currentLocationMarker.value?.map = null
            currentLocationMarker.value = null
        }
    }
}