package com.taba.lawro.data_class

import java.util.Date

data class WorktimeRecord(
    val id: String = "",
    val date: String = "", // 근무 날짜 (예: "2025.02.01")
    val startTime: String = "", // 시작 시간 (예: "09:00")
    val endTime: String = "", // 종료 시간 (예: "18:00")
    val totalSeconds: Long = 0, // 총 근무 시간 (초)
    val workLocation: String = "", // 근무지 이름
    val workAddress: String = "", // 근무지 주소
    val gpsViolations: Int = 0, // GPS 이탈 횟수
    val isCompleted: Boolean = false, // 근무 완료 여부
    val gpsViolationSeconds: Long = 0L, // GPS 위반 총 시간 (초)
    val gpsViolationStartTime: String = "", // GPS 위반 시작 시간
    val gpsViolationEndTime: String = "", // GPS 위반 종료 시간
    val createdAt: Date = Date()
) {
    // 총 근무시간을 HH:MM:SS 형태로 반환
    fun getFormattedDuration(): String {
        val hours = totalSeconds / 3600
        val minutes = (totalSeconds % 3600) / 60
        val seconds = totalSeconds % 60
        return String.format("%02d:%02d:%02d", hours, minutes, seconds)
    }
    
    // 총 근무시간을 시간 단위로 반환 (예: "8.5시간")
    fun getDurationInHours(): String {
        val hours = totalSeconds / 3600.0
        return String.format("%.1f시간", hours)
    }
    
    // GPS 위반 시간을 MM:SS 형태로 반환
    fun getFormattedGpsViolationTime(): String {
        val minutes = gpsViolationSeconds / 60
        val seconds = gpsViolationSeconds % 60
        return String.format("%02d:%02d", minutes, seconds)
    }
} 