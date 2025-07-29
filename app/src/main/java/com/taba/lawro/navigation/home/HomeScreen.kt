package com.taba.lawro.navigation.home

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.RoundedCornerShape

import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.taba.lawro.R
import com.taba.lawro.navigation.Screen

@Composable
fun HomeScreen(
    navController: NavController
) {
    val context = LocalContext.current
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        // 헤더 타이틀과 설정 아이콘
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 24.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // 왼쪽 빈 공간 (설정 아이콘과 균형)
            Spacer(modifier = Modifier.width(48.dp))
            
            // LawRo 로고 (중앙)
            Text(
                text = "LAWRO",
                fontSize = 32.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF005FDC)
            )
            
            // 설정 아이콘 (오른쪽)
            IconButton(
                onClick = {
                    navController.navigate(Screen.Settings.route)
                }
            ) {
                Icon(
                    painter = painterResource(id = R.drawable.ic_settings_selected),
                    contentDescription = stringResource(R.string.settings_description),
                    modifier = Modifier.size(28.dp),
                    tint = Color.Unspecified
                )
            }
        }
        
        // 환영 메시지
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .height(120.dp)
                .padding(bottom = 24.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(20.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Text(
                    text = stringResource(R.string.home_welcome_message),
                    fontSize = 18.sp,
                    fontWeight = FontWeight.SemiBold,
                    textAlign = TextAlign.Center
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = stringResource(R.string.home_welcome_subtitle),
                    fontSize = 14.sp,
                    color = Color.Gray,
                    textAlign = TextAlign.Center
                )
            }
        }
        
        // 기능 카드들
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // 계약서 분석 카드
            FeatureCard(
                modifier = Modifier.weight(1f),
                title = stringResource(R.string.home_feature_contract_analysis),
                description = stringResource(R.string.home_feature_contract_analysis_desc),
                iconRes = R.drawable.ic_analyze_selected,
                backgroundColor = Color(0xFFE3F2FD),
                iconColor = Color(0xFF1976D2)
            ) {
                navController.navigate(Screen.Analyze.route) {
                    popUpTo(Screen.Home.route) { saveState = true }
                    launchSingleTop = true
                    restoreState = true
                }
            }
            
            // 기록 확인 카드
            FeatureCard(
                modifier = Modifier.weight(1f),
                title = stringResource(R.string.home_feature_record_check),
                description = stringResource(R.string.home_feature_record_check_desc),
                iconRes = R.drawable.ic_history_selected,
                backgroundColor = Color.White,
                iconColor = Color(0xFF1976D2)
            ) {
                navController.navigate(Screen.History.route) {
                    popUpTo(Screen.Home.route) { saveState = true }
                    launchSingleTop = true
                    restoreState = true
                }
            }
        }
        
        Spacer(modifier = Modifier.height(12.dp))
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // 근무시간 측정 카드
            FeatureCard(
                modifier = Modifier.weight(1f),
                title = stringResource(R.string.home_feature_worktime),
                description = stringResource(R.string.home_feature_worktime_desc),
                iconRes = R.drawable.ic_worktime_selected,
                backgroundColor = Color.White,
                iconColor = Color(0xFF1976D2)
            ) {
                navController.navigate(Screen.Worktime.route) {
                    popUpTo(Screen.Home.route) { saveState = true }
                    launchSingleTop = true
                    restoreState = true
                }
            }
            
            // AI 챗봇 카드
            FeatureCard(
                modifier = Modifier.weight(1f),
                title = stringResource(R.string.home_feature_ai_chatbot),
                description = stringResource(R.string.home_feature_ai_chatbot_desc),
                iconRes = R.drawable.ic_chatbot_selected,
                backgroundColor = Color(0xFFE3F2FD),
                iconColor = Color(0xFF1976D2)
            ) {
                navController.navigate(Screen.Chatbot.route) {
                    popUpTo(Screen.Home.route) { saveState = true }
                    launchSingleTop = true
                    restoreState = true
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // 최근 활동 섹션 (추후 추가 가능)
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Column(
                modifier = Modifier.padding(20.dp)
            ) {
                Text(
                    text = stringResource(R.string.home_tips_title),
                    fontSize = 16.sp,
                    fontWeight = FontWeight.SemiBold,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                Text(
                    text = stringResource(R.string.home_tips_content),
                    fontSize = 13.sp,
                    color = Color(0xFF666666),
                    lineHeight = 18.sp
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FeatureCard(
    modifier: Modifier = Modifier,
    title: String,
    description: String,
    iconRes: Int,
    backgroundColor: Color,
    iconColor: Color,
    onClick: () -> Unit
) {
    Card(
        modifier = modifier.height(140.dp),
        colors = CardDefaults.cardColors(containerColor = backgroundColor),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        shape = RoundedCornerShape(16.dp),
        onClick = onClick
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                painter = painterResource(id = iconRes),
                contentDescription = title,
                modifier = Modifier.size(32.dp),
                tint = Color.Unspecified
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = title,
                fontSize = 14.sp,
                fontWeight = FontWeight.SemiBold,
                textAlign = TextAlign.Center,
                lineHeight = 16.sp
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = description,
                fontSize = 11.sp,
                color = Color(0xFF666666),
                textAlign = TextAlign.Center,
                lineHeight = 13.sp
            )
        }
    }
} 