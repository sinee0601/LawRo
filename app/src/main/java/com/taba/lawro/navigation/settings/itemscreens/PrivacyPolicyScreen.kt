package com.taba.lawro.navigation.settings.itemscreens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.taba.lawro.R

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PrivacyPolicyScreen(navController: NavController? = null) {
    val context = LocalContext.current
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                },
                navigationIcon = {
                    if (navController != null) {
                        IconButton(onClick = { navController.popBackStack() }) {
                            Icon(Icons.Default.ArrowBack, contentDescription = stringResource(R.string.back))
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color.White,
                    titleContentColor = Color.Black,
                    navigationIconContentColor = Color.Black
                )
            )
        },
        containerColor =(Color.White)
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
            contentPadding = PaddingValues(vertical = 16.dp)
        ) {
            // 마지막 업데이트 날짜
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primary),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text(
                        text = stringResource(R.string.privacy_policy_last_updated),
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        textAlign = TextAlign.Center,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium,
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                }
            }

            // 섹션 1: 개인정보의 수집 및 이용목적
            item {
                PrivacyPolicySection(
                    title = stringResource(R.string.section_1_title),
                    content = stringResource(R.string.section_1_content)
                )
            }

            // 섹션 2: 수집하는 개인정보의 항목
            item {
                PrivacyPolicySection(
                    title = stringResource(R.string.section_2_title),
                    content = stringResource(R.string.section_2_content)
                )
            }

            // 섹션 3: 개인정보의 처리 및 보유기간
            item {
                PrivacyPolicySection(
                    title = stringResource(R.string.section_3_title),
                    content = stringResource(R.string.section_3_content)
                )
            }

            // 섹션 4: 개인정보의 제3자 제공
            item {
                PrivacyPolicySection(
                    title = stringResource(R.string.section_4_title),
                    content = stringResource(R.string.section_4_content)
                )
            }

            // 섹션 5: 이용자의 권리
            item {
                PrivacyPolicySection(
                    title = stringResource(R.string.section_6_title),
                    content = stringResource(R.string.section_6_content)
                )
            }

            // 섹션 6: 개인정보보호책임자
            item {
                PrivacyPolicySection(
                    title = stringResource(R.string.section_7_title),
                    content = stringResource(R.string.section_7_content)
                )
            }

            // 섹션 7: 개인정보 처리방침의 변경
            item {
                PrivacyPolicySection(
                    title = stringResource(R.string.section_8_title),
                    content = stringResource(R.string.section_8_content)
                )
            }

            // 하단 여백
            item {
                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }
}

@Composable
private fun PrivacyPolicySection(
    title: String,
    content: String
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        shape = RoundedCornerShape(12.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = title,
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF1976D2),
                modifier = Modifier.padding(bottom = 8.dp)
            )
            Text(
                text = content,
                fontSize = 14.sp,
                lineHeight = 20.sp,
                color = Color(0xFF424242)
            )
        }
    }
}