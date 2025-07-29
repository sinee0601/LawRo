package com.taba.lawro.network

import android.util.Log
import com.taba.lawro.data_class.ChatRequest
import com.taba.lawro.data_class.ChatResponse
import com.taba.lawro.data_class.SessionResponse
import com.taba.lawro.data_class.ChatHistoryResponse
import com.taba.lawro.network.RetrofitClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class LawRoRepository {
    
    private val apiService = RetrofitClient.apiService

    suspend fun sendMessage(
        message: String,
        user_language: String = "korean",
        sessionId: String? = null,
        context: String? = null
    ): Result<ChatResponse> {
        return withContext(Dispatchers.IO) {
            try {
                val request = ChatRequest(
                    message = message,
                    sessionId = sessionId,
                    context = context,
                    userLanguage = user_language
                )
                
                Log.d("LawRoRepository", "메시지 전송: $message")
                val response = apiService.sendMessage(request)
                
                Log.d("LawRoRepository", "응답 성공: ${response.message}")
                Result.success(response)
                
            } catch (e: Exception) {
                Log.e("LawRoRepository", "메시지 전송 실패", e)
                Result.failure(e)
            }
        }
    }

    suspend fun createNewSession(): Result<SessionResponse> {
        return withContext(Dispatchers.IO) {
            try {
                Log.d("LawRoRepository", "새 세션 생성 시작")
                val response = apiService.createNewSession()
                
                if (response.isSuccessful) {
                    response.body()?.let { sessionResponse ->
                        Log.d("LawRoRepository", "세션 생성 성공: ${sessionResponse.sessionId}")
                        Result.success(sessionResponse)
                    } ?: Result.failure(Exception("세션 생성 응답이 비어있습니다"))
                } else {
                    Log.e("LawRoRepository", "세션 생성 실패: ${response.code()}")
                    Result.failure(Exception("세션 생성 실패: ${response.code()} ${response.message()}"))
                }
            } catch (e: Exception) {
                Log.e("LawRoRepository", "세션 생성 오류", e)
                Result.failure(e)
            }
        }
    }
    

    suspend fun getChatHistory(sessionId: String): Result<ChatHistoryResponse> {
        return withContext(Dispatchers.IO) {
            try {
                Log.d("LawRoRepository", "채팅 히스토리 조회: $sessionId")
                val response = apiService.getChatHistory(sessionId)
                
                if (response.isSuccessful) {
                    response.body()?.let { historyResponse ->
                        Log.d("LawRoRepository", "히스토리 조회 성공: ${historyResponse.messageCount}개 메시지")
                        Result.success(historyResponse)
                    } ?: Result.failure(Exception("히스토리 응답이 비어있습니다"))
                } else {
                    Log.e("LawRoRepository", "히스토리 조회 실패: ${response.code()}")
                    Result.failure(Exception("히스토리 조회 실패: ${response.code()} ${response.message()}"))
                }
            } catch (e: Exception) {
                Log.e("LawRoRepository", "히스토리 조회 오류", e)
                Result.failure(e)
            }
        }
    }

    suspend fun checkServerHealth(): Result<Boolean> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.healthCheck()
                Result.success(response.isSuccessful)
            } catch (e: Exception) {
                Log.e("LawRoRepository", "서버 상태 확인 오류", e)
                Result.failure(e)
            }
        }
    }
} 