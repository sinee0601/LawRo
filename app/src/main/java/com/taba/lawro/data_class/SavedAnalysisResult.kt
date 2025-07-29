package com.taba.lawro.data_class

import java.text.SimpleDateFormat
import java.util.*

data class SavedAnalysisResult(
    val id: String = UUID.randomUUID().toString(),
    val title: String,
    val contractTitle: String,
    val analysisDate: String,
    val signatureDate: String?, // 서명 날짜 (정렬용)
    val saveDate: String = getCurrentDate(),
    val aware: String,
    val totalScore: Double,
    val summary: String,
    val highlights: List<String>,
    val legalInterpretation: List<LegalInterpretationItem>,
    val deepAnalysis: String
) {
    companion object {
        fun getCurrentDate(): String {
            val sdf = SimpleDateFormat("yyyy.MM.dd", Locale.getDefault())
            return sdf.format(Date())
        }
        
        fun getCurrentYear(): String {
            val sdf = SimpleDateFormat("yyyy", Locale.getDefault())
            return sdf.format(Date())
        }
        
        fun getYearFromDate(dateString: String?): String {
            return try {
                if (dateString.isNullOrBlank()) {
                    getCurrentYear()
                } else {
                    // 다양한 날짜 형식 지원
                    val formats = listOf(
                        "yyyy.MM.dd",
                        "yyyy-MM-dd",
                        "yyyy/MM/dd",
                        "MM.dd.yyyy",
                        "MM-dd-yyyy",
                        "MM/dd/yyyy"
                    )
                    
                    for (format in formats) {
                        try {
                            val sdf = SimpleDateFormat(format, Locale.getDefault())
                            val date = sdf.parse(dateString)
                            val yearFormat = SimpleDateFormat("yyyy", Locale.getDefault())
                            return yearFormat.format(date!!)
                        } catch (e: Exception) {
                            continue
                        }
                    }
                    getCurrentYear()
                }
            } catch (e: Exception) {
                getCurrentYear()
            }
        }
    }
} 