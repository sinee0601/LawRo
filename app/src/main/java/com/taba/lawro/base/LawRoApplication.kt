package com.taba.lawro.base

import android.app.Application
import com.naver.maps.map.NaverMapSdk
import com.taba.lawro.selectLanguage.LanguageManager

class LawRoApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // 저장된 언어 설정 적용
        val savedLanguage = LanguageManager.getLanguage(this)
        LanguageManager.setLanguage(this, savedLanguage)

        NaverMapSdk.getInstance(this).client =
            NaverMapSdk.NcpKeyClient("7i5sl0t675")
    }

}