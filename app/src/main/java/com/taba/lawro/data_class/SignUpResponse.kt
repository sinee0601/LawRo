package com.taba.lawro.data_class

data class SignUpResponse(
    val success: Boolean,
    val message: String,
    val user_id: String
)