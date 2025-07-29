package com.taba.lawro.data_class

data class SignUpRequest(
    val email: String,
    val password: String,
    val full_name: String
)