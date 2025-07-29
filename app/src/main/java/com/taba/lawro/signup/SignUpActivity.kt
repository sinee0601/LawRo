package com.taba.lawro.signup

import android.os.Bundle
import androidx.activity.compose.setContent
import com.taba.lawro.base.BaseActivity
import com.taba.lawro.ui.theme.LawRoTheme

class SignUpActivity : BaseActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        setContent {
            LawRoTheme {
                SignUpNavController()
            }
        }
    }
}
