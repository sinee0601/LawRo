    package com.taba.lawro.navigation.settings

    import android.content.Context
    import android.content.Intent
    import androidx.compose.foundation.background
    import androidx.compose.foundation.clickable
    import androidx.compose.foundation.layout.*
    import androidx.compose.foundation.lazy.LazyColumn
    import androidx.compose.foundation.shape.RoundedCornerShape
    import androidx.compose.material.icons.Icons
    import androidx.compose.material.icons.filled.*
    import androidx.compose.material3.*
    import androidx.compose.runtime.Composable
    import androidx.compose.ui.Alignment
    import androidx.compose.ui.Modifier
    import androidx.compose.ui.text.font.FontWeight
    import androidx.compose.ui.unit.dp
    import androidx.compose.ui.unit.sp
    import androidx.navigation.NavController
    import androidx.annotation.DrawableRes
    import androidx.compose.ui.graphics.ColorFilter
    import androidx.compose.ui.res.painterResource
    import androidx.compose.foundation.Image
    import androidx.compose.ui.graphics.Color
    import androidx.compose.ui.graphics.vector.ImageVector
    import androidx.compose.ui.platform.LocalContext
    import androidx.compose.ui.res.stringResource

    import com.taba.lawro.login.LoginActivity
    import com.taba.lawro.R

    @Composable
fun SettingsScreen(navController: NavController) {
    Box(
        modifier = Modifier
            .fillMaxSize().background(Color.White)
           .windowInsetsPadding(WindowInsets.systemBars)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(Color.White)
                .padding(top = 18.dp, bottom = 16.dp),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = stringResource(R.string.settings_title),
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold
            )
        }

        // 메인 컨텐츠
        Column(
            modifier = Modifier
                .fillMaxSize().background(Color.White)
                .padding(top = 56.dp) // 제목 공간만큼 여백 추가
        ) {

            // 스크롤 가능한 컨텐츠
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp),
                contentPadding = PaddingValues(bottom = 16.dp)
            ) {
                item {
                    Text(
                        text = stringResource(R.string.account_section), 
                        fontWeight = FontWeight.Bold, 
                        fontSize = 16.sp,
                        modifier = Modifier.padding(vertical = 8.dp)
                    )
                }
                
                item {
                    SettingsItemVector(Icons.Default.Person, stringResource(R.string.my_info)) {
                        navController.navigate("my_info")
                    }
                }
                
                item {
                    SettingsItemVector(Icons.Default.Lock, stringResource(R.string.change_password)) {
                        navController.navigate("change_password")
                    }
                }
                
                item {
                    SettingsItemVector(Icons.Default.Language, stringResource(R.string.change_language)) {
                        navController.navigate("change_language")
                    }
                }
                
                item {
                    SettingsItemVector(Icons.Default.AccessTime, stringResource(R.string.worktime_records)) {
                        navController.navigate("worktime_records/home")
                    }
                }

                item {
                    Text(
                        text = stringResource(R.string.info_section), 
                        fontWeight = FontWeight.Bold, 
                        fontSize = 16.sp,
                        modifier = Modifier.padding(top = 24.dp, bottom = 8.dp)
                    )
                }
                
                item {
                    SettingsItemVector(Icons.Default.Info, stringResource(R.string.app_description)) {
                        navController.navigate("app_info")
                    }
                }
                
                item {
                    SettingsItemVector(Icons.Default.PrivacyTip, stringResource(R.string.privacy_policy)) {
                        navController.navigate("privacy_policy")
                    }
                }

                item {
                    Spacer(modifier = Modifier.height(32.dp))
                }
                
                item {
                    val context = LocalContext.current
                    Button(
                        onClick = {
                            doLogout(context)
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 8.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = MaterialTheme.colorScheme.primaryContainer,
                            contentColor = MaterialTheme.colorScheme.onPrimaryContainer
                        ),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Text(stringResource(R.string.logout))
                    }
                }
            }
        }
    }
}

    fun doLogout(context: Context) {
        val loginPrefs = context.getSharedPreferences("login_pref", Context.MODE_PRIVATE)
        loginPrefs.edit().clear().apply()

        val intent = Intent(context, LoginActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        context.startActivity(intent)
    }

    @Composable
    fun SettingsItemDrawable(
        @DrawableRes iconResId: Int,
        title: String,
        highlighted: Boolean = false,
        iconTint: Color = Color(0xFF005BBB),
        onClick: () -> Unit
    ) {
        val backgroundColor = if (highlighted) Color(0xFFE3F2FD) else Color.White

        Surface(
            shape = RoundedCornerShape(12.dp),
            shadowElevation = 4.dp,
            color = backgroundColor,
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 4.dp)
                .clickable(onClick = onClick)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(16.dp)
            ) {
                Image(
                    painter = painterResource(id = iconResId),
                    contentDescription = title,
                    colorFilter = ColorFilter.tint(iconTint),
                    modifier = Modifier.size(36.dp)
                )
                Spacer(modifier = Modifier.width(16.dp))
                Text(title, modifier = Modifier.weight(1f))
                Icon(Icons.Default.ChevronRight, contentDescription = "Go")
            }
        }
    }

    @Composable
    fun SettingsItemVector(
        icon: ImageVector,
        title: String,
        highlighted: Boolean = false,
        iconTint: Color = Color(0xFF005BBB),
        onClick: () -> Unit
    ) {
        val backgroundColor = if (highlighted) Color(0xFFE3F2FD) else Color.White

        Surface(
            shape = RoundedCornerShape(12.dp),
            shadowElevation = 4.dp,
            color = backgroundColor,
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 4.dp)
                .clickable(onClick = onClick)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(16.dp)
            ) {
                Icon(icon, contentDescription = title, tint = iconTint)
                Spacer(modifier = Modifier.width(16.dp))
                Text(title, modifier = Modifier.weight(1f))
                Icon(Icons.Default.ChevronRight, contentDescription = "Go")
            }
        }
    }




