package com.taba.lawro.selectLanguage

import android.content.Intent
import android.os.Bundle
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.taba.lawro.base.BaseActivity
import com.taba.lawro.login.LoginActivity
import com.taba.lawro.ui.theme.LawRoTheme

class SelectLanguageActivity : BaseActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        setContent {
            LawRoTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    SelectLanguageScreen(
                        onLanguageSelected = { language ->
                            // 선택된 언어 설정 저장
                            LanguageManager.setLanguage(this, language)
                            
                            // LoginActivity로 이동하고 앱 재시작
                            val loginIntent = Intent(this, LoginActivity::class.java)
                            loginIntent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_NEW_TASK)
                            startActivity(loginIntent)
                            finishAffinity() // 모든 액티비티 종료
                        }
                    )
                }
            }
        }
    }

    override fun onResume() {
        super.onResume()
        // 현재 저장된 언어 설정을 적용
        val currentLanguage = LanguageManager.getLanguage(this)
        LanguageManager.setLanguage(this, currentLanguage)
    }
}