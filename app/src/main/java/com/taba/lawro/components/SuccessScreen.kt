package com.taba.lawro.components

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.taba.lawro.R

@Composable
fun SuccessScreen(
    mainString : String,
    subString : String
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp, alignment = Alignment.Top),

        ) {
        Spacer(modifier = Modifier.height(120.dp))
        Image(
            painter = painterResource(id = R.drawable.symbol_logo_blue),
            contentDescription = "symbol_logo_blue",
            modifier = Modifier
                .size(180.dp)
        )
        androidx.compose.material.Text(
            text = mainString,
            fontWeight = FontWeight.Bold,
            fontSize = 25.sp
        )
        androidx.compose.material.Text(
            text = subString,
            fontSize = 16.sp,
            color = Color.Gray
        )
    }
}
