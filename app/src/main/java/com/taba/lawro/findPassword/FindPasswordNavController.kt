package com.taba.lawro.findPassword

import androidx.compose.runtime.Composable
import androidx.compose.ui.res.stringResource
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.taba.lawro.R
import com.taba.lawro.components.SuccessScreen

@Composable
fun FindPasswordNavController() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "find_password_one_screen") {
        composable("find_password_one_screen") {
            FindPasswordOneScreen(navController)
        }
        composable("find_password_two_screen"){
            FindPasswordTwoScreen(navController)
        }

        composable("success_screen") {
            SuccessScreen(stringResource(R.string.password_change_complete),(stringResource(R.string.login_with_new_password)))
        }
    }
}