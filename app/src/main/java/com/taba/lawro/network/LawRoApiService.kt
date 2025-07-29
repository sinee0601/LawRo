package com.taba.lawro.network

import com.taba.lawro.data_class.*
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Path

interface LawRoApiService {

    //로그인
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>

    //회원가입
    @POST("auth/signup")
    suspend fun signup(@Body request: SignUpRequest): Response<SignUpResponse>

    //이미지 전송 (기존)
    @Multipart
    @POST("contract/upload-and-extract")
    suspend fun uploadContract(
        @Header("Authorization") token: String,
        @Part image: MultipartBody.Part,
        @Part("uid") uid: RequestBody,
        @Part("language") language: RequestBody
    ):  Response<AnalyzeRequest>

    //이미지 전송 (새로운 API)
    @Multipart
    @POST("contract/api/upload")
    suspend fun uploadContractNew(
        @Part("user_id") userId: RequestBody,
        @Part("language") language: RequestBody,
        @Part("contract_id") contractId: RequestBody,
        @Part files: MultipartBody.Part
    ): Response<UploadResponse>
    
    //이미지 전송 (다중 파일용)
    @Multipart  
    @POST("contract/api/upload")
    suspend fun uploadContractMultiple(
        @Part("user_id") userId: RequestBody,
        @Part("language") language: RequestBody,
        @Part("contract_id") contractId: RequestBody,
        @Part files: List<MultipartBody.Part>
    ): Response<UploadResponse>

    //계약서 분석
    @POST("contract/api/analyze")
    suspend fun analyzeContract(
        @Body request: AnalyzeApiRequest
    ): Response<AnalyzeResponse>

    // 계약서 챗봇 분석
    @POST("contract/api/analyze-with-chatbot")
    suspend fun analyzeWithChatbot(
        @Body request: AnalyzeWithChatbotRequest
    ): Response<AnalyzeWithChatbotResponse>

    //프로필 조회
    @GET("auth/profile")
    suspend fun getProfile(
        @Header("Authorization") token: String
    ): Response<ProfileResponse>

    // 채팅 메시지 전송
    @POST("chat/send")
    suspend fun sendChatMessage(@Body request: ChatRequest): Response<ChatResponse>
    
    // 기존 API와의 호환성을 위한 메서드
    @POST("chat/send")
    suspend fun sendMessage(@Body request: ChatRequest): ChatResponse
    
    // 새로운 세션 생성
    @POST("chat/new-session")
    suspend fun createNewSession(): Response<SessionResponse>
    
    // 채팅 히스토리 조회
    @GET("chat/history/{session_id}")
    suspend fun getChatHistory(@Path("session_id") sessionId: String): Response<ChatHistoryResponse>
    
    // 헬스 체크
    @GET("health")
    suspend fun healthCheck(): Response<Map<String, Any>>
    
    // 계약서 분석 결과 저장
    @POST("contract/save-analysis")
    suspend fun saveAnalysis(
        @Header("Authorization") token: String,
        @Body request: SaveAnalysisRequest
    ): Response<SaveAnalysisResponse>
} 