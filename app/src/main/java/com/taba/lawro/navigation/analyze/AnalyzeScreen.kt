package com.taba.lawro.navigation.analyze

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.net.Uri
import android.util.Log
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
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
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import androidx.navigation.NavController
import com.taba.lawro.R
import com.taba.lawro.data_class.UploadResponse
import com.taba.lawro.data_class.AnalyzeApiRequest
import com.taba.lawro.network.RetrofitClient
import com.taba.lawro.viewmodel.ContractViewModel
import com.taba.lawro.viewmodel.LoadingViewModel
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File

@Composable
fun AnalyzeScreen(
    uid : String,
    token : String,
    language : String,
    navController: NavController,
    contractViewModel: ContractViewModel,
    loadingViewModel: LoadingViewModel
) {
    // 새로운 분석을 시작할 때 과거 기록 모드 초기화
    contractViewModel.clearCurrentSavedResult()
    
    val context = LocalContext.current
    val imageUri = remember { mutableStateOf<Uri?>(null) }
    val cameraImageUri = remember { mutableStateOf<Uri?>(null) }
    val cameraPermissionGranted = remember { mutableStateOf(false) }
    val galleryLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            imageUri.value = it
            uploadImageToServer(context, it, uid, language, token, loadingViewModel, navController, contractViewModel)
        }
    }

    val cameraLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.TakePicture()
    ) { success ->
        Log.d("", "촬영 성공 여부: $success")
        Log.d("Camera", "촬영된 URI: ${cameraImageUri.value}")
        if (success) {
            cameraImageUri.value?.let { uri ->
                uploadImageToServer(context, uri, uid, language, token, loadingViewModel, navController, contractViewModel)
            }
        }
    }

    val cameraPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { granted ->
        cameraPermissionGranted.value = granted
        if (granted) {
            val uri = createImageFile(context, cameraImageUri)
            Log.d("Camera", "사진 저장될 URI: ${cameraImageUri.value}") //  반드시 여기 들어감
            uri?.let { cameraLauncher.launch(it) }
        }
    }
    Box(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.White)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.Start
        ) {
            Column(
                modifier = Modifier.fillMaxWidth(),
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
                        text = stringResource(id = R.string.analyze_title),
                        fontWeight = FontWeight.Bold,
                        fontSize = 20.sp,
                        style = MaterialTheme.typography.headlineMedium,
                        modifier = Modifier
                            .padding(top = 4.dp, start = 16.dp, bottom = 4.dp)
                            .offset(y = 80.dp)
                    )

                    Text(
                        text = stringResource(id = R.string.analyze_description),
                        fontSize = 14.sp,
                        style = MaterialTheme.typography.bodyLarge,
                        textAlign = TextAlign.Start,
                        modifier = Modifier
                            .padding(top = 4.dp, start = 16.dp, bottom = 10.dp)
                            .offset(y = 115.dp)
                    )
                }

                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 20.dp)
                        .height(360.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
                ) {
                    Box(
                        modifier = Modifier.fillMaxSize().padding(16.dp),
                        contentAlignment = Alignment.Center
                    ) {

                    }
                }

                Spacer(modifier = Modifier.height(32.dp))

                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = Color.Transparent)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalAlignment = Alignment.Start,
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Button(
                            onClick = { galleryLauncher.launch("image/*") },
                            modifier = Modifier.fillMaxWidth(),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = MaterialTheme.colorScheme.primaryContainer,
                                contentColor = MaterialTheme.colorScheme.onPrimaryContainer
                            )
                        ) {
                            Text(stringResource(id = R.string.photo_upload))
                        }

                        Button(
                            onClick = {
                                if (ContextCompat.checkSelfPermission(
                                        context,
                                        Manifest.permission.CAMERA
                                    ) == PackageManager.PERMISSION_GRANTED
                                ) {
                                    val uri = createImageFile(context, cameraImageUri)
                                    Log.d(
                                        "Camera",
                                        "사진 저장될 URI: ${cameraImageUri.value}"
                                    )
                                    uri?.let { cameraLauncher.launch(it) }
                                } else {
                                    cameraPermissionLauncher.launch(Manifest.permission.CAMERA)
                                }
                            },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(stringResource(id = R.string.photo_capture))
                        }
                    }
                }
            }
        }
    }
}

// 여러 이미지 업로드 함수 (백엔드 요청 형식에 맞춤)
fun uploadContractImages(
    context: Context,
    imageUris: List<Uri>,
    userId: String,
    contractId: String = "contract_${System.currentTimeMillis()}",
    language: String = "korean",
    loadingViewModel: LoadingViewModel,
    navController: NavController,
    contractViewModel: ContractViewModel
) {
    loadingViewModel.setLoading(true)
    val contentResolver = context.contentResolver
    
    val userIdBody = userId.toRequestBody("text/plain".toMediaTypeOrNull())
    val languageBody = language.toRequestBody("text/plain".toMediaTypeOrNull())
    val contractIdBody = contractId.toRequestBody("text/plain".toMediaTypeOrNull())
    
    val parts = imageUris.mapIndexed { index, uri ->
        val inputStream = contentResolver.openInputStream(uri)
        val requestFile = inputStream!!.readBytes().toRequestBody("image/*".toMediaTypeOrNull())
        MultipartBody.Part.createFormData("files", "contract_$index.jpg", requestFile)
    }
    
    Log.d("Upload", "여러 이미지 업로드 시작: userId=$userId, contractId=$contractId, 파일 수=${parts.size}")
    
    CoroutineScope(Dispatchers.IO).launch {
        try {
            val response = RetrofitClient.apiService.uploadContractMultiple(
                userId = userIdBody,
                language = languageBody,
                contractId = contractIdBody,
                files = parts
            )
            
            withContext(Dispatchers.Main) {
                if (response.isSuccessful) {
                    Log.d("Upload", "여러 이미지 업로드 성공: ${response.body()}")
                    val uploadResponse = response.body()
                    if (uploadResponse != null) {
                        Log.d("Upload", "Contract ID: ${uploadResponse.contract_id}")
                        Log.d("Upload", "Message: ${uploadResponse.message}")
                        Log.d("Upload", "S3 Keys: ${uploadResponse.s3_keys}")
                        Log.d("Upload", "File Count: ${uploadResponse.file_count}")
                        
                        // 업로드 성공 후 분석 API 호출
                        analyzeContractAfterUpload(
                            userId = userId,
                            contractId = uploadResponse.contract_id,
                            contractViewModel = contractViewModel,
                            navController = navController,
                            loadingViewModel = loadingViewModel
                        )
                    }else{
                        loadingViewModel.setLoading(false)
                    }
                } else {
                    loadingViewModel.setLoading(false)
                    Log.e("Upload", "여러 이미지 업로드 실패: ${response.code()} ${response.message()}")
                }
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                loadingViewModel.setLoading(false)
                Log.e("Upload", "여러 이미지 업로드 예외 발생: ${e.message}", e)
            }
        }
    }
}

//  파일 URI 생성 함수
fun createImageFile(context: Context, uriState: MutableState<Uri?>): Uri? {
    val file = File(context.cacheDir, "camera_capture_${System.currentTimeMillis()}.jpg")
    return FileProvider.getUriForFile(
        context,
        "${context.packageName}.provider",
        file
    ).also {
        uriState.value = it
    }
}

// 사진 전송 함수
fun uploadImageToServer(
    context: Context,
    uri: Uri,
    uid: String,
    language: String,
    token: String,
    loadingViewModel: LoadingViewModel,
    navController: NavController,
    contractViewModel: ContractViewModel
) {
    Log.d("Upload", "함수 진입 ")
    loadingViewModel.setLoading(true)
    val contentResolver = context.contentResolver
    
    // 파일의 실제 MIME 타입 확인
    val mimeType = contentResolver.getType(uri) ?: "image/jpeg"
    val fileExtension = when {
        mimeType.contains("png") -> "png"
        mimeType.contains("jpeg") || mimeType.contains("jpg") -> "jpg"
        else -> "jpg"
    }
    
    Log.d("Upload", "원본 파일 MIME 타입: $mimeType, 확장자: $fileExtension")
    
    val inputStream = contentResolver.openInputStream(uri)
    if (inputStream == null) {
        Log.e("Upload", "inputStream == null XX")
        loadingViewModel.setLoading(false)
        return
    }

    val file = File(context.cacheDir, "upload_${System.currentTimeMillis()}.$fileExtension")
    inputStream.use { input ->
        file.outputStream().use { output ->
            input.copyTo(output)
        }
    }

    Log.d("Upload", "파일 복사 완료 → ${file.absolutePath}")

    val userIdBody = uid.toRequestBody("text/plain".toMediaTypeOrNull())
    val languageBody = language.toRequestBody("text/plain".toMediaTypeOrNull())
    val contractId = "contract_${System.currentTimeMillis()}"
    val contractIdBody = contractId.toRequestBody("text/plain".toMediaTypeOrNull())
    
    // 백엔드 예시와 동일하게 파일 처리
    val inputStreamForUpload = contentResolver.openInputStream(uri)
    val fileBytes = inputStreamForUpload!!.readBytes()
    inputStreamForUpload.close()
    
    val requestFile = fileBytes.toRequestBody(mimeType.toMediaTypeOrNull())
    val filePart = MultipartBody.Part.createFormData("files", "contract_0.$fileExtension", requestFile)
    
    Log.d("Upload", "파일 정보: 크기=${requestFile.contentLength()} bytes, 이름=contract_0.$fileExtension")
    Log.d("Upload", "요청 파라미터: user_id=$uid, language=$language, contract_id=$contractId")
    Log.d("Upload", "MIME 타입: $mimeType")

    CoroutineScope(Dispatchers.IO).launch {
        try {
            val response = RetrofitClient.apiService.uploadContractNew(
                userId = userIdBody,
                language = languageBody,
                contractId = contractIdBody,
                files = filePart
            )
            withContext(Dispatchers.Main) {
                if (response.isSuccessful) {
                    Log.d("Upload", " 업로드 성공: ${response.body()}")
                    val uploadResponse = response.body()
                    if (uploadResponse != null) {
                        Log.d("Upload", "Contract ID: ${uploadResponse.contract_id}")
                        Log.d("Upload", "Message: ${uploadResponse.message}")
                        Log.d("Upload", "S3 Keys: ${uploadResponse.s3_keys}")
                        Log.d("Upload", "File Count: ${uploadResponse.file_count}")
                        
                        // 업로드 성공 후 분석 API 호출
                        analyzeContractAfterUpload(
                            userId = uid,
                            contractId = uploadResponse.contract_id,
                            contractViewModel = contractViewModel,
                            navController = navController,
                            loadingViewModel = loadingViewModel
                        )
                    }else{
                        loadingViewModel.setLoading(false)
                    }

                } else {
                    loadingViewModel.setLoading(false)
                    Log.e("Upload", " 업로드 실패: ${response.code()} ${response.message()}")
                }
            }
        } catch (e: Exception) {
            loadingViewModel.setLoading(false)
            Log.e("Upload", " 예외 발생: ${e.message}", e)
        }
    }
}

// 계약서 분석 함수
fun analyzeContractAfterUpload(
    userId: String,
    contractId: String,
    contractViewModel: ContractViewModel,
    navController: NavController,
    loadingViewModel: LoadingViewModel
) {
    Log.d("Analyze", "분석 시작: userId=$userId, contractId=$contractId")
    
    CoroutineScope(Dispatchers.IO).launch {
        try {
            val analyzeRequest = AnalyzeApiRequest(
                user_id = userId,
                contract_id = contractId
            )
            
            Log.d("Analyze", "분석 요청 데이터: $analyzeRequest")
            
            val response = RetrofitClient.apiService.analyzeContract(analyzeRequest)
            
            withContext(Dispatchers.Main) {
                // 응답 상세 로깅 추가
                Log.d("Analyze", "=== 분석 API 응답 상세 정보 ===")
                Log.d("Analyze", "Response Code: ${response.code()}")
                Log.d("Analyze", "Response Message: ${response.message()}")
                Log.d("Analyze", "Response Headers: ${response.headers()}")
                
                if (response.isSuccessful) {
                    val analyzeResponse = response.body()
                    
                    // 응답이 null이 아닌지 먼저 확인
                    Log.d("Analyze", "response.body() is null: ${analyzeResponse == null}")
                    
                    if (analyzeResponse != null) {
                        // 파싱된 결과 JSON 출력
                        val gson = com.google.gson.GsonBuilder().setPrettyPrinting().create()
                        val jsonString = gson.toJson(analyzeResponse)
                        Log.d("Analyze", "=== 파싱된 응답 JSON ===")
                        Log.d("Analyze", jsonString)
                        Log.d("Analyze", "=== 파싱된 응답 JSON 끝 ===")
                        
                        // structured_result에서 실제 계약서 데이터 추출
                        val analyzeResult = analyzeResponse.structuredResult
                        
                        Log.d("Analyze", "서버 메시지: ${analyzeResponse.message}")
                        Log.d("Analyze", "처리 정보: ${analyzeResponse.processingInfo}")
                        Log.d("Analyze", "실제 계약서 데이터: $analyzeResult")
                        
                        if (analyzeResult != null) {
                            // 각 필드별 null 체크
                            Log.d("Analyze", "employer: ${analyzeResult.employer}")
                            Log.d("Analyze", "employee: ${analyzeResult.employee}")
                            Log.d("Analyze", "contractPeriod: ${analyzeResult.contractPeriod}")
                            Log.d("Analyze", "workplace: ${analyzeResult.workplace}")
                            Log.d("Analyze", "jobDetails: ${analyzeResult.jobDetails}")
                            Log.d("Analyze", "workingHours: ${analyzeResult.workingHours}")
                            Log.d("Analyze", "wages: ${analyzeResult.wages}")
                            
                            // ContractViewModel에 분석 결과와 contract_id 설정
                            contractViewModel.setContract(analyzeResult, contractId)
                            Log.d("Analyze", "✅ 분석 성공! 로딩 화면 끄기")
                            // 로딩 끄기
                            loadingViewModel.setLoading(false)
                            Log.d("Analyze", "✅ 로딩 화면 꺼짐, EditContractScreen으로 이동")
                            // EditContractScreen으로 이동
                            navController.navigate("edit_contract")
                        } else {
                            Log.e("Analyze", "❌ structured_result가 null입니다")
                            loadingViewModel.setLoading(false)
                        }
                    } else {
                        Log.e("Analyze", "응답 전체가 null입니다")
                        loadingViewModel.setLoading(false)
                    }
                } else {
                    // 에러 응답도 상세히 로깅
                    val errorBody = response.errorBody()?.string()
                    Log.e("Analyze", "분석 실패: ${response.code()} ${response.message()}")
                    Log.e("Analyze", "Error Body: $errorBody")
                    loadingViewModel.setLoading(false)
                }
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                loadingViewModel.setLoading(false)
                Log.e("Analyze", "분석 예외 발생: ${e.message}", e)
            }
        }
    }
}