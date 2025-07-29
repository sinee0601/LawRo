package com.taba.lawro.data_class

import com.google.gson.annotations.SerializedName

// 분석 결과 전체 응답
data class AnalysisResultResponse(
    @SerializedName("success") val success: Boolean,
    @SerializedName("message") val message: String,
    @SerializedName("contract_title") val contractTitle: String? = null,
    @SerializedName("analysis_date") val analysisDate: String? = null,
    @SerializedName("analysis_results") val analysisResults: List<AnalysisResultItem>? = null
)

// 개별 분석 결과 항목
data class AnalysisResultItem(
    @SerializedName("type") val type: String, // "success", "warning", "error"
    @SerializedName("message") val message: String,
    @SerializedName("severity") val severity: Int? = null, // 심각도 (1-5)
    @SerializedName("category") val category: String? = null // 카테고리 (근로시간, 임금 등)
)

// UI에서 사용할 분석 결과 데이터
data class AnalysisResultUIItem(
    val type: AnalysisResultType,
    val message: String,
    val iconColor: androidx.compose.ui.graphics.Color,
    val category: String? = null
)

enum class AnalysisResultType {
    SUCCESS, WARNING, ERROR
} 