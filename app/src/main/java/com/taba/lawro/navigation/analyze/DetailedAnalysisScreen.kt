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
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.navigation.NavController
import androidx.lifecycle.viewmodel.compose.viewModel
import com.taba.lawro.R
import com.taba.lawro.viewmodel.ContractViewModel
import com.taba.lawro.data_class.LegalInterpretationItem
import android.content.Context

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DetailedAnalysisScreen(
    navController: NavController,
    contractViewModel: ContractViewModel = viewModel()
) {
    val newAnalysisResult by contractViewModel.newAnalysisResult
    val isViewingPastRecord = contractViewModel.isViewingPastRecord()
    val context = androidx.compose.ui.platform.LocalContext.current
    var showSaveDialog by remember { mutableStateOf(false) }
    var titleInput by remember { mutableStateOf("") }
    
    newAnalysisResult?.let { result ->
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

                Text(
                    text = stringResource(R.string.detailed_analysis),
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // 상세 분석 콘텐츠
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // 법적 해석 섹션
                LegalInterpretationSection(legalInterpretations = result.legalInterpretation)
                
                // 상세 분석 섹션
                DeepAnalysisSection(deepAnalysis = result.deepAnalysis)
                
                Spacer(modifier = Modifier.height(24.dp))
                
                // 하단 버튼들 (과거 기록을 보고 있을 때는 저장 버튼 숨김)
                BottomButtons(
                    onSaveClick = if (!isViewingPastRecord) {
                        { showSaveDialog = true }
                    } else null,
                    onChatbotClick = {
                        // 분석 결과를 챗봇 질문으로 자동 생성
                        val analysisQuery = buildAnalysisQuery(result, context)
                        navController.navigate("chatbot?autoQuery=${java.net.URLEncoder.encode(analysisQuery, "UTF-8")}") {
                            popUpTo("home") { saveState = true }
                            launchSingleTop = true
                            restoreState = true
                        }
                    },
                    showSaveButton = !isViewingPastRecord
                )
            }
        }
        
        // 저장 다이얼로그
        if (showSaveDialog) {
            SaveAnalysisDialog(
                title = titleInput,
                onTitleChange = { titleInput = it },
                onSave = { title ->
                    // 실제 저장 로직 구현
                    contractViewModel.saveAnalysisResultLocally(context, title)
                    showSaveDialog = false
                    titleInput = ""
                    
                    // 저장 완료 후 분석 화면으로 이동 (백스택 정리)
                    navController.navigate("analyze") {
                        popUpTo("analyze") { inclusive = true }
                        launchSingleTop = true
                    }
                },
                onDismiss = {
                    showSaveDialog = false
                    titleInput = ""
                }
            )
        }
    }
}

@Composable
private fun LegalInterpretationSection(legalInterpretations: List<LegalInterpretationItem>) {
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
                text = stringResource(R.string.legal_interpretation),
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Color.Black
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            legalInterpretations.forEachIndexed { index, item ->
                LegalInterpretationItem(
                    item = item,
                    index = index + 1
                )
                
                if (index < legalInterpretations.size - 1) {
                    Spacer(modifier = Modifier.height(16.dp))
                    Divider(
                        color = Color(0xFFE0E0E0),
                        thickness = 1.dp
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                }
            }
        }
    }
}

@Composable
private fun LegalInterpretationItem(
    item: LegalInterpretationItem,
    index: Int
) {
    Column {
        // 이슈 제목
        Row(
            verticalAlignment = Alignment.Top
        ) {
            Surface(
                modifier = Modifier.size(24.dp),
                shape = RoundedCornerShape(12.dp),
                color = Color(0xFF2196F3)
            ) {
                Box(
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = index.toString(),
                        color = Color.White,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
            
            Spacer(modifier = Modifier.width(12.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = item.issue,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium,
                    color = Color(0xFF2196F3)
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = item.interpretation,
                    fontSize = 14.sp,
                    lineHeight = 20.sp,
                    color = Color(0xFF333333)
                )
            }
        }
    }
}

@Composable
private fun DeepAnalysisSection(deepAnalysis: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Default.Analytics,
                    contentDescription = null,
                    tint = Color(0xFF4CAF50),
                    modifier = Modifier.size(24.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = stringResource(R.string.comprehensive_analysis),
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.Black
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = deepAnalysis,
                fontSize = 14.sp,
                lineHeight = 22.sp,
                color = Color(0xFF333333),
                textAlign = TextAlign.Justify
            )
        }
    }
}

@Composable
private fun BottomButtons(
    onSaveClick: (() -> Unit)? = null,
    onChatbotClick: () -> Unit,
    showSaveButton: Boolean = true
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // 결과 저장 버튼 (조건부 표시)
        if (showSaveButton && onSaveClick != null) {
            Button(
                onClick = onSaveClick,
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.primary
                ),
                shape = RoundedCornerShape(12.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Save,
                    contentDescription = null,
                    tint = Color.White,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = stringResource(R.string.save_result),
                    color = Color.White,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.padding(vertical = 8.dp)
                )
            }
        }
        
        // 챗봇 문의 버튼
        OutlinedButton(
            onClick = onChatbotClick,
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.outlinedButtonColors(
                contentColor = MaterialTheme.colorScheme.primary
            ),
            border = ButtonDefaults.outlinedButtonBorder.copy(
                brush = androidx.compose.ui.graphics.SolidColor(MaterialTheme.colorScheme.primary)
            ),
            shape = RoundedCornerShape(12.dp)
        ) {
            Icon(
                imageVector = Icons.Default.Chat,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(20.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = stringResource(R.string.chatbot_inquiry),
                color = MaterialTheme.colorScheme.primary,
                fontSize = 16.sp,
                fontWeight = FontWeight.Medium,
                modifier = Modifier.padding(vertical = 8.dp)
            )
        }
    }
}

@Composable
private fun SaveAnalysisDialog(
    title: String,
    onTitleChange: (String) -> Unit,
    onSave: (String) -> Unit,
    onDismiss: () -> Unit
) {
    Dialog(onDismissRequest = onDismiss) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // 제목
                Text(
                    text = stringResource(R.string.save_analysis_result),
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.Black
                )
                
                // 설명
                Text(
                    text = stringResource(R.string.enter_title_to_save),
                    fontSize = 14.sp,
                    color = Color(0xFF666666),
                    lineHeight = 20.sp
                )
                
                // 입력 필드
                OutlinedTextField(
                    value = title,
                    onValueChange = onTitleChange,
                    label = { Text(stringResource(R.string.title)) },
                    placeholder = { Text(stringResource(R.string.title_example)) },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = MaterialTheme.colorScheme.primary,
                        focusedLabelColor = MaterialTheme.colorScheme.primary
                    )
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                // 버튼들
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    // 취소 버튼
                    OutlinedButton(
                        onClick = onDismiss,
                        modifier = Modifier.weight(1f),
                        colors = ButtonDefaults.outlinedButtonColors(
                            contentColor = Color(0xFF666666)
                        ),
                        border = ButtonDefaults.outlinedButtonBorder.copy(
                            brush = androidx.compose.ui.graphics.SolidColor(Color(0xFFE0E0E0))
                        )
                    ) {
                        Text(stringResource(R.string.cancel))
                    }
                    
                    // 저장 버튼
                    Button(
                        onClick = { 
                            if (title.isNotBlank()) {
                                onSave(title.trim())
                            }
                        },
                        modifier = Modifier.weight(1f),
                        enabled = title.isNotBlank(),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = MaterialTheme.colorScheme.primary
                        )
                    ) {
                        Text(stringResource(R.string.save), color = Color.White)
                    }
                }
            }
        }
    }
}

// 분석 결과를 챗봇 질문으로 변환하는 함수
private fun buildAnalysisQuery(result: com.taba.lawro.data_class.NewAnalysisResponse, context: Context): String {
    val sb = StringBuilder()
    
    // 주요 문제점들을 더 자세히
    sb.append(context.getString(R.string.analysis_major_issues)).append("\n")
    result.highlights.forEachIndexed { index, highlight ->
        sb.append("${index + 1}. $highlight\n")
    }
    sb.append("\n")
    
    // 모든 문제점에 대한 구체적 질문
    sb.append(context.getString(R.string.specific_questions_about_issues)).append("\n\n")
    result.highlights.forEachIndexed { index, highlight ->
        sb.append(context.getString(R.string.issue_number_format, index + 1, highlight)).append("\n")
        sb.append(context.getString(R.string.ask_for_specific_damage_solution)).append("\n\n")
    }
    
    sb.append(context.getString(R.string.request_practical_advice))
    
    return sb.toString()
} 