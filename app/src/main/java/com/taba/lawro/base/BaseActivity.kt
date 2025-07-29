package com.taba.lawro.base

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.core.view.WindowCompat
import com.taba.lawro.selectLanguage.LanguageManager

open class BaseActivity : ComponentActivity() {
    override fun attachBaseContext(newBase: Context) {
        val languageCode = LanguageManager.getLanguage(newBase)
        super.attachBaseContext(LanguageManager.updateContextLocale(newBase, languageCode))
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // 상태바를 흰색으로 설정
        window.statusBarColor = android.graphics.Color.WHITE
        WindowCompat.getInsetsController(window, window.decorView).isAppearanceLightStatusBars = true
        
        // 언어 설정을 강제로 적용하여 시스템 언어 변경에 영향받지 않도록 함
        val languageCode = LanguageManager.getLanguage(this)
        LanguageManager.setLanguage(this, languageCode)
    }

    override fun onResume() {
        super.onResume()
        // 앱이 다시 포그라운드로 올 때마다 언어 설정 확인 및 재적용
        val languageCode = LanguageManager.getLanguage(this)
        if (!LanguageManager.isLanguageSetCorrectly(this)) {
            // 언어 설정이 올바르지 않으면 강제로 재설정
            LanguageManager.setLanguage(this, languageCode)
            // 액티비티 재생성으로 언어 변경 즉시 반영
            recreate()
        }
    }
} 