package com.taba.lawro.navigation.history

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.BorderStroke
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.taba.lawro.R
import com.taba.lawro.viewmodel.ContractViewModel
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.ui.platform.LocalContext
import com.taba.lawro.data_class.SavedAnalysisResult
import com.taba.lawro.data_class.AwareLevel
import com.taba.lawro.data_class.LegalInterpretationItem

// 위험도 수준 enum
enum class RiskLevel {
    SAFE, WARNING, DANGER
}

// 분석 결과 데이터 클래스
data class ContractAnalysis(
    val id: String,
    val title: String,
    val analysisDate: String,
    val riskLevel: RiskLevel,
    val year: String,
    val description: String = ""
)

// 필터 타입 enum
enum class FilterType {
    ALL, SAFE, WARNING, DANGER, DATE_ASC, DATE_DESC
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HistoryScreen(
    navController: NavController? = null,
    contractViewModel: ContractViewModel = viewModel()
) {
    val context = LocalContext.current
    var searchQuery by remember { mutableStateOf("") }
    var selectedFilter by remember { mutableStateOf(FilterType.ALL) }
    var showFilterDialog by remember { mutableStateOf(false) }
    
    val savedAnalysisResults by contractViewModel.savedAnalysisResults
    
    // 화면 시작 시 저장된 분석 결과들을 로드
    LaunchedEffect(Unit) {
        contractViewModel.loadSavedAnalysisResults(context)
        
        // 더미 데이터 추가 (발표용)
        val dummyResults = listOf(
            // 안전한 계약 더미 데이터
            SavedAnalysisResult(
                id = "dummy_safe_001",
                title = "표준 근로계약서 - 안전",
                contractTitle = "㈜테크컴퍼니 정규직 근로계약서",
                analysisDate = "2024.01.15",
                signatureDate = "2024.01.10",
                aware = "안전",
                totalScore = 8.5,
                summary = "근로기준법을 준수하는 표준적인 근로계약서입니다. 근로시간, 임금, 휴가 등 주요 조건이 법적 기준에 부합하며, 근로자에게 불리한 조항이 없습니다.",
                highlights = listOf(
                    "법정 근로시간 준수 (주 40시간)",
                    "최저임금 이상 지급",
                    "연차휴가 적정 보장",
                    "퇴직금 규정 명시",
                    "부당한 손해배상 조항 없음"
                ),
                legalInterpretation = listOf(
                    LegalInterpretationItem(
                        issue = "근로시간",
                        interpretation = "주 40시간, 1일 8시간 법정 근로시간을 준수하고 있으며, 연장근로 시 할증임금 지급 조항이 포함되어 있습니다."
                    ),
                    LegalInterpretationItem(
                        issue = "임금지급",
                        interpretation = "최저임금 이상의 적정한 임금이 설정되어 있으며, 임금지급일과 지급방법이 명확히 규정되어 있습니다."
                    ),
                    LegalInterpretationItem(
                        issue = "휴가제도",
                        interpretation = "연차휴가 15일이 보장되며, 근로기준법에 따른 휴가 사용 권리가 적절히 명시되어 있습니다."
                    )
                ),
                deepAnalysis = "본 계약서는 근로기준법의 모든 주요 조항을 충실히 반영하고 있습니다. 특히 근로자의 기본권 보장에 충실하며, 회사와 근로자 간의 균형잡힌 권리와 의무를 규정하고 있습니다. 안전하게 체결할 수 있는 표준적인 근로계약서로 평가됩니다."
            ),
            
            // 위험한 계약 더미 데이터
            SavedAnalysisResult(
                id = "dummy_danger_001",
                title = "문제가 있는 계약서 - 위험",
                contractTitle = "○○건설 일용직 근로계약서",
                analysisDate = "2025.01.20",
                signatureDate = "2023.01.18",
                aware = "위험",
                totalScore = 3.5,
                summary = "다수의 법적 문제점이 발견되는 위험한 계약서입니다. 과도한 근로시간, 최저임금 미달, 부당한 손해배상 조항 등 근로자에게 불리한 내용이 포함되어 있습니다.",
                highlights = listOf(
                    "주 60시간 초과 근무 요구",
                    "최저임금 미달 의심",
                    "과도한 손해배상 조항",
                    "연차휴가 미보장",
                    "부당한 계약해지 조항"
                ),
                legalInterpretation = listOf(
                    LegalInterpretationItem(
                        issue = "과도한 근로시간",
                        interpretation = "주 60시간 근무는 근로기준법 위반입니다. 법정 근로시간(주 40시간)과 최대 연장근로시간(주 12시간)을 초과하는 불법적인 조항입니다."
                    ),
                    LegalInterpretationItem(
                        issue = "손해배상 조항",
                        interpretation = "'계약 위반 시 월급의 3배 배상'은 과도한 손해배상 조항으로 근로기준법 제20조 위반에 해당합니다."
                    ),
                    LegalInterpretationItem(
                        issue = "임금 수준",
                        interpretation = "명시된 시급이 최저임금에 미달할 가능성이 높으며, 연장·야간·휴일근로 할증임금 지급 조항이 누락되어 있습니다."
                    ),
                    LegalInterpretationItem(
                        issue = "휴가권리",
                        interpretation = "연차휴가 사용을 제한하는 조항이 있어 근로기준법상 보장된 휴가권을 침해할 소지가 있습니다."
                    )
                ),
                deepAnalysis = "본 계약서는 근로기준법의 핵심 조항들을 다수 위반하고 있어 체결 시 심각한 법적 위험이 예상됩니다. 특히 과도한 근로시간과 손해배상 조항은 근로자의 기본권을 현저히 침해하는 내용입니다. 계약 체결 전 반드시 수정이 필요하며, 가능하다면 계약을 재검토하거나 다른 대안을 모색하는 것이 권장됩니다. 노동청 신고나 법률 상담을 통해 권리구제 방안을 모색하시기 바랍니다."
            )
        )
        
        // 더미 데이터를 ViewModel에 추가
        dummyResults.forEach { dummyResult ->
            contractViewModel.addDummyAnalysisResult(dummyResult)
        }
    }
    
    // SavedAnalysisResult를 ContractAnalysis로 변환
    val analysisData = remember(savedAnalysisResults) {
        savedAnalysisResults.map { saved ->
            val riskLevel = when (AwareLevel.fromString(saved.aware)) {
                AwareLevel.SAFE -> RiskLevel.SAFE
                AwareLevel.WARNING -> RiskLevel.WARNING
                AwareLevel.DANGER -> RiskLevel.DANGER
            }
            val year = SavedAnalysisResult.getYearFromDate(saved.signatureDate)
            
            ContractAnalysis(
                id = saved.id,
                title = saved.title,
                analysisDate = saved.analysisDate,
                riskLevel = riskLevel,
                year = year,
                description = saved.summary.take(50) + if (saved.summary.length > 50) "..." else ""
            )
        }
    }
    
    // 검색 및 필터링 로직
    val filteredData = remember(searchQuery, selectedFilter, analysisData) {
        var filtered = analysisData
        
        // 검색 필터
        if (searchQuery.isNotEmpty()) {
            filtered = filtered.filter { 
                it.title.contains(searchQuery, ignoreCase = true) ||
                it.description.contains(searchQuery, ignoreCase = true)
            }
        }
        
        // 위험도 필터
        filtered = when (selectedFilter) {
            FilterType.SAFE -> filtered.filter { it.riskLevel == RiskLevel.SAFE }
            FilterType.WARNING -> filtered.filter { it.riskLevel == RiskLevel.WARNING }
            FilterType.DANGER -> filtered.filter { it.riskLevel == RiskLevel.DANGER }
            FilterType.DATE_ASC -> filtered.sortedBy { it.analysisDate }
            FilterType.DATE_DESC -> filtered.sortedByDescending { it.analysisDate }
            FilterType.ALL -> filtered
        }
        
        // 년도별 그룹화
        filtered.groupBy { it.year }
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
    ) {
        // 제목 (챗봇 스타일과 동일)
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top =50.dp, bottom = 16.dp),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = stringResource(R.string.history_title),
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold
            )
        }
        
        // 검색 및 필터 섹션
        Column(
            modifier = Modifier.padding(horizontal = 16.dp)
        ) {
            // 검색창
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
                shape = RoundedCornerShape(12.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    OutlinedTextField(
                        value = searchQuery,
                        onValueChange = { searchQuery = it },
                        placeholder = { Text(stringResource(R.string.search_hint), color = Color.Gray) },
                        modifier = Modifier.weight(1f),
                        colors = TextFieldDefaults.colors(
                            focusedContainerColor = Color.Transparent,
                            unfocusedContainerColor = Color.Transparent,
                            focusedIndicatorColor = Color.Transparent,
                            unfocusedIndicatorColor = Color.Transparent,
                            cursorColor = MaterialTheme.colorScheme.primary
                        ),
                        singleLine = true
                    )
                    
                    IconButton(
                        onClick = { 
                            // 검색 실행 (현재는 자동으로 됨)
                        }
                    ) {
                        Icon(
                            Icons.Default.Search, 
                            contentDescription = stringResource(R.string.search),
                            tint = MaterialTheme.colorScheme.primary
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // 필터 버튼들
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // 전체 검색 버튼
                Surface(
                    onClick = { selectedFilter = FilterType.ALL },
                    shape = RoundedCornerShape(16.dp),
                    color = if (selectedFilter == FilterType.ALL) MaterialTheme.colorScheme.primary else Color.White,
                    border = BorderStroke(
                        1.dp, 
                        if (selectedFilter == FilterType.ALL) MaterialTheme.colorScheme.primary else Color(0xFFE0E0E0)
                    ),
                    modifier = Modifier.wrapContentSize()
                ) {
                    Text(
                        text = stringResource(R.string.filter_all),
                        modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
                        color = if (selectedFilter == FilterType.ALL) Color.White else Color.Gray,
                        fontSize = 14.sp
                    )
                }
                
                // 위험 검색 버튼
                Surface(
                    onClick = { selectedFilter = FilterType.DANGER },
                    shape = RoundedCornerShape(16.dp),
                    color = if (selectedFilter == FilterType.DANGER) MaterialTheme.colorScheme.primary else Color.White,
                    border = BorderStroke(
                        1.dp, 
                        if (selectedFilter == FilterType.DANGER) MaterialTheme.colorScheme.primary else Color(0xFFE0E0E0)
                    ),
                    modifier = Modifier.wrapContentSize()
                ) {
                    Text(
                        text = stringResource(R.string.filter_danger),
                        modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
                        color = if (selectedFilter == FilterType.DANGER) Color.White else Color.Gray,
                        fontSize = 14.sp
                    )
                }
                
                Spacer(modifier = Modifier.weight(1f))
                
                IconButton(
                    onClick = { showFilterDialog = true }
                ) {
                    Icon(
                        Icons.Default.FilterList,
                        contentDescription = stringResource(R.string.more_filters),
                        tint = MaterialTheme.colorScheme.primary
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // 분석 기록 리스트
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            filteredData.forEach { (year, contracts) ->
                item {
                    Text(
                        text = "${year}${stringResource(R.string.year_suffix)}",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(vertical = 8.dp)
                    )
                }
                
                items(contracts) { contract ->
                    ContractAnalysisCard(
                        contract = contract,
                        onClick = {
                            // 저장된 분석 결과 찾기
                            val savedResult = savedAnalysisResults.find { it.id == contract.id }
                            savedResult?.let { result ->
                                // 과거 기록 모드로 설정
                                contractViewModel.setCurrentSavedResult(result)
                                // 분석 결과 화면으로 이동
                                navController?.navigate("new_analysis_result")
                            }
                        }
                    )
                }
            }
        }
    }
    
    // 필터 다이얼로그
    if (showFilterDialog) {
        FilterDialog(
            selectedFilter = selectedFilter,
            onFilterSelected = { filter ->
                selectedFilter = filter
                showFilterDialog = false
            },
            onDismiss = { showFilterDialog = false }
        )
    }
}

@Composable
fun ContractAnalysisCard(
    contract: ContractAnalysis,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = contract.title,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                
                Spacer(modifier = Modifier.height(4.dp))
                
                Text(
                    text = "${stringResource(R.string.analysis_date)} ${contract.analysisDate}",
                    fontSize = 12.sp,
                    color = Color.Gray
                )
                
                if (contract.description.isNotEmpty()) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = contract.description,
                        fontSize = 12.sp,
                        color = Color.Gray,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
            }
            
            Spacer(modifier = Modifier.width(16.dp))
            
            // 위험도 아이콘
            RiskLevelIcon(riskLevel = contract.riskLevel)
        }
    }
}

@Composable
fun RiskLevelIcon(riskLevel: RiskLevel) {
    val (icon, color, backgroundColor) = when (riskLevel) {
        RiskLevel.SAFE -> Triple(Icons.Default.Check, Color.White, Color(0xFF4CAF50))
        RiskLevel.WARNING -> Triple(Icons.Default.Warning, Color.White, Color(0xFFFF9800))
        RiskLevel.DANGER -> Triple(Icons.Default.Warning, Color.White, Color(0xFFF44336))
    }
    
    Box(
        modifier = Modifier
            .size(32.dp)
            .clip(CircleShape)
            .background(backgroundColor),
        contentAlignment = Alignment.Center
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = color,
            modifier = Modifier.size(20.dp)
        )
    }
}

@Composable
fun FilterDialog(
    selectedFilter: FilterType,
    onFilterSelected: (FilterType) -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(stringResource(R.string.filter_options)) },
        text = {
            Column {
                FilterOption(stringResource(R.string.filter_all_simple), FilterType.ALL, selectedFilter, onFilterSelected)
                FilterOption(stringResource(R.string.filter_safe), FilterType.SAFE, selectedFilter, onFilterSelected)
                FilterOption(stringResource(R.string.filter_warning), FilterType.WARNING, selectedFilter, onFilterSelected)
                FilterOption(stringResource(R.string.filter_danger_simple), FilterType.DANGER, selectedFilter, onFilterSelected)
                Divider(modifier = Modifier.padding(vertical = 8.dp))
                FilterOption(stringResource(R.string.filter_date_asc), FilterType.DATE_ASC, selectedFilter, onFilterSelected)
                FilterOption(stringResource(R.string.filter_date_desc), FilterType.DATE_DESC, selectedFilter, onFilterSelected)
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text(stringResource(R.string.confirm))
            }
        }
    )
}

@Composable
fun FilterOption(
    text: String,
    filterType: FilterType,
    selectedFilter: FilterType,
    onFilterSelected: (FilterType) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onFilterSelected(filterType) }
            .padding(vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        RadioButton(
            selected = selectedFilter == filterType,
            onClick = { onFilterSelected(filterType) }
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(text)
    }
}