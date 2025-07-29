package com.taba.lawro.findPassword

import android.app.Activity
import android.os.Handler
import android.os.Looper
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.RoundedCornerShape
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
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.taba.lawro.R
import com.taba.lawro.components.CustomTextField

@Composable
fun FindPasswordOneScreen(
    navController: NavController,
    onSignUpClick: (String, String, String) -> Unit = { _, _, _ -> },
) {
    var name by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var verificationCode by remember { mutableStateOf("") }


    var nameError by remember { mutableStateOf(false) }
    var emailError by remember { mutableStateOf(false) }
    var verificationError by remember { mutableStateOf(false) }

    val context = LocalContext.current
    val activity = context as? Activity
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
            .verticalScroll(rememberScrollState())
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
                text = stringResource(R.string.find_password),
                fontSize = 18.sp,
                fontWeight = FontWeight.Medium,
                modifier = Modifier.align(Alignment.Center)
            )
        }

        // 입력 필드들
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp)
                .padding(top = 40.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
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
                        nameError = false
                    },
                    placeholder = stringResource(R.string.name_hint),
                    isError = nameError,
                    modifier = Modifier.fillMaxWidth()
                )
            }
            // 이메일 입력
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(min = 90.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text =stringResource(R.string.email),
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium
                )
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    CustomTextField(
                        value = email.substringBefore("@"),
                        onValueChange = {
                            email = "$it${if (email.contains("@")) "@${email.substringAfter("@")}" else ""}"
                            emailError = false
                        },
                        placeholder = stringResource(R.string.email),
                        isError = emailError,
                        modifier = Modifier.weight(1f)
                    )
                    Text(
                        text = "@",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium
                    )
                    CustomTextField(
                        value = if (email.contains("@")) email.substringAfter("@") else "",
                        onValueChange = {
                            email = "${email.substringBefore("@")}@$it"
                            emailError = false
                        },
                        placeholder = stringResource(R.string.select),
                        isError = emailError,
                        modifier = Modifier.weight(1f)
                    )
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
                            verificationError = false
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
            }
        }
        
        Spacer(modifier = Modifier.weight(1f))
        
        // 비밀번호 변경 메일받기 버튼
        Button(
            onClick = {
                navController.navigate("find_password_two_screen")
                // 유효성 검사
//                nameError = name.isBlank()
//                emailError = !email.contains("@") || !email.contains(".")
//                verificationError = verificationCode.length != 6
//                passwordError = password.length < 8
//                confirmPasswordError = password != confirmPassword
//
//                if (!nameError && !emailError && !verificationError &&
//                    !passwordError && !confirmPasswordError) {
//                    onSignUpClick(email, password, name)
//                }
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
                text = stringResource(R.string.receive_password_reset_email),
                fontSize = 16.sp,
                modifier = Modifier.padding(vertical = 4.dp)
            )
        }
    }
}