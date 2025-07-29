package com.taba.lawro.navigation.settings.itemscreens

import android.content.Context
import android.content.Intent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.taba.lawro.R
import com.taba.lawro.components.SuccessScreen
import com.taba.lawro.login.LoginActivity
import com.taba.lawro.selectLanguage.Language
import com.taba.lawro.selectLanguage.LanguageManager

@Composable
fun ChangeLanguageScreen(
    navController: NavController,
    showSuccessScreen: Boolean = false
) {
    val context = LocalContext.current
    
    if (showSuccessScreen) {
        SuccessScreen(
            mainString = stringResource(R.string.language_change_complete),
            subString = stringResource(R.string.please_login_again)
        )
        
        // 3초 후 로그인 화면으로 자동 이동
        LaunchedEffect(Unit) {
            kotlinx.coroutines.delay(3000)
            doLogout(context)
            val loginIntent = Intent(context, LoginActivity::class.java)
            loginIntent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(loginIntent)
            (context as? android.app.Activity)?.finishAffinity()
        }
    } else {
        var selectedLanguage by remember { mutableStateOf<Language?>(null) }
        
        val languages = listOf(
            Language("en", stringResource(R.string.english_korean), stringResource(R.string.english_korean)),
            Language("ja", stringResource(R.string.japanese_korean), stringResource(R.string.japanese_korean)),
            Language("zh", stringResource(R.string.chinese_korean), stringResource(R.string.chinese_korean)),
            Language("vi", stringResource(R.string.vietnamese_korean), stringResource(R.string.vietnamese_korean)),
            Language("th", stringResource(R.string.thai_korean), stringResource(R.string.thai_korean)),
            Language("ko", stringResource(R.string.korean_korean), stringResource(R.string.korean_korean))
        )

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

            // 언어 목록
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                languages.forEachIndexed { index, language ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { selectedLanguage = language },
                        colors = CardDefaults.cardColors(
                            containerColor = if (selectedLanguage == language) 
                                Color(0xFFE8F1FF) else Color.White
                        ),
                        shape = RoundedCornerShape(8.dp),
                        elevation = CardDefaults.cardElevation(
                            defaultElevation = 2.dp
                        )
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 12.dp, horizontal = 16.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            // 각 언어별 국기 아이콘 표시
                            val flagResource = when (language.code) {
                                "en" -> R.drawable.ic_us
                                "ja" -> R.drawable.ic_jp
                                "zh" -> R.drawable.ic_ch
                                "vi" -> R.drawable.ic_vi
                                "th" -> R.drawable.ic_th
                                "ko" -> R.drawable.ic_ko
                                else -> null
                            }
                            
                            flagResource?.let {
                                androidx.compose.foundation.Image(
                                    painter = painterResource(id = it),
                                    contentDescription = "${language.displayName} Flag",
                                    modifier = Modifier.size(32.dp)
                                )
                                Spacer(modifier = Modifier.width(12.dp))
                            }
                            
                            Column {
                                Text(
                                    text = language.displayName,
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.Normal
                                )
                                Text(
                                    text = language.nativeName,
                                    fontSize = 14.sp,
                                    color = Color.Gray
                                )
                            }
                        }
                    }
                    
                    if (index == languages.lastIndex) {
                        Spacer(modifier = Modifier.height(16.dp))
                        HorizontalDivider(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 8.dp),
                            color = Color(0xFFE0E0E0),
                            thickness = 1.dp
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.weight(1f))
            
            Button(
                onClick = { 
                    selectedLanguage?.let { language ->
                        // 선택된 언어 설정 저장
                        LanguageManager.setLanguage(context, language.code)
                        
                        // 성공 화면으로 이동
                        navController.navigate("language_change_success")
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp)
                    .padding(bottom = 52.dp)
                    .height(48.dp),
                enabled = selectedLanguage != null,
                shape = RoundedCornerShape(12.dp)
            ) {
                Text(
                    text = stringResource(R.string.select_button),
                    fontSize = 16.sp
                )
            }
        }
    }
}

private fun doLogout(context: Context) {
    val loginPrefs = context.getSharedPreferences("login_pref", Context.MODE_PRIVATE)
    loginPrefs.edit().clear().apply()
} 