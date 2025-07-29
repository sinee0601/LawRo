package com.taba.lawro.data_class

import com.google.gson.annotations.SerializedName

// 새로운 분석 결과 응답 구조
data class NewAnalysisResponse(
    @SerializedName("totalScore") val totalScore: Double,
    @SerializedName("aware") val aware: String, // "위험", "주의", "안전"
    @SerializedName("summary") val summary: String,
    @SerializedName("highlights") val highlights: List<String>,
    @SerializedName("legalInterpretation") val legalInterpretation: List<LegalInterpretationItem>,
    @SerializedName("deepAnalysis") val deepAnalysis: String
)

data class LegalInterpretationItem(
    @SerializedName("issue") val issue: String,
    @SerializedName("interpretation") val interpretation: String
)

// 위험도 enum
enum class AwareLevel(val displayName: String, val colorCode: String) {
    SAFE("안전", "#4CAF50"),
    WARNING("주의", "#FF9800"), 
    DANGER("위험", "#F44336");
    
    companion object {
        fun fromString(value: String): AwareLevel {
            return when(value) {
                "안전" -> SAFE
                "주의" -> WARNING
                "위험" -> DANGER
                else -> WARNING
            }
        }
    }
} 