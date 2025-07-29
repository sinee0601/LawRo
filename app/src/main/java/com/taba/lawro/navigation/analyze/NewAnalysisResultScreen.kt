package com.taba.lawro.navigation.analyze

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.rememberScrollState
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
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import androidx.lifecycle.viewmodel.compose.viewModel
import com.taba.lawro.R
import com.taba.lawro.viewmodel.ContractViewModel
import com.taba.lawro.data_class.NewAnalysisResponse
import com.taba.lawro.data_class.AwareLevel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NewAnalysisResultScreen(
    navController: NavController,
    contractViewModel: ContractViewModel = viewModel()
) {
    val context = LocalContext.current
    val newAnalysisResult by contractViewModel.newAnalysisResult
    val isViewingPastRecord = contractViewModel.isViewingPastRecord()
    
    // 더미 데이터가 없으면 생성 (현재 화면의 언어 설정이 적용된 Context 사용)
    LaunchedEffect(Unit) {
        if (newAnalysisResult == null) {
            contractViewModel.setNewDummyAnalysisResult(context)
        }
    }
    
    newAnalysisResult?.let { result ->
        val awareLevel = AwareLevel.fromString(result.aware)
        
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background((Color.White))
                .verticalScroll(rememberScrollState())
                .padding(start = 8.dp,end = 8.dp)
        ) {

            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 30.dp, bottom = 16.dp)
                    .offset( y = (-10).dp),
                contentAlignment = Alignment.Center
            ) {
                // 뒤로가기 버튼 (왼쪽)
                IconButton(
                    onClick = { 
                        if (isViewingPastRecord) {
                            contractViewModel.clearCurrentSavedResult()
                        }
                        navController.navigateUp() 
                    },
                    modifier = Modifier
                        .align(Alignment.CenterStart)
                        .size(48.dp)
                ) {
                    Icon(
                        painter = painterResource(id = R.drawable.ic_back),
                        contentDescription = "뒤로가기",
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.size(32.dp)
                    )
                }
                
                // 제목 (중앙)
                Text(
                    text = stringResource(R.string.analysis_result),
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // 분석 결과 콘텐츠
            Column(
                modifier = Modifier
                    .wrapContentHeight()
                    .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // 위험도 결과 카드
                RiskResultCard(
                    awareLevel = awareLevel,
                    totalScore = result.totalScore,
                    summary = result.summary
                )
                
                // 주요 문제점 카드
                HighlightsCard(highlights = result.highlights)
                
                Spacer(modifier = Modifier.height(12.dp))
                
                // 결과 확인 버튼
                Button(
                    onClick = {
                        navController.navigate("detailed_analysis")
                    },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.primary
                    ),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text(
                        text = stringResource(R.string.check_result),
                        color = Color.White,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium,
                        modifier = Modifier.padding(vertical = 8.dp)
                    )
                }
                
                
                // 하단 여백 (스크롤을 위한 최소 공간)
                Spacer(modifier = Modifier.height(32.dp))
                        }
        }
    }
} 

@Composable
private fun RiskResultCard(
    awareLevel: AwareLevel,
    totalScore: Double,
    summary: String
) {
    val riskColor = Color(android.graphics.Color.parseColor(awareLevel.colorCode))
    val riskIcon = when(awareLevel) {
        AwareLevel.SAFE -> Icons.Default.CheckCircle
        AwareLevel.WARNING -> Icons.Default.Warning
        AwareLevel.DANGER -> Icons.Default.Error
    }
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            // 위험도 아이콘과 레벨
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center
            ) {
                Icon(
                    imageVector = riskIcon,
                    contentDescription = null,
                    tint = riskColor,
                    modifier = Modifier.size(32.dp)
                )
                Spacer(modifier = Modifier.width(12.dp))
                Text(
                    text = when(awareLevel) {
                        AwareLevel.SAFE -> stringResource(R.string.risk_level_safe)
                        AwareLevel.WARNING -> stringResource(R.string.risk_level_warning)
                        AwareLevel.DANGER -> stringResource(R.string.risk_level_danger)
                    },
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold,
                    color = riskColor
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // 요약문
            Text(
                text = summary,
                fontSize = 14.sp,
                lineHeight = 20.sp,
                color = Color(0xFF333333),
                textAlign = TextAlign.Start
            )
        }
    }
}

@Composable
private fun HighlightsCard(highlights: List<String>) {
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
                text = stringResource(R.string.key_issues),
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Color.Black
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            highlights.forEach { highlight ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 6.dp),
                    verticalAlignment = Alignment.Top
                ) {
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = highlight,
                        fontSize = 14.sp,
                        lineHeight = 20.sp,
                        color = Color(0xFF333333),
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }
    }
} 