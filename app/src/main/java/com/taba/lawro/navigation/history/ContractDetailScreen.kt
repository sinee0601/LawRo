package com.taba.lawro.navigation.history

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
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.taba.lawro.R

// 분석 항목 데이터 클래스
data class AnalysisItem(
    val title: String,
    val description: String,
    val riskLevel: RiskLevel
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ContractDetailScreen(
    contractId: String,
    navController: NavController? = null
) {
    // 샘플 데이터 (실제로는 contractId를 기반으로 API에서 가져올 예정)
    val contractInfo = remember {
        ContractAnalysis(
            id = contractId,
            title = "2025 근로계약서",
            analysisDate = "2025.02.01",
            riskLevel = RiskLevel.SAFE,
            year = "2025",
            description = "정규직 근로 계약서"
        )
    }
    
    val analysisItems = listOf(
        AnalysisItem(
            title = stringResource(R.string.issues_without_problems),
            description = "근로자는 휴일(공휴일 포함) 근로의 대가로서 근로기준법에서 정한 휴일근로수당을 받습니다.",
            riskLevel = RiskLevel.SAFE
        ),
        AnalysisItem(
            title = stringResource(R.string.dangerous_risk_issues),
            description = "제 7조(임금의 지급) 임금 근로자에 대한 기본급과 수당제공에 대한 기준이 명확히 제시되지 않았습니다.",
            riskLevel = RiskLevel.DANGER
        ),
        AnalysisItem(
            title = stringResource(R.string.issues_requiring_attention),
            description = "제 9조(근로의 의무) 임금 근로자에 대한 기본급과 수당제공에 대한 기준이 20% 부족하게 책정될 수 있습니다.",
            riskLevel = RiskLevel.WARNING
        ),
        AnalysisItem(
            title = stringResource(R.string.issues_requiring_attention),
            description = "제 4조(근로의 의무) 임금 근로자에 대한 기본급과 수당제공에 대한 기준이 20% 부족하게 책정될 수 있습니다.",
            riskLevel = RiskLevel.WARNING
        )
    )
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF5F5F5))
    ) {
        // 상단 헤더
        TopAppBar(
            title = { 
                Text(
                    stringResource(R.string.detail_record),
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Medium
                )
            },
            navigationIcon = {
                IconButton(onClick = { navController?.popBackStack() }) {
                    Icon(Icons.Default.ArrowBack, contentDescription = stringResource(R.string.back))
                }
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = Color.White
            )
        )
        
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // 계약서 정보 카드
            item {
                ContractInfoCard(contractInfo)
            }
            
            // 분석 결과 리스트
            items(analysisItems) { item ->
                AnalysisItemCard(item)
            }
            
            // PDF 내보내기 버튼
            item {
                Spacer(modifier = Modifier.height(16.dp))
                Button(
                    onClick = { 
                        // PDF 내보내기 로직
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(48.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF2196F3)
                    ),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(
                        Icons.Default.PictureAsPdf,
                        contentDescription = null,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        stringResource(R.string.export_pdf),
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
            }
        }
    }
}

@Composable
fun ContractInfoCard(contract: ContractAnalysis) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            Text(
                text = contract.title,
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = "${stringResource(R.string.analysis_date_label)} ${contract.analysisDate}",
                fontSize = 14.sp,
                color = Color.Gray
            )
        }
    }
}

@Composable
fun AnalysisItemCard(item: AnalysisItem) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                RiskLevelIcon(riskLevel = item.riskLevel)
                
                Spacer(modifier = Modifier.width(12.dp))
                
                Text(
                    text = item.title,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium,
                    color = when (item.riskLevel) {
                        RiskLevel.SAFE -> Color(0xFF4CAF50)
                        RiskLevel.WARNING -> Color(0xFFFF9800)
                        RiskLevel.DANGER -> Color(0xFFF44336)
                    }
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Text(
                text = item.description,
                fontSize = 14.sp,
                color = Color(0xFF666666),
                lineHeight = 20.sp
            )
        }
    }
} 