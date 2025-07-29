package com.taba.lawro

import android.os.Bundle
import androidx.activity.compose.setContent
import androidx.core.view.WindowCompat
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.zIndex
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.taba.lawro.base.BaseActivity
import com.taba.lawro.navigation.BottomNavigation
import com.taba.lawro.navigation.Screen
import com.taba.lawro.navigation.analyze.AnalyzeScreen
import com.taba.lawro.navigation.analyze.EditContractScreen
import com.taba.lawro.navigation.analyze.NewAnalysisResultScreen
import com.taba.lawro.navigation.analyze.DetailedAnalysisScreen
import com.taba.lawro.navigation.chatbot.ChatbotScreen
import com.taba.lawro.navigation.history.HistoryScreen
import com.taba.lawro.navigation.history.ContractDetailScreen
import com.taba.lawro.navigation.settings.SettingsScreen
import com.taba.lawro.navigation.settings.itemscreens.*
import com.taba.lawro.navigation.worktime.WorktimeScreen
import com.taba.lawro.navigation.home.HomeScreen
import com.taba.lawro.selectLanguage.LanguageManager
import com.taba.lawro.navigation.settings.itemscreens.ChangeLanguageScreen
import com.taba.lawro.ui.theme.LawRoTheme
import com.taba.lawro.viewmodel.ContractViewModel
import com.taba.lawro.viewmodel.LoadingViewModel


class MainActivity : BaseActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // 상태바 색상을 직접 설정 (테스트용으로 빨간색)
        window.statusBarColor = android.graphics.Color.RED
        WindowCompat.getInsetsController(window, window.decorView).isAppearanceLightStatusBars = false

        val sharedPref = getSharedPreferences("login_pref", MODE_PRIVATE)
        val uid = sharedPref.getString("uid", null).orEmpty()
        val token = sharedPref.getString("token", null).orEmpty()

        val langPref = getSharedPreferences("LanguagePrefs", MODE_PRIVATE)
        val langCode = langPref.getString("SelectedLanguage", "en")
        val language = LanguageManager.getLanguageNameFromCode(langCode)

        // 로그 찍기 (확인용)
        android.util.Log.d("MainActivity", "uid: $uid, token: $token, language: $language")

        setContent {
            LawRoTheme {
                Surface(
                    color = Color.White
                ) {
                    val navController = rememberNavController()
                    val contractViewModel: ContractViewModel = viewModel()
                    val loadingViewModel: LoadingViewModel = viewModel()

                    val isGlobalLoading by loadingViewModel.isLoading.collectAsState()

                    Box(modifier = Modifier.fillMaxSize()) {
                        Scaffold(
                            bottomBar = { BottomNavigation(navController = navController, contractViewModel = contractViewModel) },
                            contentWindowInsets = WindowInsets(0, 0, 0, 0)
                        ) { paddingValues ->
                            Box(modifier = Modifier.padding(paddingValues)) {
                                NavHost(
                                    navController = navController,
                                    startDestination = Screen.Home.route
                                ) {
                                    composable(Screen.Home.route) { HomeScreen(navController) }
                                    composable(Screen.Analyze.route) {
                                        AnalyzeScreen(
                                            uid,
                                            token,
                                            language,
                                            navController,
                                            contractViewModel,
                                            loadingViewModel
                                        )
                                    }
                                    composable(Screen.History.route) {
                                        HistoryScreen(
                                            navController,
                                            contractViewModel
                                        )
                                    }
                                    composable(Screen.Chatbot.route) { ChatbotScreen(language) }
                                    composable("chatbot?autoQuery={autoQuery}") { backStackEntry ->
                                        val autoQuery = backStackEntry.arguments?.getString("autoQuery")
                                        ChatbotScreen(
                                            language = language,
                                            autoQuery = autoQuery
                                        )
                                    }
                                    composable(Screen.Worktime.route) { WorktimeScreen(navController = navController) }
                                    composable(Screen.Settings.route) { SettingsScreen(navController) }

                                    composable("edit_contract") {
                                        EditContractScreen(
                                            contractViewModel = contractViewModel,
                                            navController = navController,
                                            loadingViewModel = loadingViewModel
                                        )
                                    }
                                    composable("new_analysis_result") {
                                        NewAnalysisResultScreen(
                                            navController = navController,
                                            contractViewModel = contractViewModel
                                        )
                                    }
                                    composable("detailed_analysis") {
                                        DetailedAnalysisScreen(
                                            navController = navController,
                                            contractViewModel = contractViewModel
                                        )
                                    }
                                    composable("contract_detail/{contractId}") { backStackEntry ->
                                        val contractId =
                                            backStackEntry.arguments?.getString("contractId") ?: ""
                                        ContractDetailScreen(
                                            contractId = contractId,
                                            navController = navController
                                        )
                                    }
                                    composable("my_info") {
                                        MyInfoScreen(
                                            token = token,
                                            navController = navController
                                        )
                                    }
                                    composable("change_password") { ChangePasswordScreen() }
                                    composable("change_language") {
                                        ChangeLanguageScreen(
                                            navController
                                        )
                                    }
                                    composable("language_change_success") {
                                        ChangeLanguageScreen(
                                            navController,
                                            showSuccessScreen = true
                                        )
                                    }
                                    composable("worktime_records/{source}") { backStackEntry ->
                                        val source = backStackEntry.arguments?.getString("source") ?: "home"
                                        WorktimeRecordsScreen(
                                            navController,
                                            source = source
                                        )
                                    }
                                    composable("app_info") { AppInfoScreen(navController) }
                                    composable("privacy_policy") { PrivacyPolicyScreen(navController) }
                                }
                            }
                        }

                        // 전역 로딩 오버레이
                        if (isGlobalLoading) {
                            Box(
                                modifier = Modifier
                                    .fillMaxSize()
                                    .background(Color.Black.copy(alpha = 0.6f))
                                    .zIndex(1000f),
                                contentAlignment = Alignment.Center
                            ) {
                                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                    CircularProgressIndicator(
                                        color = Color.White
                                    )
                                    Spacer(modifier = Modifier.height(16.dp))
                                    Text(
                                        text = stringResource(id = R.string.uploading_and_analyzing),
                                        color = Color.White,
                                        fontSize = 16.sp,
                                        fontWeight = FontWeight.Medium
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
    }

}