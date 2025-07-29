package com.taba.lawro.findPassword

import android.os.Bundle
import androidx.activity.compose.setContent
import com.taba.lawro.base.BaseActivity
import com.taba.lawro.signup.SignUpNavController
import com.taba.lawro.ui.theme.LawRoTheme

class FindPasswordActivity : BaseActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            LawRoTheme {
                FindPasswordNavController()
            }
        }
    }
}
