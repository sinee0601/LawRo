package com.taba.lawro.navigation.chatbot

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.graphics.Color
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.taba.lawro.data_class.ChatMessage
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.sp
import android.util.Log
import androidx.compose.ui.text.font.FontWeight
import com.taba.lawro.R
import com.taba.lawro.network.LawRoRepository
import com.taba.lawro.selectLanguage.LanguageManager
import kotlinx.coroutines.launch
import androidx.compose.foundation.layout.imePadding
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.foundation.layout.statusBarsPadding

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatbotScreen(
    language: String,
    autoQuery: String? = null
) {
    val messages = remember { mutableStateListOf<ChatMessage>() }
    var input by remember { mutableStateOf("") }
    val scope = rememberCoroutineScope()
    val repository = remember { LawRoRepository() }
    var currentSessionId by remember { mutableStateOf<String?>(null) }
    val context = LocalContext.current
    val listState = rememberLazyListState()
    
    // 앱 시작시 새 세션 생성
    LaunchedEffect(Unit) {
        repository.createNewSession()
            .onSuccess { sessionResponse ->
                currentSessionId = sessionResponse.sessionId
                Log.d("ChatbotScreen", "새 세션 생성됨: ${sessionResponse.sessionId}")
            }
            .onFailure { error ->
                Log.e("ChatbotScreen", "세션 생성 실패", error)
            }
    }
    
    // 자동 질문이 있으면 초기화할 때 추가하고 바로 전송
    LaunchedEffect(autoQuery, currentSessionId) {
        if (!autoQuery.isNullOrBlank() && messages.isEmpty() && currentSessionId != null) {
            // URL 디코딩하여 한글 복원
            val decodedQuery = try {
                java.net.URLDecoder.decode(autoQuery, "UTF-8")
            } catch (e: Exception) {
                autoQuery // 디코딩 실패 시 원본 사용
            }
            
            // 사용자 메시지 추가
            messages.add(ChatMessage(
                role = "user",
                content = decodedQuery
            ))
            
            // 타이핑 메시지 추가
            val typingMsg = ChatMessage(
                role = "assistant",
                content = context.getString(R.string.chatbot_typing),
                isTyping = true
            )
            messages.add(typingMsg)
            
            // 자동으로 메시지 전송
            repository.sendMessage(
                message = decodedQuery,
                user_language = language,
                sessionId = currentSessionId
            )
            .onSuccess { response ->
                messages.remove(typingMsg)
                messages.add(ChatMessage(
                    role = "assistant",
                    content = response.message
                ))
                Log.d("ChatbotScreen", "자동 전송 AI 응답: ${response.message}")
                
                // 응답 후 스크롤
                scope.launch {
                    listState.animateScrollToItem(messages.size - 1)
                }
            }
            .onFailure { error ->
                messages.remove(typingMsg)
                messages.add(ChatMessage(
                    role = "assistant",
                    content = context.getString(R.string.chatbot_error, error.message)
                ))
                Log.e("ChatbotScreen", "자동 전송 실패", error)
            }
        }
    }

    // 메시지가 추가될 때마다 맨 아래로 스크롤
    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            listState.scrollToItem(messages.size - 1)
        }
    }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
            .statusBarsPadding()
    ) {
        Column(
            modifier = Modifier.fillMaxSize()
        ) {
            // 헤더
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 14.dp, bottom = 16.dp),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = context.getString(R.string.chatbot_title),
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
            }
            
            // 채팅 메시지 리스트
            LazyColumn(
                state = listState,
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color.White)
                    .padding(horizontal = 8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
                contentPadding = PaddingValues(
                    top = 8.dp, 
                    bottom = 100.dp // 입력창과의 간격 증가
                )
            ) {
                items(messages) { msg ->
                    ChatBubble(msg)
                }
            }
        }
        
        // 입력창을 하단에 고정
        Surface(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .windowInsetsPadding(WindowInsets.ime),
            color = Color.White,
            tonalElevation = 2.dp,
            shadowElevation = 4.dp
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                TextField(
                    value = input,
                    onValueChange = { input = it },
                    modifier = Modifier.weight(1f),
                    placeholder = { Text(context.getString(R.string.chatbot_input_hint)) },
                    colors = TextFieldDefaults.colors(
                        focusedContainerColor = Color.Transparent,
                        unfocusedContainerColor = Color.Transparent,
                        focusedIndicatorColor = Color.Transparent,
                        unfocusedIndicatorColor = Color.Transparent
                    )
                )
                Spacer(modifier = Modifier.width(8.dp))
                Box(
                    modifier = Modifier
                        .size(56.dp),
                    contentAlignment = Alignment.Center
                ) {
                    IconButton(
                        onClick = {
                        if (input.isNotBlank()) {
                            val userMessage = input
                            messages.add(ChatMessage(
                                role = "user",
                                content = userMessage
                            ))
                            input = ""

                            val typingMsg = ChatMessage(
                                role = "assistant",
                                content = context.getString(R.string.chatbot_typing),
                                isTyping = true
                            )
                            messages.add(typingMsg)

                            scope.launch {
                                repository.sendMessage(
                                    message = userMessage,
                                    user_language = language,
                                    sessionId = currentSessionId
                                )
                                                                    .onSuccess { response ->
                                        messages.remove(typingMsg)
                                        messages.add(ChatMessage(
                                            role = "assistant",
                                            content = response.message
                                        ))

                                        Log.d("ChatbotScreen", "AI 응답: ${response.message}")
                                        Log.d("ChatbotScreen", "처리 시간: ${response.processingTime}초")
                                        
                                        // 응답 후 스크롤
                                        scope.launch {
                                            listState.animateScrollToItem(messages.size - 1)
                                        }
                                    }
                                .onFailure { error ->
                                    messages.remove(typingMsg)
                                    messages.add(ChatMessage(
                                        role = "assistant",
                                        content = context.getString(R.string.chatbot_error, error.message)
                                    ))
                                    Log.e("ChatbotScreen", "메시지 전송 실패", error)
                                }
                            }
                        }
                    }) {
                        Icon(
                            painter = if (input.isBlank())
                                painterResource(R.drawable.ic_send_isblanked)
                            else
                                painterResource(R.drawable.ic_send_isnotblanked),
                            contentDescription = "전송",
                            modifier = Modifier.size(32.dp),
                            tint = if (input.isBlank()) Color(0xFF0C8FF6) else Color.Unspecified                            )
                    }
                }
            }
        }
    }
}
