package com.taba.lawro.selectLanguage

import android.content.Context
import android.content.SharedPreferences
import android.content.res.Configuration
import android.os.Build
import android.os.LocaleList
import java.util.*

object LanguageManager {
    private const val PREFS_NAME = "LanguagePrefs"
    private const val SELECTED_LANGUAGE = "SelectedLanguage"

    fun setLanguage(context: Context, languageCode: String) {
        saveLanguagePreference(context, languageCode)
        updateResources(context, languageCode)
    }

    fun getLanguage(context: Context): String {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        // 시스템 기본 언어 대신 영어를 기본값으로 사용하여 한국어로 바뀌는 것을 방지
        return prefs.getString(SELECTED_LANGUAGE, "en") ?: "en"
    }

    fun getLanguageNameFromCode(langCode: String?): String {
        return when (langCode) {
            "ko" -> "korean"
            "en" -> "english"
            "ja" -> "japanese"
            "zh" -> "chinese"
            "vi" -> "vietnamese"
            "th" -> "thai"
            else -> "english"
        }
    }

    private fun saveLanguagePreference(context: Context, languageCode: String) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        prefs.edit().putString(SELECTED_LANGUAGE, languageCode).apply()
    }

    fun updateContextLocale(context: Context, language: String): Context {
        val locale = Locale(language)
        Locale.setDefault(locale)

        val configuration = context.resources.configuration.apply {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                val localeList = LocaleList(locale)
                LocaleList.setDefault(localeList)
                setLocales(localeList)
            } else {
                setLocale(locale)
            }
        }

        return context.createConfigurationContext(configuration)
    }

    // 현재 설정된 언어가 올바른지 확인하는 함수
    fun isLanguageSetCorrectly(context: Context): Boolean {
        val savedLanguage = getLanguage(context)
        val currentLocale = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            context.resources.configuration.locales[0].language
        } else {
            @Suppress("DEPRECATION")
            context.resources.configuration.locale.language
        }
        return savedLanguage == currentLocale
    }

    private fun updateResources(context: Context, language: String) {
        val locale = Locale(language)
        Locale.setDefault(locale)

        val configuration = context.resources.configuration
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            val localeList = LocaleList(locale)
            LocaleList.setDefault(localeList)
            configuration.setLocales(localeList)
        } else {
            configuration.setLocale(locale)
        }

        @Suppress("DEPRECATION")
        context.resources.updateConfiguration(configuration, context.resources.displayMetrics)
        
        // 설정을 적용
        context.createConfigurationContext(configuration)
    }
} 