package com.taba.lawro.login

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.font.FontWeight
import com.taba.lawro.R
import com.taba.lawro.components.ErrorText
import com.taba.lawro.components.CustomTextField

@Composable
fun LoginScreen(
    onLoginClick: (String, String, (Boolean) -> Unit) -> Unit = { _, _, _ -> },
    onSignUpClick: () -> Unit = {},
    onForgotPasswordClick: () -> Unit = {}
) {
    val context = LocalContext.current

    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var emailError by remember { mutableStateOf(false) }
    var passwordError by remember { mutableStateOf(false) }
    var isLoginAttempted by remember { mutableStateOf(false) }
    
    // 입력 필드 초기화 함수
    fun clearInputFields() {
        email = ""
        password = ""
        emailError = false
        passwordError = false
        isLoginAttempted = false
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 32.dp)
            .background(Color.White)
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Spacer(modifier = Modifier.height(60.dp))

        // 로고
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(240.dp)
        ) {
            Image(
                painter = painterResource(id = R.drawable.symbol_logo_blue),
                contentDescription = "symbol_logo_blue",
                modifier = Modifier
                    .size(180.dp)
                    .align(Alignment.TopCenter)
                    .padding(top = 20.dp)
            )
            Image(
                painter = painterResource(id = R.drawable.typo_logo_blue),
                contentDescription = "typo_logo_blue",
                modifier = Modifier
                    .size(160.dp)
                    .align(Alignment.BottomCenter)
                    .offset(y = 10.dp)
            )
        }

        // 에러 메시지
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(20.dp)
                .padding(horizontal = 4.dp)
        ) {
            if (isLoginAttempted && (emailError || passwordError)) {
                ErrorText(
                    text = when {
                        emailError && passwordError -> stringResource(id = R.string.error_invalid_email_and_password)
                        emailError -> stringResource(id = R.string.error_email_not_found)
                        else -> stringResource(id = R.string.error_password_incorrect)
                    },
                    modifier = Modifier.align(Alignment.CenterStart)
                )
            }
        }

        // 입력 필드들을 담는 Column
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            // 이메일 입력
            CustomTextField(
                value = email,
                onValueChange = {
                    email = it
                },
                placeholder = stringResource(id = R.string.email_hint),
                isError = emailError,
                modifier = Modifier.fillMaxWidth()
            )

            // 비밀번호 입력
            CustomTextField(
                value = password,
                onValueChange = {
                    password = it
                },
                placeholder = stringResource(id = R.string.password_hint),
                isError = passwordError,
                visualTransformation = PasswordVisualTransformation(),
                modifier = Modifier.fillMaxWidth()
            )

            // 비밀번호 찾기
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .offset(y = (-8).dp),
                contentAlignment = Alignment.CenterEnd
            ) {
                TextButton(
                    onClick = {
                        clearInputFields()
                        onForgotPasswordClick()
                    },
                    contentPadding = PaddingValues(0.dp),
                    modifier = Modifier.height(32.dp)
                ) {
                    Text(
                        text = stringResource(id = R.string.forgot_password),
                        color = Color.Black,
                        fontSize = 14.sp
                    )
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // 로그인 버튼
            Surface(
                modifier = Modifier
                    .fillMaxWidth(),
                shape = RoundedCornerShape(8.dp),
                shadowElevation = 8.dp
            ) {
                Button(
                    onClick = {
                        isLoginAttempted = true
                        emailError = email.isBlank()
                        passwordError = password.isBlank()
                        if (!emailError && !passwordError) {
                            onLoginClick(email, password) { isSuccess ->
                                if (!isSuccess) {
                                    emailError = true
                                    passwordError = true
                                }
                           }
                        }
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(50.dp),
                    shape = RoundedCornerShape(8.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color.White,
                        contentColor = Color.Black
                    ),
                    elevation = null
                ) {
                    Text(
                        text = stringResource(id = R.string.login_button),
                        color = Color.Black
                    )
                }
            }

            Spacer(modifier = Modifier.height(40.dp))

            // 구분선 & or 텍스트
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                HorizontalDivider(
                    modifier = Modifier.weight(1f),
                    color = MaterialTheme.colorScheme.outline
                )
                Text(
                    text = "or",
                    color = MaterialTheme.colorScheme.outline,
                    fontSize = 12.sp,
                    modifier = Modifier.padding(horizontal = 16.dp)
                )
                HorizontalDivider(
                    modifier = Modifier.weight(1f),
                    color = MaterialTheme.colorScheme.outline
                )
            }

            Spacer(modifier = Modifier.height(2.dp))
            
            Text(
                text = stringResource(id = R.string.login_subtitle),
                fontSize = 12.sp,
                modifier = Modifier.fillMaxWidth(),
                textAlign = TextAlign.Center,
                color = MaterialTheme.colorScheme.onSurface
            )

            // SNS 로그인 버튼들
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // 카카오 로그인
                Surface(
                    shape = CircleShape,
                    modifier = Modifier
                        .size(40.dp)
                        .clickable { /* TODO: Implement Kakao login */ },
                    color = Color.White,
                    shadowElevation = 4.dp
                ) {
                    Image(
                        painter = painterResource(id = R.drawable.ic_kakao),
                        contentDescription = "Kakao Login",
                        modifier = Modifier
                            .fillMaxSize()
                    )
                }
                
                Spacer(modifier = Modifier.width(12.dp))
                
                // 구글 로그인
                Surface(
                    shape = CircleShape,
                    modifier = Modifier
                        .size(40.dp)
                        .clickable { /* TODO: Implement Google login */ },
                    color = Color.White,
                    shadowElevation = 4.dp
                ) {
                    Image(
                        painter = painterResource(id = R.drawable.ic_google),
                        contentDescription = "Google Login",
                        modifier = Modifier
                            .fillMaxSize()
                    )
                }
                
                Spacer(modifier = Modifier.width(12.dp))
                
                // 네이버 로그인
                Surface(
                    shape = CircleShape,
                    modifier = Modifier
                        .size(40.dp)
                        .clickable { /* TODO: Implement Naver login */ },
                    color = Color.White,
                    shadowElevation = 4.dp
                ) {
                    Image(
                        painter = painterResource(id = R.drawable.ic_naver),
                        contentDescription = "Naver Login",
                        modifier = Modifier
                            .fillMaxSize()
                    )
                }
            }

            Spacer(modifier = Modifier.weight(1f))

            // 회원가입 텍스트
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 32.dp)
                    .clickable { 
                        clearInputFields()
                        onSignUpClick() 
                    },
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = stringResource(id = R.string.signup_prompt),
                    color = Color.Black,
                    fontSize = 12.sp
                )
                TextButton(
                    onClick = {
                        clearInputFields()
                        onSignUpClick()
                    },
                    contentPadding = PaddingValues(horizontal = 4.dp, vertical = 0.dp)
                ) {
                    Text(
                        text = stringResource(id = R.string.signup_button),
                        fontWeight = FontWeight.Bold,
                        color = Color.Black,
                        fontSize = 12.sp
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))
    }
}

