package com.taba.lawro.splash

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.taba.lawro.ui.theme.LawRoTheme

class SplashActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            LawRoTheme {
                SplashScreen {
                    startActivity(Intent(this, com.taba.lawro.selectLanguage.SelectLanguageActivity::class.java))
                    finish()
                }
            }
        }
    }
}