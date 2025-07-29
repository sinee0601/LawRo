package com.taba.lawro.navigation.analyze

import android.content.Context
import android.widget.Toast
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.wrapContentHeight
import androidx.compose.foundation.layout.wrapContentWidth
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.taba.lawro.R
import com.taba.lawro.viewmodel.ContractViewModel
import androidx.navigation.NavController

@Composable
fun EditContractScreen(
    contractViewModel: ContractViewModel, 
    navController: NavController,
    loadingViewModel: com.taba.lawro.viewmodel.LoadingViewModel? = null
)
{
    val context = LocalContext.current
    val contract = contractViewModel.contract.value
    val isSaving by contractViewModel.isSaving
    val saveError by contractViewModel.saveError
    val saveSuccess by contractViewModel.saveSuccess
    
    // 분석 상태 추가
    val isAnalyzing by contractViewModel.isAnalyzing
    val analyzeError by contractViewModel.analyzeError
    val analyzeSuccess by contractViewModel.analyzeSuccess

    // SharedPreferences에서 필요한 데이터 가져오기
    val sharedPref = context.getSharedPreferences("login_pref", Context.MODE_PRIVATE)
    val uid = sharedPref.getString("uid", null).orEmpty()
    val token = sharedPref.getString("token", null).orEmpty()
    val userLanguage = sharedPref.getString("language", "korean") ?: "korean"
    
    // 실제 서버에서 받은 contract_id 사용
    val contractId = contractViewModel.contractId.value ?: "unknown_contract"
    
    // contract_id 확인 로깅
    android.util.Log.d("EditContractScreen", "사용할 Contract ID: $contractId")
    android.util.Log.d("EditContractScreen", "ViewModel에 저장된 Contract ID: ${contractViewModel.contractId.value}")
    android.util.Log.d("EditContractScreen", "사용자 언어: $userLanguage")

    // 문자열 리소스를 미리 가져오기
    val contractSavedSuccessfullyText = stringResource(R.string.contract_saved_successfully)
    val saveFailedText = stringResource(R.string.save_failed)
    val analysisCompletedText = stringResource(R.string.analysis_completed)
    val analysisFailedText = stringResource(R.string.analysis_failed)
    val loginInfoMissingText = stringResource(R.string.login_info_missing)

    // 저장 성공/실패 처리
    LaunchedEffect(saveSuccess) {
        if (saveSuccess) {
            Toast.makeText(context, contractSavedSuccessfullyText, Toast.LENGTH_SHORT).show()
            contractViewModel.clearSaveState()
        }
    }
    
    LaunchedEffect(saveError) {
        saveError?.let { error ->
            Toast.makeText(context, "$saveFailedText: $error", Toast.LENGTH_LONG).show()
            contractViewModel.clearSaveState()
        }
    }

    // 분석 성공/실패 처리
    LaunchedEffect(analyzeSuccess) {
        if (analyzeSuccess) {
            Toast.makeText(context, analysisCompletedText, Toast.LENGTH_SHORT).show()
            contractViewModel.clearSaveState()
            // 분석 결과 화면으로 이동
            navController.navigate("analysis_result")
        }
    }
    
    LaunchedEffect(analyzeError) {
        analyzeError?.let { error ->
            Toast.makeText(context, "$analysisFailedText: $error", Toast.LENGTH_LONG).show()
            contractViewModel.clearSaveState()
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background((Color.White))
                .padding(16.dp),
            horizontalAlignment = Alignment.Start
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Box(modifier = Modifier.fillMaxWidth()) {
                    Image(
                        painter = painterResource(id = R.drawable.typo_logo_blue),
                        contentDescription = "typo_logo_blue",
                        modifier = Modifier
                            .size(200.dp)
                            .offset(y = (-50).dp, x = (-20).dp)
                    )
                    Text(
                        text = stringResource(R.string.edit_contract_description),
                        fontSize = 14.sp,
                        style = MaterialTheme.typography.bodyLarge,
                        textAlign = TextAlign.Start,
                        modifier = Modifier
                            .padding(top = 4.dp, start = 16.dp, bottom = 10.dp)
                            .offset(y = 70.dp)
                    )
                }
                Spacer(modifier = Modifier.height(30.dp))
                Card(
                    modifier = Modifier
                        .wrapContentWidth()
                        .wrapContentHeight()
                        .offset(y = (-70).dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
                ) {
                    Box(modifier = Modifier.padding(16.dp)) {

                        if (contract != null) {
                            ResultFromOcr(
                                contract = contract,
                                onDataChange = { updatedContract ->
                                    contractViewModel.updateEditedContract(updatedContract)
                                },
                                onSaveClick = {
                                    if (uid.isNotEmpty() && token.isNotEmpty()) {
                                        contractViewModel.saveAnalysis(
                                            contractId = contractId,
                                            userId = uid,
                                            token = token,
                                            userLanguage = userLanguage,
                                            context = context
                                        )
                                    } else {
                                        Toast.makeText(context, loginInfoMissingText, Toast.LENGTH_SHORT).show()
                                    }
                                },
                                isSaving = isSaving,
                                isAnalyzing = isAnalyzing,
                                navController = navController,
                                contractViewModel = contractViewModel,
                                loadingViewModel = loadingViewModel
                            )
                        } else {
                            Text(stringResource(R.string.no_contract_info))
                        }
                    }
                }
            }
        }
    }
}

