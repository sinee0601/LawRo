package com.taba.lawro.splash

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import com.taba.lawro.R
import kotlinx.coroutines.delay


@Composable
fun SplashScreen(onTimeout: () -> Unit) {
    LaunchedEffect(Unit) {
        delay(2000)
        onTimeout()
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF005FDC)),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Image(
                painter = painterResource(id = R.drawable.symbol_logo_white),
                contentDescription = null,
                modifier = Modifier.size(180.dp)
                                   .offset(x= (-5).dp)
            )
            Image(
                painter = painterResource(id = R.drawable.typo_logo_white),
                contentDescription = null,
                modifier = Modifier.size(160.dp)
                                   .offset(x =5.dp, y = (-100).dp)

            )
        }
    }
}