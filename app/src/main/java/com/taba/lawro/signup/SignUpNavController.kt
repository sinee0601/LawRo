package com.taba.lawro.signup

import android.widget.Toast
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.taba.lawro.R
import com.taba.lawro.components.SuccessScreen
import com.taba.lawro.components.showAlertDialog
import com.taba.lawro.data_class.SignUpRequest
import com.taba.lawro.network.RetrofitClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

@Composable
fun SignUpNavController() {
    val navController = rememberNavController()
    val context = LocalContext.current

    NavHost(navController = navController, startDestination = "sign_up_screen") {
        composable("sign_up_screen") {
            SignUpScreen(
                navController = navController,
                onSignUpClick = { email, password, name, callback ->
                    doSignUp(email, password, name) { success, message ->
                        callback(success, message)
                    }
                }
            )
        }
        composable("success_screen") {
            SuccessScreen(stringResource(R.string.signup_complete),(stringResource(R.string.please_login)))
        }
    }
}

fun doSignUp(email: String, password: String, name: String, onResult: (Boolean, String) -> Unit) {
    CoroutineScope(Dispatchers.IO).launch {
        try {
            val request = SignUpRequest(email, password, name)
            val response = RetrofitClient.apiService.signup(request)

            withContext(Dispatchers.Main) {
                if (response.isSuccessful && response.body()?.success == true) {
                    val msg = response.body()?.message ?: "회원가입 성공"
                    onResult(true, msg)
                } else {
                    // 서버에서 보낸 실제 에러 메시지 사용
                    val errorMessage = response.body()?.message ?: "회원가입 실패: ${response.message()}"
                    onResult(false, errorMessage)
                }
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                onResult(false, "네트워크 오류: ${e.message}")
            }
        }
    }
}