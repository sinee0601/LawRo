package com.taba.lawro.data_class

data class UploadResponse(
    val message: String,
    val contract_id: String,
    val s3_keys: List<String>,
    val language: String,
    val file_count: Int
) 