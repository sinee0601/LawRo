package com.taba.lawro.navigation.settings.itemscreens

import android.util.Log
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.CalendarToday
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.taba.lawro.R
import com.taba.lawro.data_class.UserProfile
import com.taba.lawro.network.RetrofitClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MyInfoScreen(
    token: String = "",
    navController: NavController
) {
    var userProfile by remember { mutableStateOf<UserProfile?>(null) }
    var isLoading by remember { mutableStateOf(true) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    // 화면 진입 시 프로필 로드
    LaunchedEffect(Unit) {
        loadUserProfile(token) { profile, error ->
            userProfile = profile
            errorMessage = error
            isLoading = false
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
            .verticalScroll(rememberScrollState())
    ) {
        // 상단 바
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 0.dp, bottom = 16.dp)
        ) {
            // 뒤로가기 버튼
            IconButton(
                onClick = { navController.popBackStack() },
                modifier = Modifier
                    .padding(start = 16.dp)
                    .size(48.dp)
                    .align(Alignment.CenterStart)
            ) {
                Icon(
                    painter = painterResource(id = R.drawable.ic_back),
                    contentDescription = stringResource(R.string.back),
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(32.dp)
                )
            }
        }

        Spacer(modifier = Modifier.height(40.dp))
        // 컨텐츠 영역
        Column(
            modifier = Modifier.padding(horizontal = 16.dp)
        ) {

            when {
                isLoading -> {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            CircularProgressIndicator(color = Color(0xFF0C8FF6))
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                text = stringResource(R.string.loading_user_info),
                                color = Color(0xFF718096)
                            )
                        }
                    }
                }

                errorMessage != null -> {
                    // 에러 상태
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Card(
                            modifier = Modifier.padding(16.dp),
                            colors = CardDefaults.cardColors(containerColor = Color(0xFFFFF5F5)),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Column(
                                modifier = Modifier.padding(24.dp),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Text(
                                    text = "❌",
                                    fontSize = 48.sp,
                                    modifier = Modifier.padding(bottom = 16.dp)
                                )
                                Text(
                                    text = stringResource(R.string.cannot_load_info),
                                    fontSize = 18.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color(0xFFE53E3E),
                                    modifier = Modifier.padding(bottom = 8.dp)
                                )
                                Text(
                                    text = errorMessage ?: stringResource(R.string.unknown_error),
                                    fontSize = 14.sp,
                                    color = Color(0xFF718096),
                                    textAlign = TextAlign.Center
                                )
                            }
                        }
                    }
                }

                userProfile != null -> {
                    // 프로필 정보 표시
                    ProfileContent(userProfile!!)
                }
            }
        }
    }
}

@Composable
fun ProfileContent(profile: UserProfile) {
    Column {
        // 프로필 헤더 카드
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color.White
            ),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier.padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // 프로필 아이콘
                Box(
                    modifier = Modifier
                        .size(80.dp)
                        .clip(CircleShape)
                        .background(Color(0xFF0C8FF6)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.AccountCircle,
                        contentDescription = stringResource(R.string.profile),
                        modifier = Modifier.size(48.dp),
                        tint = Color.White
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                // 이름
                Text(
                    text = profile.fullName,
                    fontSize = 22.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF2D3748)
                )

                Spacer(modifier = Modifier.height(4.dp))

                // 사용자 ID
                Text(
                    text = "ID: ${profile.userId}",
                    fontSize = 14.sp,
                    color = Color(0xFF718096)
                )
            }
        }

        // 정보 카드들
        ProfileInfoCard(
            icon = Icons.Default.Email,
            title = stringResource(R.string.email),
            value = profile.email,
            iconColor = Color(0xFF38A169)
        )

        Spacer(modifier = Modifier.height(12.dp))

        ProfileInfoCard(
            icon = Icons.Default.Person,
            title = stringResource(R.string.user_id_label),
            value = profile.userId,
            iconColor = Color(0xFF3182CE)
        )

        Spacer(modifier = Modifier.height(12.dp))

        ProfileInfoCard(
            icon = Icons.Default.CalendarToday,
            title = stringResource(R.string.join_date),
            value = formatDate(profile.createdAt),
            iconColor = Color(0xFF805AD5)
        )
    }
}

@Composable
fun ProfileInfoCard(
    icon: ImageVector,
    title: String,
    value: String,
    iconColor: Color
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // 아이콘
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(iconColor.copy(alpha = 0.1f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = title,
                    modifier = Modifier.size(24.dp),
                    tint = iconColor
                )
            }

            Spacer(modifier = Modifier.width(16.dp))

            // 텍스트 정보
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    fontSize = 14.sp,
                    color = Color(0xFF718096),
                    fontWeight = FontWeight.Medium
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = value,
                    fontSize = 16.sp,
                    color = Color(0xFF2D3748),
                    fontWeight = FontWeight.SemiBold
                )
            }
        }
    }
}

// 프로필 로드 함수
fun loadUserProfile(
    token: String,
    onResult: (UserProfile?, String?) -> Unit
) {
    CoroutineScope(Dispatchers.IO).launch {
        try {
            val response = RetrofitClient.apiService.getProfile("Bearer $token")

            withContext(Dispatchers.Main) {
                if (response.isSuccessful) {
                    val profileResponse = response.body()
                    if (profileResponse?.success == true) {
                        Log.d("Profile", "프로필 로드 성공: ${profileResponse.user}")
                        onResult(profileResponse.user, null)
                    } else {
                        Log.e("Profile", "프로필 로드 실패: success=false")
                        onResult(null, "프로필 정보를 가져올 수 없습니다")
                    }
                } else {
                    Log.e("Profile", "프로필 로드 실패: ${response.code()} ${response.message()}")
                    onResult(null, "서버 오류가 발생했습니다 (${response.code()})")
                }
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                Log.e("Profile", "프로필 로드 예외: ${e.message}", e)
                onResult(null, "네트워크 오류가 발생했습니다")
            }
        }
    }
}

// 날짜 포맷 함수
fun formatDate(dateString: String): String {
    return try {
        val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.getDefault())
        val outputFormat = SimpleDateFormat("yyyy년 MM월 dd일", Locale.getDefault())
        val date = inputFormat.parse(dateString)
        outputFormat.format(date ?: Date())
    } catch (e: Exception) {
        dateString
    }
}


