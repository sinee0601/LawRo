package com.taba.lawro.data_class

data class LoginResponse(
    val success: Boolean,
    val message: String,
    val access_token: String,
    val token_type: String,
    val user_info: UserInfo?
)

data class UserInfo(
    val user_id: String?,
    val email: String?,
    val full_name: String?
)