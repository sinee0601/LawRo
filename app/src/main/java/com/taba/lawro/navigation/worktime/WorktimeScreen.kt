package com.taba.lawro.navigation.worktime

import android.location.Geocoder
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.layout.positionInRoot
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.zIndex
import androidx.navigation.NavController
import com.naver.maps.geometry.LatLng
import com.naver.maps.map.overlay.Marker
import com.taba.lawro.components.showAlertDialog
import com.taba.lawro.R
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*
import android.Manifest
import android.content.pm.PackageManager
import android.location.Location
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationServices
import kotlin.math.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WorktimeScreen(
    navController: NavController? = null
) {
    val context = LocalContext.current
    val density = LocalDensity.current

    // 타이머 상태 변수들
    var elapsedTime by remember { mutableStateOf(0L) } // 경과 시간 (초)
    var isTimerRunning by remember { mutableStateOf(false) } // 타이머 실행 상태
    var startTime by remember { mutableStateOf(0L) } // 시작 시간
    var pausedTime by remember { mutableStateOf(0L) } // 일시정지된 시간
    var wasRunningBeforeLocationChange by remember { mutableStateOf(false) } // 위치 변경 전 실행 상태
    
    // 발표용: 근무 기록을 위한 변수들
    var workStartTime by remember { mutableStateOf("") } // 근무 시작 시간
    var workStartDate by remember { mutableStateOf("") } // 근무 시작 날짜
    
    // GPS 위반 추적 변수들
    var gpsViolationStartTime by remember { mutableStateOf(0L) } // GPS 위반 시작 시간
    var totalGpsViolationSeconds by remember { mutableStateOf(0L) } // 총 GPS 위반 시간 (초)
    var gpsViolationStartTimeString by remember { mutableStateOf("") } // GPS 위반 시작 시간 (문자열)
    var gpsViolationEndTimeString by remember { mutableStateOf("") } // GPS 위반 종료 시간 (문자열)
    
    // 시간을 HH:MM:SS 형태로 포맷팅하는 함수
    fun formatTime(seconds: Long): String {
        val hours = seconds / 3600
        val minutes = (seconds % 3600) / 60
        val secs = seconds % 60
        return String.format("%02d : %02d : %02d", hours, minutes, secs)
    }

    // 타이머 효과 (수정된 버전)
    LaunchedEffect(isTimerRunning) {
        if (isTimerRunning) {
            if (startTime == 0L) {
                startTime = System.currentTimeMillis()
            }
            while (isTimerRunning) {
                kotlinx.coroutines.delay(1000L)
                if (isTimerRunning) {
                    elapsedTime = pausedTime + (System.currentTimeMillis() - startTime) / 1000
                }
            }
        } else {
            // 타이머가 멈출 때 현재까지의 시간을 저장
            if (startTime != 0L) {
                pausedTime = elapsedTime
            }
        }
    }

    // 상태 변수
    var sheetY by remember { mutableStateOf(0f) }
    var showSearchCard by remember { mutableStateOf(false) }
    var searchQuery by remember { mutableStateOf("") }
    var selectedLatLng by remember { mutableStateOf<LatLng?>(null) }
    var sheetPeekHeight by remember { mutableStateOf(130.dp) }
    var isRegisteringLocation by remember { mutableStateOf(false) }
    val coroutineScope = rememberCoroutineScope()
    val scaffoldState = rememberBottomSheetScaffoldState()
    var registeredLatLng by remember { mutableStateOf<LatLng?>(null) }
    var searchedLabel by remember { mutableStateOf<String?>(null) }
    var searchedAddress by remember { mutableStateOf<String?>(null) }
    var currentAddress by remember { mutableStateOf<String?>(null) }
    var currentMarker by remember { mutableStateOf<Marker?>(null) }
    
    // 실제 GPS 위치 확인 상태
    var isAtWorkLocation by remember { mutableStateOf(true) } // 기본값: 근무지에 있음
    var currentLocation by remember { mutableStateOf<Location?>(null) }
    var hasLocationPermission by remember { mutableStateOf(false) }
    var isDemoMode by remember { mutableStateOf(false) } // 발표용 데모 모드
    
    // FusedLocationProviderClient 초기화
    val fusedLocationClient = remember { LocationServices.getFusedLocationProviderClient(context) }
    
    // 위치 권한 요청 launcher
    val locationPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        hasLocationPermission = permissions[Manifest.permission.ACCESS_FINE_LOCATION] == true ||
                               permissions[Manifest.permission.ACCESS_COARSE_LOCATION] == true
    }
    
    // 두 지점 간의 거리 계산 함수 (미터 단위)
    fun calculateDistance(lat1: Double, lon1: Double, lat2: Double, lon2: Double): Float {
        val results = FloatArray(1)
        Location.distanceBetween(lat1, lon1, lat2, lon2, results)
        return results[0]
    }
    
    // 현재 위치가 근무지 반경 내에 있는지 확인 (100미터 반경)
    fun checkIfAtWorkLocation(): Boolean {
        val current = currentLocation
        val registered = registeredLatLng
        
        return if (current != null && registered != null) {
            val distance = calculateDistance(
                current.latitude, current.longitude,
                registered.latitude, registered.longitude
            )
            distance <= 200f // 200미터 반경 내
        } else {
            true // 위치 정보가 없으면 기본적으로 허용
        }
    }
    
    // 현재 위치 업데이트 함수
    fun updateCurrentLocation() {
        if (hasLocationPermission && !isDemoMode) { // 데모 모드가 아닐 때만 실제 GPS 업데이트
            try {
                fusedLocationClient.lastLocation.addOnSuccessListener { location ->
                    currentLocation = location
                    isAtWorkLocation = checkIfAtWorkLocation()
                }
            } catch (e: SecurityException) {
                // 권한이 없는 경우
            }
        }
    }
    
    // 초기화 및 권한 확인
    LaunchedEffect(Unit) {
        // 위치 권한 확인
        hasLocationPermission = ContextCompat.checkSelfPermission(
            context, Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED || ContextCompat.checkSelfPermission(
            context, Manifest.permission.ACCESS_COARSE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
        
        // 권한이 없으면 요청
        if (!hasLocationPermission) {
            locationPermissionLauncher.launch(
                arrayOf(
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION
                )
            )
        }
        
        // 저장된 근무지 정보 불러오기
        val sharedPref = context.getSharedPreferences("workplace_info", android.content.Context.MODE_PRIVATE)
        val latitude = sharedPref.getFloat("workplace_latitude", 0f)
        val longitude = sharedPref.getFloat("workplace_longitude", 0f)
        val address = sharedPref.getString("workplace_address", null)
        val label = sharedPref.getString("workplace_label", null)
        
        if (latitude != 0f && longitude != 0f && !address.isNullOrEmpty()) {
            registeredLatLng = LatLng(latitude.toDouble(), longitude.toDouble())
            selectedLatLng = registeredLatLng
            currentAddress = address
            searchedLabel = label
            searchedAddress = address
        }
        
        // 초기 위치 업데이트
        updateCurrentLocation()
    }
    
    // 주기적으로 위치 업데이트 (5초마다)
    LaunchedEffect(hasLocationPermission, registeredLatLng) {
        if (hasLocationPermission && registeredLatLng != null) {
            while (true) {
                updateCurrentLocation()
                kotlinx.coroutines.delay(5000) // 5초 대기
            }
        }
    }

    // GPS 위치 상태 변화에 따른 타이머 자동 제어 및 GPS 위반 추적
    LaunchedEffect(isAtWorkLocation, currentAddress) {
        if (currentAddress != null) { // 근무지가 등록된 경우에만
            if (!isAtWorkLocation) {
                // 근무지를 벗어나면 타이머 일시정지 및 GPS 위반 시작
                if (isTimerRunning) {
                    wasRunningBeforeLocationChange = true
                    isTimerRunning = false
                    gpsViolationStartTime = System.currentTimeMillis() // GPS 위반 시작 시간 기록
                    
                    // GPS 위반 시작 시간을 문자열로 기록
                    val violationStartCal = Calendar.getInstance(java.util.TimeZone.getTimeZone("Asia/Seoul"))
                    val violationTimeFormat = SimpleDateFormat("HH:mm", Locale.KOREA).apply {
                        timeZone = java.util.TimeZone.getTimeZone("Asia/Seoul")
                    }
                    gpsViolationStartTimeString = violationTimeFormat.format(violationStartCal.time)
                }
            } else {
                // 근무지로 돌아오면 이전에 실행 중이었다면 타이머 재개 및 GPS 위반 시간 누적
                if (wasRunningBeforeLocationChange && !isTimerRunning) {
                    // GPS 위반 시간 계산 및 누적
                    if (gpsViolationStartTime > 0) {
                        val violationDuration = (System.currentTimeMillis() - gpsViolationStartTime) / 1000
                        totalGpsViolationSeconds += violationDuration
                        
                        // GPS 위반 종료 시간을 문자열로 기록
                        val violationEndCal = Calendar.getInstance(java.util.TimeZone.getTimeZone("Asia/Seoul"))
                        val violationTimeFormat = SimpleDateFormat("HH:mm", Locale.KOREA).apply {
                            timeZone = java.util.TimeZone.getTimeZone("Asia/Seoul")
                        }
                        gpsViolationEndTimeString = violationTimeFormat.format(violationEndCal.time)
                        
                        gpsViolationStartTime = 0L // GPS 위반 추적 종료
                    }
                    startTime = System.currentTimeMillis()
                    isTimerRunning = true
                    wasRunningBeforeLocationChange = false
                }
            }
        }
    }

    val cardOffsetDp by remember {
        derivedStateOf {
            with(density) { (sheetY - 540).toDp() }
        }
    }
    val animatedOffset by animateDpAsState(
        targetValue = cardOffsetDp,
        label = "AnimatedCardOffset"
    )
    
    Column(modifier = Modifier.fillMaxSize().background(Color.White)) {
        // 근무 시간 측정 텍스트 (별도 영역)
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 50.dp,),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = context.getString(R.string.worktime_measurement),
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold
            )
        }
        
        // 지도와 다른 요소들
        Box(modifier = Modifier.fillMaxSize()) {
            val markerToShow = selectedLatLng ?: registeredLatLng

            NaverMapComposable(
                context = context,
                latitude = markerToShow?.latitude ?: 37.5665,
                longitude = markerToShow?.longitude ?: 126.9780,
                marker = markerToShow,
                currentLocation = currentLocation,
                onMapReady = { naverMap ->
                    val location = markerToShow
                    if (location != null) {
                        currentMarker?.map = null

                        val newMarker = Marker().apply {
                            position = location
                            map = naverMap
                        }
                        currentMarker = newMarker
                        
                        // 등록된 근무지로 카메라 이동
                        naverMap.moveCamera(com.naver.maps.map.CameraUpdate.scrollTo(location))
                        naverMap.moveCamera(com.naver.maps.map.CameraUpdate.zoomTo(15.0))
                    }
                }
            )

        // 검색창 카드 (지도 위)
        if (showSearchCard) {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp)
                    .offset(y = 50.dp)
                    .align(Alignment.TopCenter)
                    .zIndex(2f),
                elevation = CardDefaults.cardElevation(defaultElevation = 5.dp),
                shape = RoundedCornerShape(2.dp),
                colors = CardDefaults.cardColors(containerColor = Color.Transparent)
            ) {
                TextField(
                    value = searchQuery,
                    onValueChange = { searchQuery = it },
                    placeholder = {
                        Row(modifier = Modifier.padding(start = 0.dp)) {
                            Text(context.getString(R.string.company_name_hint), textAlign = TextAlign.Start)
                        }
                    },
                    singleLine = true,
                    textStyle = TextStyle(textAlign = TextAlign.Start),
                    shape = RoundedCornerShape(50.dp),
                    trailingIcon = {
                        IconButton(onClick = {
                            coroutineScope.launch {
                                val geocoder = Geocoder(context)
                                val result = withContext(Dispatchers.IO) {
                                    geocoder.getFromLocationName(searchQuery, 1)
                                }

                                if (!result.isNullOrEmpty()) {
                                    val loc = result[0]
                                    selectedLatLng = LatLng(loc.latitude, loc.longitude)

                                    searchedLabel = searchQuery
                                    searchedAddress = loc.getAddressLine(0)
                                    isRegisteringLocation = true
                                    showSearchCard = false
                                    sheetPeekHeight = 240.dp
                                } else {
                                    showAlertDialog(
                                        title = context.getString(R.string.search_failed),
                                        message = context.getString(R.string.location_not_found),
                                        context = context
                                    )
                                }
                            }
                        }) {
                            Icon(Icons.Default.Search, contentDescription = context.getString(R.string.search_failed), tint = Color(0xFF2196F3))
                        }
                    },
                    colors = TextFieldDefaults.colors(
                        focusedContainerColor = Color.White,
                        unfocusedContainerColor = Color.White,
                        disabledIndicatorColor = Color.Transparent,
                        focusedIndicatorColor = Color.Transparent,
                        unfocusedIndicatorColor = Color.Transparent
                    ),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(60.dp)
                )
            }
        }
        // 위치 정보 카드 (기존 상단)
        if (!isRegisteringLocation) {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp)
                    .offset { IntOffset(x = 0, y = animatedOffset.roundToPx()) }
                    .align(Alignment.TopCenter)
                    .zIndex(1f),
                elevation = CardDefaults.cardElevation(defaultElevation = 10.dp),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = Color.White)
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(24.dp),
                    contentAlignment = Alignment.Center
                ) {
                    val locationText = "${context.getString(R.string.work_location)} : ${currentAddress ?: context.getString(R.string.not_registered)}"
                    Text(
                        text = locationText,
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
        }

        // 바텀시트 (측정 버튼 포함)
        BottomSheetScaffold(
            scaffoldState = scaffoldState,
            sheetPeekHeight = sheetPeekHeight,
            sheetContainerColor = Color.White,
            sheetContent = {
                if (isRegisteringLocation) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("${context.getString(R.string.workplace)} : ${searchedLabel ?: ""}", fontSize = 15.sp)
                        Text("${context.getString(R.string.road_name)} : ${searchedAddress ?: ""}", fontSize = 15.sp)
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            context.getString(R.string.register_workplace_question),
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Bold,
                            textAlign = TextAlign.Center,
                            modifier = Modifier.fillMaxWidth()
                        )

                        Spacer(modifier = Modifier.height(16.dp))
                        Box(
                            modifier = Modifier.fillMaxWidth(),
                            contentAlignment = Alignment.Center
                        ) {
                            Row(
                                horizontalArrangement = Arrangement.spacedBy(16.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Button(
                                    onClick = {
                                        if (searchedAddress.isNullOrBlank()) {
                                            showAlertDialog(
                                                title = context.getString(R.string.work_location_not_found),
                                                message = context.getString(R.string.search_location_first),
                                                context = context
                                            )
                                        } else {
                                            registeredLatLng = selectedLatLng
                                            isRegisteringLocation = false
                                            sheetPeekHeight = 130.dp
                                            currentAddress = searchedAddress
                                            
                                            // SharedPreferences에 근무지 정보 저장
                                            val sharedPref = context.getSharedPreferences("workplace_info", android.content.Context.MODE_PRIVATE)
                                            val editor = sharedPref.edit()
                                            selectedLatLng?.let { latLng ->
                                                editor.putFloat("workplace_latitude", latLng.latitude.toFloat())
                                                editor.putFloat("workplace_longitude", latLng.longitude.toFloat())
                                                editor.putString("workplace_address", searchedAddress)
                                                editor.putString("workplace_label", searchedLabel)
                                                editor.apply()
                                            }
                                        }
                                    }
                                ) {
                                    Text(context.getString(R.string.register))
                                }

                                Button(
                                    onClick = {
                                        if (registeredLatLng == null) {
                                            selectedLatLng = null
                                            searchedLabel = null
                                            searchedAddress = null
                                            currentMarker?.map = null // 지도에서 마커 제거
                                            currentMarker = null

                                            isRegisteringLocation = false
                                            showSearchCard = false
                                            sheetPeekHeight = 130.dp
                                            coroutineScope.launch {
                                                scaffoldState.bottomSheetState.partialExpand()
                                            }
                                        } else {
                                            selectedLatLng = registeredLatLng
                                            searchedLabel = null
                                            searchedAddress = null
                                            isRegisteringLocation = false
                                            showSearchCard = false
                                            sheetPeekHeight = 130.dp
                                        }
                                    },
                                    colors = ButtonDefaults.buttonColors(
                                        containerColor = MaterialTheme.colorScheme.primaryContainer,
                                        contentColor = MaterialTheme.colorScheme.onPrimaryContainer
                                    )
                                ) {
                                    Text(context.getString(R.string.cancel))
                                }
                            }
                        }
                    }
                } else {
                    // 기본 측정 화면
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .onGloballyPositioned { coordinates ->
                                sheetY = coordinates.positionInRoot().y
                            }
                            .padding(14.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        val registerButtonText = if (currentAddress.isNullOrEmpty()) context.getString(R.string.register_work_location) else context.getString(R.string.change_work_location)
                        Button(
                            onClick = {
                                searchQuery = ""
                                showSearchCard = true
                                sheetPeekHeight = 50.dp
                                isRegisteringLocation = true
                                coroutineScope.launch {
                                    scaffoldState.bottomSheetState.partialExpand()
                                }
                            },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(registerButtonText)
                        }
                        Spacer(modifier = Modifier.height(24.dp))
                        Text(context.getString(R.string.worktime_measurement), fontSize = 18.sp)
                        Text(formatTime(elapsedTime), fontSize = 36.sp)
                        
                        // GPS 위치 상태 표시
                        Spacer(modifier = Modifier.height(8.dp))
                        if (currentAddress != null) {
                            Card(
                                modifier = Modifier.padding(horizontal = 16.dp),
                                colors = CardDefaults.cardColors(
                                    containerColor = if (isAtWorkLocation) Color(0xFFE8F5E8) else Color(0xFFFFEBEE)
                                )
                            ) {
                                Column(
                                    modifier = Modifier.padding(8.dp),
                                    horizontalAlignment = Alignment.CenterHorizontally
                                ) {
                                    Text(
                                        text = if (isAtWorkLocation) context.getString(R.string.working_at_location) else context.getString(R.string.working_outside_location),
                                        fontSize = 12.sp,
                                        color = if (isAtWorkLocation) Color(0xFF4CAF50) else Color(0xFFE53935)
                                    )
                                    if (!isAtWorkLocation && wasRunningBeforeLocationChange) {
                                        Text(
                                            text = "⏸️일시정지",
                                            fontSize = 10.sp,
                                            color = Color(0xFFE53935),
                                            modifier = Modifier.padding(top = 2.dp)
                                        )
                                    }
                                    
                                    // 거리 정보 표시 (디버깅용)
                                    currentLocation?.let { current ->
                                        registeredLatLng?.let { registered ->
                                            val distance = calculateDistance(
                                                current.latitude, current.longitude,
                                                registered.latitude, registered.longitude
                                            )
                                            Text(
                                                text = "거리: ${String.format("%.0f", distance)}m",
                                                fontSize = 10.sp,
                                                color = Color.Gray,
                                                modifier = Modifier.padding(top = 2.dp)
                                            )
                                        }
                                    }
                                }
                            }
                        }
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(16.dp),
                            modifier = Modifier.padding(horizontal = 32.dp)
                        ) {
                            Button(
                                onClick = {
                                    if (currentAddress == null || isAtWorkLocation) {
                                        startTime = System.currentTimeMillis()
                                        isTimerRunning = true
                                        
                                        // 발표용: 근무 시작 시간 기록 (한국시간)
                                        val currentTime = Calendar.getInstance(java.util.TimeZone.getTimeZone("Asia/Seoul"))
                                        val dateFormat = SimpleDateFormat("yyyy.MM.dd", Locale.KOREA).apply {
                                            timeZone = java.util.TimeZone.getTimeZone("Asia/Seoul")
                                        }
                                        val timeFormat = SimpleDateFormat("HH:mm", Locale.KOREA).apply {
                                            timeZone = java.util.TimeZone.getTimeZone("Asia/Seoul")
                                        }
                                        workStartDate = dateFormat.format(currentTime.time)
                                        workStartTime = timeFormat.format(currentTime.time)
                                    } else {
                                        showAlertDialog(
                                            title = context.getString(R.string.start_not_allowed_title),
                                            message = context.getString(R.string.start_not_allowed_message),
                                            context = context
                                        )
                                    }
                                },
                                enabled = currentAddress == null || isAtWorkLocation, // 근무지 등록되지 않았거나 근무지에 있을 때만 활성화
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = if (currentAddress == null || isAtWorkLocation) 
                                        MaterialTheme.colorScheme.primary 
                                    else Color.Gray,
                                    contentColor = if (currentAddress == null || isAtWorkLocation)
                                        Color.White
                                    else Color.White
                                )
                            ) { 
                                Text(context.getString(R.string.start_measurement)) 
                            }
                            Button(
                                onClick = {
                                    if (currentAddress == null || isAtWorkLocation) {
                                        isTimerRunning = false
                                        
                                        // 발표용: 근무 기록 저장 및 화면 이동
                                        if (elapsedTime > 0) {
                                            val currentTime = Calendar.getInstance(java.util.TimeZone.getTimeZone("Asia/Seoul"))
                                            val endTimeFormat = SimpleDateFormat("HH:mm", Locale.KOREA).apply {
                                                timeZone = java.util.TimeZone.getTimeZone("Asia/Seoul")
                                            }
                                            val workEndTime = endTimeFormat.format(currentTime.time)
                                            
                                            // SharedPreferences에 기록 저장 (발표용 하드코딩)
                                            val sharedPref = context.getSharedPreferences("worktime_records", android.content.Context.MODE_PRIVATE)
                                            val editor = sharedPref.edit()
                                            
                                            // 기존 기록 개수 확인
                                            val recordCount = sharedPref.getInt("record_count", 0)
                                            val newRecordId = "record_${recordCount + 1}"
                                            
                                            // 새 기록 저장
                                            editor.putString("${newRecordId}_date", workStartDate)
                                            editor.putString("${newRecordId}_start_time", workStartTime)
                                            editor.putString("${newRecordId}_end_time", workEndTime)
                                            editor.putLong("${newRecordId}_total_seconds", elapsedTime)
                                            editor.putString("${newRecordId}_work_location", currentAddress ?: "미등록")
                                            editor.putLong("${newRecordId}_gps_violation_seconds", totalGpsViolationSeconds)
                                            editor.putString("${newRecordId}_gps_violation_start_time", gpsViolationStartTimeString)
                                            editor.putString("${newRecordId}_gps_violation_end_time", gpsViolationEndTimeString)
                                            editor.putBoolean("${newRecordId}_is_completed", true)
                                            editor.putInt("record_count", recordCount + 1)
                                            editor.apply()
                                            
                                            // 타이머 리셋
                                            elapsedTime = 0L
                                            pausedTime = 0L
                                            startTime = 0L
                                            workStartTime = ""
                                            workStartDate = ""
                                            totalGpsViolationSeconds = 0L
                                            gpsViolationStartTime = 0L
                                            gpsViolationStartTimeString = ""
                                            gpsViolationEndTimeString = ""
                                            
                                            // 근무시간 기록 화면으로 이동
                                            navController?.navigate("worktime_records/worktime")
                                        }
                                    } else {
                                        showAlertDialog(
                                            title = context.getString(R.string.stop_not_allowed_title),
                                            message = context.getString(R.string.stop_not_allowed_message),
                                            context = context
                                        )
                                    }
                                },
                                enabled = currentAddress == null || isAtWorkLocation, // 근무지 등록되지 않았거나 근무지에 있을 때만 활성화
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = if (currentAddress == null || isAtWorkLocation) 
                                        MaterialTheme.colorScheme.primaryContainer 
                                    else Color.Gray,
                                    contentColor = if (currentAddress == null || isAtWorkLocation)
                                        MaterialTheme.colorScheme.onPrimaryContainer
                                    else Color.White
                                )
                            ) { Text(context.getString(R.string.stop_measurement)) }
                        }
                        
                                // 발표용: GPS 상태 토글 버튼 (근무지가 등록된 경우에만 표시)
        if (currentAddress != null) {
            Spacer(modifier = Modifier.height(8.dp))
            Button(
                onClick = { 
                    isDemoMode = true // 데모 모드 활성화
                    isAtWorkLocation = !isAtWorkLocation 
                },
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (isDemoMode) Color(0xFFE91E63) else Color(0xFFFF9800)
                ),
                modifier = Modifier.fillMaxWidth(0.8f)
            ) {
                Text(
                    text = if (isAtWorkLocation) context.getString(R.string.simulate_leave_workplace) else context.getString(R.string.simulate_return_workplace),
                    fontSize = 12.sp
                )
            }
            
            // 데모 모드 해제 버튼
            if (isDemoMode) {
                Spacer(modifier = Modifier.height(4.dp))
                Button(
                    onClick = { 
                        isDemoMode = false 
                        updateCurrentLocation() // 실제 GPS로 복귀
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF4CAF50)
                    ),
                    modifier = Modifier.fillMaxWidth(0.6f)
                ) {
                    Text(
                        text = "실제 GPS 모드로 복귀",
                        fontSize = 10.sp
                    )
                }
            }
        }
                    }
                }
            },
            modifier = Modifier.align(Alignment.BottomCenter)
        ){}
        }
    }
}
