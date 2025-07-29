package com.taba.lawro.navigation

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import androidx.navigation.compose.currentBackStackEntryAsState
import com.taba.lawro.R
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.lifecycle.viewmodel.compose.viewModel
import com.taba.lawro.viewmodel.ContractViewModel

@Composable
fun BottomNavigation(
    navController: NavController,
    contractViewModel: ContractViewModel = viewModel()
) {
    Box(
        modifier = Modifier.drawBehind {
            drawLine(
                color = Color(0xFFE0E0E0),
                start = Offset(0f, 0f),
                end = Offset(size.width, 0f),
                strokeWidth = 1.dp.toPx()
            )
        }
    ) {
        NavigationBar(
            containerColor = Color.White,
            contentColor = Color(0xFF0C8FF6)
        ) {
            val navBackStackEntry by navController.currentBackStackEntryAsState()
            val currentRoute = navBackStackEntry?.destination?.route
            val iconSize = 30.dp

            // 과거 기록 보기 여부 확인
            val isViewingPastRecord = contractViewModel.isViewingPastRecord()
            
            // Analyze 탭에 속하는 route들
            val analyzeRoutes = listOf(
                Screen.Analyze.route, 
                "edit_contract", 
                "analysis_result"
            )
            
            // 분석 결과 관련 route들 (과거 기록 여부에 따라 탭 선택이 달라짐)
            val analysisResultRoutes = listOf("new_analysis_result", "detailed_analysis")
            
            // Analyze 탭 선택 조건
            val isAnalyzeSelected = when {
                currentRoute in analyzeRoutes -> true
                currentRoute in analysisResultRoutes && !isViewingPastRecord -> true
                else -> false
            }

            // source argument 추출 (worktime_records/{source} 형태)
            val sourceArgument = navBackStackEntry?.arguments?.getString("source")
            
            // Worktime 탭에 속하는 route들
            val worktimeRoutes = listOf(Screen.Worktime.route)
            val isWorktimeSelected = currentRoute in worktimeRoutes || 
                (currentRoute?.startsWith("worktime_records") == true && sourceArgument == "worktime")

            // Home 탭에 속하는 route들 (설정 관련 화면들도 포함)
            val homeRoutes = listOf(
                Screen.Home.route,
                Screen.Settings.route,
                "my_info",
                "change_password", 
                "change_language",
                "language_change_success",
                "app_info",
                "privacy_policy"
            )
            val isHomeSelected = currentRoute in homeRoutes ||
                (currentRoute?.startsWith("worktime_records") == true && sourceArgument == "home")

            // History 탭 선택 조건
            val isHistorySelected = when {
                currentRoute == Screen.History.route -> true
                currentRoute in analysisResultRoutes && isViewingPastRecord -> true
                else -> false
            }

            // Chatbot 탭 선택 조건 (chatbot으로 시작하는 모든 경로 포함)
            val isChatbotSelected = currentRoute?.startsWith("chatbot") == true

            // 1. 계약서 분석
            NavigationBarItem(
                icon = {
                    Icon(
                        painter = painterResource(
                            id = if (isAnalyzeSelected) {
                                R.drawable.ic_analyze_selected
                            } else {
                                R.drawable.ic_analyze_unselected
                            }
                        ),
                        contentDescription = "근로계약서 분석",
                        modifier = Modifier.size(iconSize),
                        tint = Color.Unspecified
                    )
                },
                selected = isAnalyzeSelected,
                onClick = {
                    navController.navigate(Screen.Analyze.route) {
                        popUpTo(Screen.Home.route) { saveState = true }
                        launchSingleTop = true
                        restoreState = true
                    }
                },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = Color.Unspecified,
                    unselectedIconColor = Color.Unspecified,
                    indicatorColor = Color.Transparent
                )
            )

            // 2. 기록 확인
            NavigationBarItem(
                icon = {
                    Icon(
                        painter = painterResource(
                            id = if (isHistorySelected) {
                                R.drawable.ic_history_selected
                            } else {
                                R.drawable.ic_history_unselected
                            }
                        ),
                        contentDescription = "과거 분석 기록",
                        modifier = Modifier.size(iconSize),
                        tint = Color.Unspecified
                    )
                },
                selected = isHistorySelected,
                onClick = {
                    navController.navigate(Screen.History.route) {
                        popUpTo(Screen.Home.route) { saveState = true }
                        launchSingleTop = true
                        restoreState = true
                    }
                },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = Color.Unspecified,
                    unselectedIconColor = Color.Unspecified,
                    indicatorColor = Color.Transparent
                )
            )

            // 3. 홈 (중간)
            NavigationBarItem(
                icon = {
                    if (isHomeSelected) {
                        Icon(
                            imageVector = Icons.Filled.Home,
                            contentDescription = "홈",
                            modifier = Modifier.size(iconSize),
                            tint = Color(0xFF0C8FF6)
                        )
                    } else {
                        Icon(
                            painter = painterResource(id = R.drawable.ic_home_thin),
                            contentDescription = "홈",
                            modifier = Modifier.size(26.dp),
                            tint = Color(0xFF0C8FF6)
                        )
                    }
                },
                selected = isHomeSelected,
                onClick = {
                    contractViewModel.clearCurrentSavedResult()
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Home.route) {
                            inclusive = true
                        }
                        launchSingleTop = true
                    }
                },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = Color.Unspecified,
                    unselectedIconColor = Color.Unspecified,
                    indicatorColor = Color.Transparent
                )
            )

            // 4. 근무시간 측정
            NavigationBarItem(
                icon = {
                    Icon(
                        painter = painterResource(
                            id = if (isWorktimeSelected) {
                                R.drawable.ic_worktime_selected
                            } else {
                                R.drawable.ic_worktime_unselected
                            }
                        ),
                        contentDescription = "근무 시간 측정",
                        modifier = Modifier.size(iconSize),
                        tint = Color.Unspecified
                    )
                },
                selected = isWorktimeSelected,
                onClick = {
                    contractViewModel.clearCurrentSavedResult()
                    navController.navigate(Screen.Worktime.route) {
                        popUpTo(Screen.Home.route) { saveState = true }
                        launchSingleTop = true
                        restoreState = true
                    }
                },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = Color.Unspecified,
                    unselectedIconColor = Color.Unspecified,
                    indicatorColor = Color.Transparent
                )
            )

            // 5. 챗봇
            NavigationBarItem(
                icon = {
                    Icon(
                        painter = painterResource(
                            id = if (isChatbotSelected) {
                                R.drawable.ic_chatbot_selected
                            } else {
                                R.drawable.ic_chatbot_unselected
                            }
                        ),
                        contentDescription = "챗봇",
                        modifier = Modifier.size(iconSize),
                        tint = Color.Unspecified
                    )
                },
                selected = isChatbotSelected,
                onClick = {
                    contractViewModel.clearCurrentSavedResult()
                    navController.navigate(Screen.Chatbot.route) {
                        popUpTo(Screen.Home.route) { saveState = true }
                        launchSingleTop = true
                        restoreState = true
                    }
                },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = Color.Unspecified,
                    unselectedIconColor = Color.Unspecified,
                    indicatorColor = Color.Transparent
                )
            )
        }
    }
}
