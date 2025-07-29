package com.taba.lawro.login

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import com.taba.lawro.MainActivity
import com.taba.lawro.base.BaseActivity
import com.taba.lawro.data_class.LoginRequest
import com.taba.lawro.findPassword.FindPasswordActivity
import com.taba.lawro.network.RetrofitClient
import com.taba.lawro.selectLanguage.LanguageManager
import com.taba.lawro.signup.SignUpActivity
import com.taba.lawro.ui.theme.LawRoTheme
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class LoginActivity : BaseActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // 현재 저장된 언어 설정을 적용
        val currentLanguage = LanguageManager.getLanguage(this)
        LanguageManager.setLanguage(this, currentLanguage)
        
        setContent {
            LawRoTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = Color.White
                ) {
                LoginScreen(
                    onLoginClick = { email, password, onResult ->
                        doLogin(
                            email = email,
                            password = password,
                            onSuccess = { uid, token ->
                                Log.d("Login", "성공: $uid, $token")
                                saveLoginInfo(uid, token)
                                onResult(true)
                                startActivity(Intent(this, MainActivity::class.java))
                                finish()
                            },
                            onFailure = { errorMsg ->
                                Log.d("Login", "실패: $errorMsg")
                                onResult(false) // 실패 시 LoginScreen 내부 상태 변경 유도
                            }
                        )
                    },
                    onSignUpClick = {
                        startActivity(Intent(this, SignUpActivity::class.java))
                    },
                    onForgotPasswordClick = {
                        startActivity(Intent(this, FindPasswordActivity::class.java))
                    }
                )
                }
            }
        }
    }

    override fun onResume() {
        super.onResume()
        // 화면이 다시 보일 때마다 언어 설정 확인
        val currentLanguage = LanguageManager.getLanguage(this)
        LanguageManager.setLanguage(this, currentLanguage)
    }
    //로그인
    fun doLogin(email: String, password: String, onSuccess: (uid: String, token: String) -> Unit, onFailure: (String) -> Unit) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val response = RetrofitClient.apiService.login(LoginRequest(email, password))
                withContext(Dispatchers.Main) {
                    if (response.isSuccessful && response.body() != null) {
                        val body = response.body()!!
                        Log.d("Login", "응답 본문: $body")
                        
                        // user_info가 null인지 확인
                        if (body.user_info != null && 
                            !body.user_info.user_id.isNullOrEmpty() && 
                            body.access_token.isNotEmpty()) {
                            onSuccess(body.user_info.user_id!!, body.access_token)
                        } else {
                            Log.e("Login", "user_info가 null이거나 필수 필드가 비어있음: user_info=${body.user_info}, token=${body.access_token}")
                            onFailure("로그인 응답 데이터가 올바르지 않습니다.")
                        }
                    } else {
                        Log.e("Login", "로그인 실패 - 코드: ${response.code()}, 메시지: ${response.message()}")
                        onFailure("로그인 실패: ${response.message()}")
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    onFailure("네트워크 오류: ${e.message}")
                }
            }
        }
    }

    //UID, 토큰 저장
    private fun saveLoginInfo(uid: String, token: String) {
        val sharedPref = getSharedPreferences("login_pref", MODE_PRIVATE)
        sharedPref.edit().apply {
            putString("uid", uid)
            putString("token", token)
            apply()
        }
    }
}