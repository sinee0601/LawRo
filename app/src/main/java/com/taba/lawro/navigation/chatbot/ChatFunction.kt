package com.taba.lawro.navigation.chatbot

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import com.taba.lawro.R
import com.taba.lawro.data_class.ChatMessage

@Composable
fun ChatBubble(message: ChatMessage) {
    val alignment = if (message.isUser) Alignment.End else Alignment.Start
    val bubbleColor = if (message.isUser) Color.White else Color(0xFFE8F0FE)
    val icon = if (message.isUser) R.drawable.ic_user else R.drawable.ic_bot

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 8.dp, vertical = 3.dp),
        horizontalArrangement = if (message.isUser) Arrangement.End else Arrangement.Start
    ) {
        if (!message.isUser) {
            Box(
                modifier = Modifier
                    .size(32.dp),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    painterResource(id = icon), 
                    contentDescription = null, 
                    tint = Color(0xFF0C8FF6),
                    modifier = Modifier.size(24.dp)
                )
            }
            Spacer(modifier = Modifier.width(6.dp))
        }

        Surface(
            color = bubbleColor,
            shape = RoundedCornerShape(10.dp),
            tonalElevation = 1.dp,
            shadowElevation = 2.dp
        ) {
            Text(
                text = if (message.isTyping) stringResource(R.string.chatbot_typing) else message.text,
                modifier = Modifier.padding(10.dp),
                color = Color.Black,
                fontSize = 14.sp,
                lineHeight = 20.sp
            )
        }

        if (message.isUser) {
            Spacer(modifier = Modifier.width(6.dp))
            Box(
                modifier = Modifier
                    .size(32.dp),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    painterResource(id = icon), 
                    contentDescription = null, 
                    tint = Color(0xFF0C8FF6),
                    modifier = Modifier.size(24.dp)
                )
            }
        }
    }
}
