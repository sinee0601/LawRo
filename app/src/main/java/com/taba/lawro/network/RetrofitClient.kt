package com.taba.lawro.network

import com.google.gson.GsonBuilder
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import okhttp3.Interceptor
import okhttp3.Response
import android.util.Log

object RetrofitClient {

    private const val BASE_URL = "http://16.176.26.197:8000/"

    private val gson = GsonBuilder()
        .setDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSSSS")
        .create()

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
        setLevel(HttpLoggingInterceptor.Level.BODY)
    }

    // 커스텀 인터셉터: 원본 JSON 응답 로깅
    private val customLoggingInterceptor = Interceptor { chain ->
        val request = chain.request()
        val response = chain.proceed(request)
        
        if (request.url.toString().contains("/contract/api/analyze")) {
            val responseBody = response.body
            val source = responseBody?.source()
            source?.request(Long.MAX_VALUE)
            val buffer = source?.buffer
            val responseBodyString = buffer?.clone()?.readUtf8()
            
            Log.d("CustomInterceptor", "=== 원본 JSON 응답 (analyze API) ===")
            Log.d("CustomInterceptor", responseBodyString ?: "null")
            Log.d("CustomInterceptor", "=== 원본 JSON 끝 ===")
        }
        
        response
    }

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(customLoggingInterceptor)
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(60, TimeUnit.SECONDS)
        .build()

    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create(gson))
        .build()

    val apiService: LawRoApiService = retrofit.create(LawRoApiService::class.java)
}