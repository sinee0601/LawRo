package com.taba.lawro.data_class

data class AnalyzeWithChatbotRequest(
    val user_id: String,
    val contract_id: String,
    val use_chatbot: Boolean = true,
    val user_language: String,
    val use_saved_data: Boolean = true
)

data class AnalyzeWithChatbotResponse(
    val success: Boolean,
    val message: String,
    val analysis_result: Map<String, Any>? = null
) 