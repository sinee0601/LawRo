package com.taba.lawro.navigation

sealed class Screen(val route: String) {
    object Home : Screen("home")
    object Analyze : Screen("analyze")
    object History : Screen("history")
    object Chatbot : Screen("chatbot")
    object Worktime : Screen("worktime")
    object Settings : Screen("settings")

    companion object {
        val bottomNavItems = listOf(
            Analyze,
            History,
            Home,
            Worktime,
            Chatbot
        )
    }
} 