package com.taba.lawro.signup

import android.app.Activity
import android.os.Handler
import android.os.Looper
import android.util.Log
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.taba.lawro.R
import com.taba.lawro.components.CustomTextField
import com.taba.lawro.components.ErrorText
import com.taba.lawro.components.showAlertDialog

@Composable
fun SignUpScreen(
    navController: NavController,
    onSignUpClick: (String, String, String, (Boolean, String) -> Unit) -> Unit)
{
    var name by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var emailDomain by remember { mutableStateOf("") }
    var verificationCode by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var confirmPassword by remember { mutableStateOf("") }
    var passwordVisible by remember { mutableStateOf(false) }
    var confirmPasswordVisible by remember { mutableStateOf(false) }

    var nameError by remember { mutableStateOf(false) }
    var emailError by remember { mutableStateOf(false) }
    var emailErrorMessage by remember { mutableStateOf("") }
    var verificationError by remember { mutableStateOf(false) }
    var passwordError by remember { mutableStateOf(false) }
    var confirmPasswordError by remember { mutableStateOf(false) }

    val context = LocalContext.current
    val activity = context as? Activity
    val scrollState = rememberScrollState()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
            .verticalScroll(scrollState)
    ) {
        // 상단 바
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 44.dp, bottom = 16.dp)
        ) {
            // 뒤로가기 버튼
            IconButton(
                onClick = { 
                    activity?.finish()
                },
                modifier = Modifier
                    .padding(start = 16.dp)
                    .size(48.dp)
                    .align(Alignment.CenterStart)
            ) {
                Icon(
                    painter = painterResource(id = R.drawable.ic_back),
                    contentDescription = "Back",
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(32.dp)
                )
            }

            // 제목
            Text(
                text = stringResource(R.string.signup_title),
                fontSize = 18.sp,
                fontWeight = FontWeight.Medium,
                modifier = Modifier.align(Alignment.Center)
            )
        }
        Spacer(modifier = Modifier.weight(0.04f))

        // 입력 필드들
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp),
        ) {
            // 이름 입력
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(min = 90.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = stringResource(R.string.name_hint),
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium
                )
                CustomTextField(
                    value = name,
                    onValueChange = {
                        name = it
                    },
                    placeholder = stringResource(R.string.name_hint),
                    isError = nameError,
                    modifier = Modifier.fillMaxWidth()
                )
                Box(modifier = Modifier.height(20.dp)) {
                    if (nameError) {
                        ErrorText(text = stringResource(R.string.name_error))
                    }
                }
            }
            // 이메일 입력
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(min = 90.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = stringResource(R.string.email),
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium
                )
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    CustomTextField(
                        value = email,
                        onValueChange = {
                            email = it
                            emailErrorMessage = ""
                        },
                        placeholder = stringResource(R.string.email),
                        isError = emailError || emailErrorMessage.isNotEmpty(),
                        modifier = Modifier.weight(1f)
                    )
                    Text(
                        text = "@",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium
                    )
                    CustomTextField(
                        value = emailDomain,
                        onValueChange = {
                            emailDomain = it
                            emailErrorMessage = ""
                        },
                        placeholder = stringResource(R.string.domain_hint),
                        isError = emailError || emailErrorMessage.isNotEmpty(),
                        modifier = Modifier.weight(1f)
                    )
                }
                Box(modifier = Modifier.height(20.dp)) {
                    if (emailError) {
                        ErrorText(text = stringResource(R.string.email_format_error))
                    } else if (emailErrorMessage.isNotEmpty()) {
                        ErrorText(text = emailErrorMessage)
                    }
                }
            }

            // 인증번호 입력
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(min = 90.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = stringResource(R.string.verification_code_hint),
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium
                )
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    CustomTextField(
                        value = verificationCode,
                        onValueChange = {
                            verificationCode = it
                        },
                        placeholder = stringResource(R.string.verification_code_6_digits),
                        isError = verificationError,
                        modifier = Modifier.weight(1f)
                    )
                    Button(
                        onClick = { /* TODO: Implement verification code sending */ },
                        modifier = Modifier
                            .width(80.dp)
                            .height(48.dp),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Text(
                            text = stringResource(R.string.send_verification_code),
                            fontSize = 14.sp
                        )
                    }
                }
                Box(modifier = Modifier.height(20.dp)) {
                    if (verificationError) {
                        ErrorText(text = stringResource(R.string.verification_code_error))
                    }
                }
            }

            // 비밀번호 입력
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(min = 90.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = stringResource(R.string.password_hint),
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium
                )
                CustomTextField(
                    value = password,
                    onValueChange = {
                        password = it
                    },
                    placeholder = stringResource(R.string.password_hint),
                    isError = passwordError,
                    visualTransformation = if (passwordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                    modifier = Modifier.fillMaxWidth(),
                    trailingIcon = {
                        IconButton(
                            onClick = { passwordVisible = !passwordVisible },
                            modifier = Modifier.size(48.dp)
                        ) {
                            Icon(
                                painter = painterResource(
                                    if (passwordVisible) R.drawable.ic_visibility_off
                                    else R.drawable.ic_visibility
                                ),
                                contentDescription = if (passwordVisible) "Hide password" else "Show password",
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(24.dp)
                            )
                        }
                    }
                )
                Box(modifier = Modifier.height(20.dp)) {
                    if (passwordError) {
                        ErrorText(text = stringResource(R.string.password_length_error))
                    }
                }
            }

            // 비밀번호 확인
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(min = 90.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = stringResource(R.string.confirm_password_hint),
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium
                )
                CustomTextField(
                    value = confirmPassword,
                    onValueChange = {
                        confirmPassword = it
                    },
                    placeholder = stringResource(R.string.confirm_password_hint),
                    isError = confirmPasswordError,
                    visualTransformation = if (confirmPasswordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                    modifier = Modifier.fillMaxWidth(),
                    trailingIcon = {
                        IconButton(
                            onClick = { confirmPasswordVisible = !confirmPasswordVisible },
                            modifier = Modifier.size(48.dp)
                        ) {
                            Icon(
                                painter = painterResource(
                                    if (confirmPasswordVisible) R.drawable.ic_visibility_off
                                    else R.drawable.ic_visibility
                                ),
                                contentDescription = if (confirmPasswordVisible) "Hide password" else "Show password",
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(24.dp)
                            )
                        }
                    }
                )
                Box(modifier = Modifier.height(20.dp)) {
                    if (confirmPasswordError) {
                        ErrorText(text = stringResource(R.string.password_mismatch_error))
                    }
                }
            }
        }

        Spacer(modifier = Modifier.weight(0.15f))

        // 회원가입 버튼
        Button(
            onClick = {
                val fullEmail = "$email@$emailDomain"

                nameError = name.isBlank()
                val isComDomain = emailDomain.endsWith(".com")
                val isAllLowerCase = emailDomain == emailDomain.lowercase()
                emailError = !(isComDomain && isAllLowerCase)
                emailErrorMessage = ""
                verificationError = verificationCode.length != 6
                passwordError = password.length < 8
                confirmPasswordError = password != confirmPassword

                if (!nameError && !emailError && !verificationError &&
                    !passwordError && !confirmPasswordError) {

                    onSignUpClick(fullEmail, password, name) { success, message ->
                        if (success) {
                            navController.navigate("success_screen")
                            Handler(Looper.getMainLooper()).postDelayed({
                                navController.popBackStack()
                                activity?.finish()
                            }, 2000)
                        } else {
                            Log.d("SIGNUP", "Received error message: '$message'")
                            // 이메일 관련 오류인지 확인 (더 포괄적으로)
                            val isEmailError = message.contains("이미 사용 중인 이메일") || 
                                             message.contains("이미 사용중인 이메일") ||
                                             message.contains("already in use") ||
                                             message.contains("already exists") ||
                                             message.contains("email") ||
                                             message.contains("이메일")
                            
                            if (isEmailError) {
                                Log.d("SIGNUP", "Setting email error message")
                                emailErrorMessage = context.getString(R.string.email_already_exists)
                            } else {
                                Log.d("SIGNUP", "Showing alert dialog")
                                showAlertDialog(
                                    context = context,
                                    title = context.getString(R.string.signup_failed),
                                    message = message
                                )
                            }
                        }
                    }
                }
                Log.d("SIGNUP", "nameError=$nameError, emailError=$emailError, verificationError=$verificationError, passwordError=$passwordError, confirmPasswordError=$confirmPasswordError")
            },
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp)
                .padding(top = 32.dp, bottom = 48.dp)
                .height(48.dp),
            shape = RoundedCornerShape(12.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = MaterialTheme.colorScheme.primary
            )
        ) {
            Text(
                text = stringResource(R.string.signup_button),
                fontSize = 16.sp,
                modifier = Modifier.padding(vertical = 4.dp)
            )
        }
    }
}
