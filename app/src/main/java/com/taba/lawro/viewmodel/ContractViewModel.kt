package com.taba.lawro.viewmodel

import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.taba.lawro.data_class.AnalyzeRequest
import com.taba.lawro.data_class.AnalyzeWithChatbotRequest
import com.taba.lawro.data_class.AnalysisResultResponse
import com.taba.lawro.data_class.SaveAnalysisRequest
import com.taba.lawro.data_class.NewAnalysisResponse
import com.taba.lawro.data_class.LegalInterpretationItem
import com.taba.lawro.data_class.SavedAnalysisResult
import android.content.Context
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.taba.lawro.network.RetrofitClient
import kotlinx.coroutines.launch
import com.google.gson.GsonBuilder
import com.taba.lawro.R
import android.app.Application
import androidx.lifecycle.AndroidViewModel
import com.taba.lawro.data_class.*
import com.taba.lawro.selectLanguage.LanguageManager

class ContractViewModel(application: Application) : AndroidViewModel(application) {
    // 언어 설정이 적용된 Context를 사용하기 위해 기본 Context는 제거
    // private val context: Context = application.applicationContext
    
    private val _contract = mutableStateOf<AnalyzeRequest?>(null)
    val contract: State<AnalyzeRequest?> = _contract

    private val _editedContract = mutableStateOf<AnalyzeRequest?>(null)
    val editedContract: State<AnalyzeRequest?> = _editedContract

    // 실제 서버에서 받은 contract_id 저장
    private val _contractId = mutableStateOf<String?>(null)
    val contractId: State<String?> = _contractId

    private val _isSaving = mutableStateOf(false)
    val isSaving: State<Boolean> = _isSaving

    private val _saveError = mutableStateOf<String?>(null)
    val saveError: State<String?> = _saveError

    private val _saveSuccess = mutableStateOf(false)
    val saveSuccess: State<Boolean> = _saveSuccess

    // 분석 상태 추가
    private val _isAnalyzing = mutableStateOf(false)
    val isAnalyzing: State<Boolean> = _isAnalyzing

    private val _analyzeError = mutableStateOf<String?>(null)
    val analyzeError: State<String?> = _analyzeError

    private val _analyzeSuccess = mutableStateOf(false)
    val analyzeSuccess: State<Boolean> = _analyzeSuccess

    // 분석 결과 데이터 상태 추가 (기존)
    private val _analysisResult = mutableStateOf<AnalysisResultResponse?>(null)
    val analysisResult: State<AnalysisResultResponse?> = _analysisResult
    
    // 새로운 분석 결과 데이터 상태 추가
    private val _newAnalysisResult = mutableStateOf<NewAnalysisResponse?>(null)
    val newAnalysisResult: State<NewAnalysisResponse?> = _newAnalysisResult
    
    // 저장된 분석 결과 목록 상태 추가
    private val _savedAnalysisResults = mutableStateOf<List<SavedAnalysisResult>>(emptyList())
    val savedAnalysisResults: State<List<SavedAnalysisResult>> = _savedAnalysisResults
    
    // 현재 보고 있는 저장된 분석 결과 (과거 기록에서 선택한 것)
    private val _currentSavedResult = mutableStateOf<SavedAnalysisResult?>(null)
    val currentSavedResult: State<SavedAnalysisResult?> = _currentSavedResult

    fun setContract(data: AnalyzeRequest, contractId: String? = null) {
        _contract.value = data
        _editedContract.value = data // 초기 편집 데이터도 설정
        if (contractId != null) {
            _contractId.value = contractId
        }
        // 분석 상태 초기화
        _isAnalyzing.value = false
        _analyzeError.value = null
        _analyzeSuccess.value = false
    }

    fun updateEditedContract(data: AnalyzeRequest) {
        _editedContract.value = data
    }

    fun testServerConnection(context: Context) {
        viewModelScope.launch {
            try {
                android.util.Log.d("ContractViewModel", "=== 서버 연결 테스트 시작 ===")
                android.util.Log.d("ContractViewModel", "서버 URL: http://16.176.26.197:8000/")
                
                val response = RetrofitClient.apiService.healthCheck()
                
                android.util.Log.d("ContractViewModel", "헬스체크 응답 코드: ${response.code()}")
                android.util.Log.d("ContractViewModel", "헬스체크 성공 여부: ${response.isSuccessful}")
                android.util.Log.d("ContractViewModel", "헬스체크 메시지: ${response.message()}")
                android.util.Log.d("ContractViewModel", "헬스체크 본문: ${response.body()}")
                
                if (response.errorBody() != null) {
                    val errorBody = response.errorBody()?.string()
                    android.util.Log.e("ContractViewModel", "헬스체크 에러 본문: $errorBody")
                }
                
                if (response.isSuccessful) {
                    android.util.Log.d("ContractViewModel", "✅ 서버 연결 성공!")
                    _saveError.value = null
                } else {
                    android.util.Log.e("ContractViewModel", "❌ 서버 연결 실패: HTTP ${response.code()}")
                    _saveError.value = context.getString(R.string.server_connection_failed, response.code().toString())
                }
            } catch (e: Exception) {
                android.util.Log.e("ContractViewModel", "❌ 서버 연결 테스트 예외 발생", e)
                _saveError.value = context.getString(R.string.server_unavailable, e.message ?: "")
            }
        }
    }

    fun saveAnalysis(
        contractId: String,
        userId: String,
        token: String,
        userLanguage: String = "korean",
        context: Context
    ) {
        val contractData = _editedContract.value ?: return
        
        _isSaving.value = true
        _saveError.value = null
        _saveSuccess.value = false

        viewModelScope.launch {
            try {
                val request = SaveAnalysisRequest(
                    contractId = contractId,
                    userId = userId,
                    analysisResult = contractData
                )

                // 요청 로깅
                android.util.Log.d("ContractViewModel", "저장 요청 시작")
                android.util.Log.d("ContractViewModel", "Contract ID: $contractId")
                android.util.Log.d("ContractViewModel", "User ID: $userId")
                android.util.Log.d("ContractViewModel", "Token: Bearer ${token.take(10)}...")

                val gson = GsonBuilder().setPrettyPrinting().create()
                val requestJson = gson.toJson(request)
                android.util.Log.d("ContractViewModel", "=== 서버로 보내는 전체 JSON ===")
                android.util.Log.d("ContractViewModel", requestJson)
                android.util.Log.d("ContractViewModel", "=== JSON 끝 ===")

                val response = RetrofitClient.apiService.saveAnalysis(
                    token = "Bearer $token",
                    request = request
                )

                // 응답 로깅
                android.util.Log.d("ContractViewModel", "Response Code: ${response.code()}")
                android.util.Log.d("ContractViewModel", "Response Body: ${response.body()}")
                android.util.Log.d("ContractViewModel", "Response Error Body: ${response.errorBody()?.string()}")

                if (response.isSuccessful && response.body()?.success == true) {
                    android.util.Log.d("ContractViewModel", "저장 성공!")
                    _saveSuccess.value = true
                    // 원본 계약서도 업데이트
                    _contract.value = contractData
                    
                    // 서버 응답 메시지 확인
                    val responseMessage = response.body()?.message ?: ""
                    if (responseMessage.contains(context.getString(R.string.contract_analysis_saved_successfully))) {
                        // 저장 성공 후 자동으로 분석 API 호출
                        analyzeWithChatbot(contractId, userId, userLanguage, context)
                    }
                } else {
                    val errorMessage = if (response.isSuccessful) {
                        response.body()?.message ?: context.getString(R.string.server_failure_response)
                    } else {
                        context.getString(R.string.server_connection_failed, response.code().toString())
                    }
                    android.util.Log.e("ContractViewModel", "저장 실패: $errorMessage")
                    _saveError.value = errorMessage
                }
            } catch (e: Exception) {
                android.util.Log.e("ContractViewModel", "저장 중 예외 발생", e)
                _saveError.value = context.getString(R.string.network_error, e.message ?: "")
            } finally {
                _isSaving.value = false
            }
        }
    }

    // 챗봇 분석 API 호출
    private fun analyzeWithChatbot(
        contractId: String,
        userId: String,
        userLanguage: String,
        context: Context
    ) {
        _isAnalyzing.value = true
        _analyzeError.value = null
        _analyzeSuccess.value = false

        viewModelScope.launch {
            try {
                val request = AnalyzeWithChatbotRequest(
                    user_id = userId,
                    contract_id = contractId,
                    use_chatbot = true,
                    user_language = userLanguage,
                    use_saved_data = true
                )

                android.util.Log.d("ContractViewModel", "=== 챗봇 분석 요청 시작 ===")
                android.util.Log.d("ContractViewModel", "User ID: $userId")
                android.util.Log.d("ContractViewModel", "Contract ID: $contractId")
                android.util.Log.d("ContractViewModel", "User Language: $userLanguage")

                val response = RetrofitClient.apiService.analyzeWithChatbot(request)

                android.util.Log.d("ContractViewModel", "분석 응답 코드: ${response.code()}")
                android.util.Log.d("ContractViewModel", "분석 응답 본문: ${response.body()}")

                if (response.isSuccessful && response.body()?.success == true) {
                    android.util.Log.d("ContractViewModel", "챗봇 분석 성공!")
                    _analyzeSuccess.value = true
                    
                    // 실제 API 응답이 오면 여기서 파싱해서 저장
                    // 현재는 임시로 더미 데이터 생성
                    val dummyResult = AnalysisResultResponse(
                        success = true,
                        message = context.getString(R.string.analysis_complete),
                        contractTitle = context.getString(R.string.dummy_contract_title),
                        analysisDate = context.getString(R.string.dummy_analysis_date),
                        analysisResults = listOf(
                            com.taba.lawro.data_class.AnalysisResultItem(
                                type = "success",
                                message = context.getString(R.string.dummy_analysis_result_1)
                            ),
                            com.taba.lawro.data_class.AnalysisResultItem(
                                type = "warning", 
                                message = context.getString(R.string.dummy_analysis_result_2)
                            ),
                            com.taba.lawro.data_class.AnalysisResultItem(
                                type = "error",
                                message = context.getString(R.string.dummy_analysis_result_3)
                            )
                        )
                    )
                    _analysisResult.value = dummyResult
                } else {
                    val errorMessage = if (response.isSuccessful) {
                        response.body()?.message ?: context.getString(R.string.analysis_failure)
                    } else {
                        context.getString(R.string.server_connection_failed, response.code().toString())
                    }
                    android.util.Log.e("ContractViewModel", "챗봇 분석 실패: $errorMessage")
                    _analyzeError.value = errorMessage
                }
            } catch (e: Exception) {
                android.util.Log.e("ContractViewModel", "챗봇 분석 중 예외 발생", e)
                _analyzeError.value = context.getString(R.string.network_error, e.message ?: "")
            } finally {
                _isAnalyzing.value = false
            }
        }
    }

    fun clearSaveState() {
        _saveError.value = null
        _saveSuccess.value = false
        _analyzeError.value = null
        _analyzeSuccess.value = false
    }

    
    // 새로운 JSON 구조 더미 데이터 설정 함수 (Context 매개변수 버전)
    fun setNewDummyAnalysisResult(context: Context) {
        // 현재 계약서의 대표자명을 확인
        val representativeName = _editedContract.value?.employer?.representativeName
        
        android.util.Log.d("ContractViewModel", "🎯 발표용 분석결과 생성: 대표자명 = $representativeName")
        
        val dummyResult = when {
            representativeName?.contains("고길동") == true -> {
                // 패턴 A: 고길동 실제 분석결과
                createGoGilDongAnalysisResult()
            }
            representativeName?.contains("곽덕식") == true -> {
                // 패턴 B: 곽덕식 실제 분석결과  
                createKwakDeokSikAnalysisResult()
            }
            representativeName?.contains("옥두팔") == true -> {
                // 패턴 C: 옥두팔 분석결과 (추후 업데이트 예정)
                createOkDuPalAnalysisResult()
            }
            else -> {
                // 기본값: 고길동 분석결과 사용
                createGoGilDongAnalysisResult()
            }
        }
        
        _newAnalysisResult.value = dummyResult
        android.util.Log.d("ContractViewModel", "✅ 발표용 분석결과 생성 완료: ${dummyResult.aware}")
    }
    
    // 고길동 실제 분석결과 (제공받은 JSON 데이터)
    private fun createGoGilDongAnalysisResult(): NewAnalysisResponse {
        val app = getApplication<Application>()
        val savedLanguage = LanguageManager.getLanguage(app)
        val localizedContext = LanguageManager.updateContextLocale(app, savedLanguage)
        
        return NewAnalysisResponse(
            totalScore = 8.5,
            aware = "주의",
            summary = localizedContext.getString(R.string.go_gildong_summary),
            highlights = listOf(
                localizedContext.getString(R.string.go_gildong_highlight_1),
                localizedContext.getString(R.string.go_gildong_highlight_2),
                localizedContext.getString(R.string.go_gildong_highlight_3)
            ),
            legalInterpretation = listOf(
                LegalInterpretationItem(
                    issue = localizedContext.getString(R.string.go_gildong_legal_issue_1),
                    interpretation = localizedContext.getString(R.string.go_gildong_legal_interpretation_1)
                ),
                LegalInterpretationItem(
                    issue = localizedContext.getString(R.string.go_gildong_legal_issue_2),
                    interpretation = localizedContext.getString(R.string.go_gildong_legal_interpretation_2)
                ),
                LegalInterpretationItem(
                    issue = localizedContext.getString(R.string.go_gildong_legal_issue_3),
                    interpretation = localizedContext.getString(R.string.go_gildong_legal_interpretation_3)
                )
            ),
            deepAnalysis = localizedContext.getString(R.string.go_gildong_deep_analysis)
        )
    }
    
    // 곽덕식 실제 분석결과 (제공받은 JSON 데이터)
    private fun createKwakDeokSikAnalysisResult(): NewAnalysisResponse {
        val app = getApplication<Application>()
        val savedLanguage = LanguageManager.getLanguage(app)
        val localizedContext = LanguageManager.updateContextLocale(app, savedLanguage)
        
        return NewAnalysisResponse(
            totalScore = 6.5,
            aware = "주의",
            summary = localizedContext.getString(R.string.kwak_deoksik_summary),
            highlights = listOf(
                localizedContext.getString(R.string.kwak_deoksik_highlight_1),
                localizedContext.getString(R.string.kwak_deoksik_highlight_2),
                localizedContext.getString(R.string.kwak_deoksik_highlight_3)
            ),
            legalInterpretation = listOf(
                LegalInterpretationItem(
                    issue = localizedContext.getString(R.string.kwak_deoksik_legal_issue_1),
                    interpretation = localizedContext.getString(R.string.kwak_deoksik_legal_interpretation_1)
                ),
                LegalInterpretationItem(
                    issue = localizedContext.getString(R.string.kwak_deoksik_legal_issue_2),
                    interpretation = localizedContext.getString(R.string.kwak_deoksik_legal_interpretation_2)
                ),
                LegalInterpretationItem(
                    issue = localizedContext.getString(R.string.kwak_deoksik_legal_issue_3),
                    interpretation = localizedContext.getString(R.string.kwak_deoksik_legal_interpretation_3)
                )
            ),
            deepAnalysis = localizedContext.getString(R.string.kwak_deoksik_deep_analysis)
        )
    }
    
    // 옥두팔 분석결과 (추후 업데이트 예정 - 임시 데이터)
    private fun createOkDuPalAnalysisResult(): NewAnalysisResponse {
        val app = getApplication<Application>()
        val savedLanguage = LanguageManager.getLanguage(app)
        val localizedContext = LanguageManager.updateContextLocale(app, savedLanguage)
        
        return NewAnalysisResponse(
            totalScore = 13.5,
            aware = "위험",
            summary = localizedContext.getString(R.string.ok_dupal_summary),
            highlights = listOf(
                localizedContext.getString(R.string.ok_dupal_highlight_1),
                localizedContext.getString(R.string.ok_dupal_highlight_2),
                localizedContext.getString(R.string.ok_dupal_highlight_3)
            ),
            legalInterpretation = listOf(
                LegalInterpretationItem(
                    issue = localizedContext.getString(R.string.ok_dupal_legal_issue_1),
                    interpretation = localizedContext.getString(R.string.ok_dupal_legal_interpretation_1)
                ),
                LegalInterpretationItem(
                    issue = localizedContext.getString(R.string.ok_dupal_legal_issue_2),
                    interpretation = localizedContext.getString(R.string.ok_dupal_legal_interpretation_2)
                ),
                LegalInterpretationItem(
                    issue = localizedContext.getString(R.string.ok_dupal_legal_issue_3),
                    interpretation = localizedContext.getString(R.string.ok_dupal_legal_interpretation_3)
                )
            ),
            deepAnalysis = localizedContext.getString(R.string.ok_dupal_deep_analysis)
        )
    }
    
    // Context 없는 버전 - 언어 설정이 적용된 Context를 사용
    fun setNewDummyAnalysisResult() {
        val app = getApplication<Application>()
        val savedLanguage = LanguageManager.getLanguage(app)
        android.util.Log.d("ContractViewModel", "🌍 현재 설정된 언어: $savedLanguage")
        val localizedContext = LanguageManager.updateContextLocale(app, savedLanguage)
        android.util.Log.d("ContractViewModel", "🔄 언어 적용된 Context로 더미 데이터 생성")
        setNewDummyAnalysisResult(localizedContext)
    }
    
    // 분석 결과를 로컬에 저장
    fun saveAnalysisResultLocally(context: Context, title: String) {
        val currentResult = _newAnalysisResult.value
        val currentContract = _editedContract.value
        
        if (currentResult != null) {
            // 서명 날짜 추출 로직 개선
            val extractedSignatureDate = extractSignatureDateFromContract(currentContract, currentResult)
            
            val savedResult = SavedAnalysisResult(
                title = title,
                contractTitle = context.getString(R.string.contract_analysis_result),
                analysisDate = SavedAnalysisResult.getCurrentDate(),
                signatureDate = extractedSignatureDate,
                aware = currentResult.aware,
                totalScore = currentResult.totalScore,
                summary = currentResult.summary,
                highlights = currentResult.highlights,
                legalInterpretation = currentResult.legalInterpretation,
                deepAnalysis = currentResult.deepAnalysis
            )
            
            saveToSharedPreferences(context, savedResult)
            loadSavedAnalysisResults(context)
        }
    }
    
    // 계약서와 분석 결과에서 서명 날짜를 추출하는 함수
    private fun extractSignatureDateFromContract(
        contract: AnalyzeRequest?, 
        analysisResult: NewAnalysisResponse
    ): String? {
        // 1. 최우선: 사용자가 직접 수정한 계약서 데이터의 서명 날짜
        contract?.signatureDate?.date?.let { date ->
            if (date.isNotBlank() && date.trim().isNotEmpty()) {
                android.util.Log.d("ContractViewModel", "✅ 서명 날짜 추출: 사용자 입력 필드에서 = $date")
                return date.trim()
            }
        }
        
        android.util.Log.d("ContractViewModel", "⚠️ 사용자 입력 서명 날짜가 비어있음. 대체 방법 시도...")
        
        // 2. 차선책: 분석 결과 텍스트에서 서명 날짜 패턴 추출 (서버가 잘못 보낼 가능성 있음)
        val textSources = listOf(
            analysisResult.summary,
            analysisResult.deepAnalysis,
            analysisResult.highlights.joinToString(" ")
        )
        
        for (text in textSources) {
            extractDateFromText(text)?.let { extractedDate ->
                android.util.Log.d("ContractViewModel", "🔍 서명 날짜 추출: 텍스트 분석에서 = $extractedDate")
                return extractedDate
            }
        }
        
        // 3. 최후 수단: 현재 날짜 사용
        val currentDate = SavedAnalysisResult.getCurrentDate()
        android.util.Log.d("ContractViewModel", "🕒 서명 날짜 추출: 기본값(현재 날짜) = $currentDate")
        return currentDate
    }
    
    // 텍스트에서 날짜 패턴을 추출하는 함수
    private fun extractDateFromText(text: String): String? {
        if (text.isBlank()) return null
        
        // 다양한 날짜 패턴 정의
        val datePatterns = listOf(
            // "서명 날짜: 2024.01.15" 형태
            Regex("""서명\s*날짜\s*[:\s]\s*(\d{4})[.-/](\d{1,2})[.-/](\d{1,2})"""),
            Regex("""계약\s*날짜\s*[:\s]\s*(\d{4})[.-/](\d{1,2})[.-/](\d{1,2})"""),
            Regex("""체결\s*날짜\s*[:\s]\s*(\d{4})[.-/](\d{1,2})[.-/](\d{1,2})"""),
            
            // "2024년 1월 15일" 형태
            Regex("""(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일"""),
            
            // "2024.01.15", "2024-01-15", "2024/01/15" 형태
            Regex("""(\d{4})[.-/](\d{1,2})[.-/](\d{1,2})"""),
            
            // "01.15.2024", "01-15-2024" 형태 (미국식)
            Regex("""(\d{1,2})[.-/](\d{1,2})[.-/](\d{4})""")
        )
        
        for (pattern in datePatterns) {
            val matchResult = pattern.find(text)
            if (matchResult != null) {
                val groups = matchResult.groupValues
                
                return when {
                    // YYYY.MM.DD 형태 (첫 번째 그룹이 년도인 경우)
                    groups.size >= 4 && groups[1].length == 4 -> {
                        val year = groups[1]
                        val month = groups[2].padStart(2, '0')
                        val day = groups[3].padStart(2, '0')
                        "$year.$month.$day"
                    }
                    // MM.DD.YYYY 형태 (세 번째 그룹이 년도인 경우)
                    groups.size >= 4 && groups[3].length == 4 -> {
                        val year = groups[3]
                        val month = groups[1].padStart(2, '0')
                        val day = groups[2].padStart(2, '0')
                        "$year.$month.$day"
                    }
                    else -> null
                }
            }
        }
        
        return null
    }
    
    // SharedPreferences에 저장
    private fun saveToSharedPreferences(context: Context, result: SavedAnalysisResult) {
        val sharedPref = context.getSharedPreferences("saved_analysis_results", Context.MODE_PRIVATE)
        val gson = Gson()
        
        // 기존 결과들을 불러오기
        val existingResultsJson = sharedPref.getString("results_list", "[]")
        val type = object : TypeToken<MutableList<SavedAnalysisResult>>() {}.type
        val existingResults: MutableList<SavedAnalysisResult> = gson.fromJson(existingResultsJson, type) ?: mutableListOf()
        
        // 새 결과 추가
        existingResults.add(result)
        
        // 서명 날짜 기준으로 정렬 (최신순)
        existingResults.sortByDescending { savedResult ->
            val year = SavedAnalysisResult.getYearFromDate(savedResult.signatureDate)
            val fallbackDate = savedResult.signatureDate ?: savedResult.saveDate
            "${year}_${fallbackDate}"
        }
        
        // 다시 저장
        val updatedJson = gson.toJson(existingResults)
        with(sharedPref.edit()) {
            putString("results_list", updatedJson)
            apply()
        }
    }
    
    // 저장된 분석 결과들을 불러오기
    fun loadSavedAnalysisResults(context: Context) {
        val sharedPref = context.getSharedPreferences("saved_analysis_results", Context.MODE_PRIVATE)
        val gson = Gson()
        val existingResultsJson = sharedPref.getString("results_list", "[]")
        val type = object : TypeToken<List<SavedAnalysisResult>>() {}.type
        val results: List<SavedAnalysisResult> = gson.fromJson(existingResultsJson, type) ?: emptyList()
        
        // 서명 날짜 기준으로 정렬 (최신순)
        val sortedResults = results.sortedByDescending { savedResult ->
            val year = SavedAnalysisResult.getYearFromDate(savedResult.signatureDate)
            val fallbackDate = savedResult.signatureDate ?: savedResult.saveDate
            "${year}_${fallbackDate}"
        }
        
        _savedAnalysisResults.value = sortedResults
    }
    
    // 과거 기록에서 선택한 분석 결과 설정 (저장 버튼 없는 버전으로 보기용)
    fun setCurrentSavedResult(result: SavedAnalysisResult) {
        _currentSavedResult.value = result
        
        // 새 분석 결과 형태로 변환해서 기존 화면들에서 사용할 수 있도록 함
        val convertedResult = NewAnalysisResponse(
            totalScore = result.totalScore,
            aware = result.aware,
            summary = result.summary,
            highlights = result.highlights,
            legalInterpretation = result.legalInterpretation,
            deepAnalysis = result.deepAnalysis
        )
        _newAnalysisResult.value = convertedResult
    }
    
    // 현재 과거 기록을 보고 있는지 확인
    fun isViewingPastRecord(): Boolean = _currentSavedResult.value != null
    
    // 과거 기록 보기 모드 종료
    fun clearCurrentSavedResult() {
        _currentSavedResult.value = null
    }
    
    // 더미 데이터 추가 메서드 (발표용)
    fun addDummyAnalysisResult(dummyResult: SavedAnalysisResult) {
        val currentResults = _savedAnalysisResults.value.toMutableList()
        
        // 같은 ID의 더미 데이터가 이미 있는지 확인
        if (!currentResults.any { it.id == dummyResult.id }) {
            currentResults.add(dummyResult)
            
            // 서명 날짜 기준으로 정렬 (최신순)
            val sortedResults = currentResults.sortedByDescending { savedResult ->
                val year = SavedAnalysisResult.getYearFromDate(savedResult.signatureDate)
                val fallbackDate = savedResult.signatureDate ?: savedResult.saveDate
                "${year}_${fallbackDate}"
            }
            
            _savedAnalysisResults.value = sortedResults
        }
    }
}