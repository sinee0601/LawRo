package com.taba.lawro.navigation.settings.itemscreens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.taba.lawro.R
import com.taba.lawro.data_class.WorktimeRecord
import java.text.SimpleDateFormat
import java.util.*

@Composable
fun WorktimeRecordsScreen(
    navController: NavController,
    source: String = "home"
) {
    val context = LocalContext.current
    
    // 기록 삭제를 위한 상태 관리
    var recordsState by remember { mutableStateOf<List<WorktimeRecord>>(emptyList()) }
    
    // SharedPreferences에서 실제 저장된 데이터 읽어오기
    fun loadRecords(): List<WorktimeRecord> {
        val sharedPref = context.getSharedPreferences("worktime_records", android.content.Context.MODE_PRIVATE)
        val recordCount = sharedPref.getInt("record_count", 0)
        
        val savedRecords = mutableListOf<WorktimeRecord>()
        
        // 실제 저장된 기록들 읽어오기
        for (i in 1..recordCount) {
            val recordId = "record_$i"
            val date = sharedPref.getString("${recordId}_date", "") ?: ""
            val startTime = sharedPref.getString("${recordId}_start_time", "") ?: ""
            val endTime = sharedPref.getString("${recordId}_end_time", "") ?: ""
            val totalSeconds = sharedPref.getLong("${recordId}_total_seconds", 0)
            val workLocation = sharedPref.getString("${recordId}_work_location", "") ?: ""
            val gpsViolationSeconds = sharedPref.getLong("${recordId}_gps_violation_seconds", 0)
            val gpsViolationStartTime = sharedPref.getString("${recordId}_gps_violation_start_time", "") ?: ""
            val gpsViolationEndTime = sharedPref.getString("${recordId}_gps_violation_end_time", "") ?: ""
            val isCompleted = sharedPref.getBoolean("${recordId}_is_completed", false)
            
            if (date.isNotEmpty()) {
                savedRecords.add(
                    WorktimeRecord(
                        id = recordId,
                        date = date,
                        startTime = startTime,
                        endTime = endTime,
                        totalSeconds = totalSeconds,
                        workLocation = workLocation,
                        workAddress = "",
                        gpsViolations = if (gpsViolationSeconds > 0) 1 else 0,
                        isCompleted = isCompleted,
                        gpsViolationSeconds = gpsViolationSeconds,
                        gpsViolationStartTime = gpsViolationStartTime,
                        gpsViolationEndTime = gpsViolationEndTime
                    )
                )
            }
        }

        
         // 최신순 정렬 (날짜+시간 기준으로 정렬)
         return savedRecords.sortedWith(compareByDescending<WorktimeRecord> { it.date }.thenByDescending { it.startTime })
    }
    
    // 기록 삭제 함수
    fun deleteRecord(recordId: String) {
        val sharedPref = context.getSharedPreferences("worktime_records", android.content.Context.MODE_PRIVATE)
        val editor = sharedPref.edit()
        
        // 해당 기록의 모든 데이터 삭제
        editor.remove("${recordId}_date")
        editor.remove("${recordId}_start_time")
        editor.remove("${recordId}_end_time")
        editor.remove("${recordId}_total_seconds")
        editor.remove("${recordId}_work_location")
        editor.remove("${recordId}_gps_violation_seconds")
        editor.remove("${recordId}_gps_violation_start_time")
        editor.remove("${recordId}_gps_violation_end_time")
        editor.remove("${recordId}_is_completed")
        editor.apply()
        
        // 기록 목록 새로고침
        recordsState = loadRecords()
    }
    
    // 초기 로드
    LaunchedEffect(Unit) {
        recordsState = loadRecords()
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
    ) {
        // 제목
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 0.dp, bottom = 16.dp),
            contentAlignment = Alignment.Center
        ) {
            // 뒤로가기 버튼
            IconButton(
                onClick = { navController.popBackStack() },
                modifier = Modifier
                    .align(Alignment.CenterStart)
                    .padding(start = 16.dp)
                    .size(48.dp)
            ) {
                Icon(
                    painter = painterResource(id = R.drawable.ic_back),
                    contentDescription = stringResource(R.string.back),
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(32.dp)
                )
            }
            
            Text(
                text = stringResource(R.string.worktime_records),
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold
            )
        }

        // 메인 컨텐츠
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(top = 56.dp)
        ) {
            // 요약 정보 카드
            SummaryCard(records = recordsState)
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // 기록 리스트
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                contentPadding = PaddingValues(vertical = 8.dp)
            ) {
                items(recordsState) { record ->
                    WorktimeRecordCard(
                        record = record,
                        onDelete = { deleteRecord(record.id) }
                    )
                }
            }
        }
    }
}

@Composable
private fun SummaryCard(records: List<WorktimeRecord>) {
    val context = LocalContext.current
    val totalHours = records.sumOf { it.totalSeconds } / 3600.0
    val totalDays = records.size
    val avgHours = if (totalDays > 0) totalHours / totalDays else 0.0
    
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            Text(
                text = stringResource(R.string.worktime_summary),
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = Color.Black
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                SummaryItem(
                    title = stringResource(R.string.total_work_days),
                    value = "${totalDays}${stringResource(R.string.days_unit)}",
                    icon = Icons.Default.DateRange,
                    color = Color(0xFF2196F3)
                )
                
                SummaryItem(
                    title = stringResource(R.string.total_work_hours), 
                    value = String.format("%.1f${stringResource(R.string.hours_unit)}", totalHours),
                    icon = Icons.Default.AccessTime,
                    color = Color(0xFF4CAF50)
                )
                
                SummaryItem(
                    title = stringResource(R.string.daily_average),
                    value = String.format("%.1f${stringResource(R.string.hours_unit)}", avgHours),
                    icon = Icons.Default.TrendingUp,
                    color = Color(0xFFFF9800)
                )
            }
        }
    }
}

@Composable
private fun SummaryItem(
    title: String,
    value: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    color: Color
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = color,
            modifier = Modifier.size(24.dp)
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = value,
            fontSize = 16.sp,
            fontWeight = FontWeight.Bold,
            color = color
        )
        Text(
            text = title,
            fontSize = 12.sp,
            color = Color.Gray
        )
    }
}

@Composable
private fun WorktimeRecordCard(
    record: WorktimeRecord,
    onDelete: () -> Unit
) {
    var showDeleteDialog by remember { mutableStateOf(false) }
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // 헤더 (날짜와 상태, 삭제 버튼)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = record.date,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.Black
                )
                
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    if (record.isCompleted) {
                        Icon(
                            imageVector = Icons.Default.CheckCircle,
                            contentDescription = stringResource(R.string.completed),
                            tint = Color(0xFF4CAF50),
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = stringResource(R.string.completed),
                            fontSize = 12.sp,
                            color = Color(0xFF4CAF50)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                    }
                    
                    // 삭제 버튼
                    IconButton(
                        onClick = { showDeleteDialog = true },
                        modifier = Modifier.size(24.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Delete,
                            contentDescription = stringResource(R.string.delete),
                            tint = Color(0xFFFF5722),
                            modifier = Modifier.size(16.dp)
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // 근무지 정보
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Default.LocationOn,
                    contentDescription = null,
                    tint = Color(0xFF2196F3),
                    modifier = Modifier.size(16.dp)
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text(
                    text = record.workLocation,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    color = Color.Black
                )
            }
            
            Spacer(modifier = Modifier.height(4.dp))
            
            // 시간 정보
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.Schedule,
                        contentDescription = null,
                        tint = Color(0xFF4CAF50),
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "${record.startTime} ~ ${record.endTime}",
                        fontSize = 12.sp,
                        color = Color.Gray
                    )
                }
                
                Text(
                    text = record.getFormattedDuration(),
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF4CAF50)
                )
            }
            
            // GPS 이탈 정보 (있는 경우에만)
            if (record.gpsViolationSeconds > 0) {
                Spacer(modifier = Modifier.height(8.dp))
                Column {
                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.Warning,
                            contentDescription = null,
                            tint = Color(0xFFFF9800),
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "${stringResource(R.string.gps_violation_prefix)}${record.getFormattedGpsViolationTime()}",
                            fontSize = 12.sp,
                            color = Color(0xFFFF9800)
                        )
                    }
                    
                    // GPS 위반 시간대 표시
                    if (record.gpsViolationStartTime.isNotEmpty() && record.gpsViolationEndTime.isNotEmpty()) {
                        Spacer(modifier = Modifier.height(4.dp))
                        Row(
                            modifier = Modifier.padding(start = 20.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "${record.gpsViolationStartTime} ~ ${record.gpsViolationEndTime}",
                                fontSize = 11.sp,
                                color = Color(0xFFFF9800)
                            )
                        }
                    }
                }
            }
        }
    }
    
    // 삭제 확인 대화상자
    if (showDeleteDialog) {
        AlertDialog(
            onDismissRequest = { showDeleteDialog = false },
            title = {
                Text(text = stringResource(R.string.delete_record_title))
            },
            text = {
                Text(text = stringResource(R.string.delete_record_message, record.date))
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        showDeleteDialog = false
                        onDelete()
                    }
                ) {
                    Text(text = stringResource(R.string.delete), color = Color(0xFFFF5722))
                }
            },
            dismissButton = {
                TextButton(
                    onClick = { showDeleteDialog = false }
                ) {
                    Text(text = stringResource(R.string.cancel))
                }
            }
        )
    }
} 