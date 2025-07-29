package com.taba.lawro.navigation.analyze

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ExpandLess
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.taba.lawro.R
import com.taba.lawro.data_class.AnalyzeRequest
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch


@Composable
fun ResultFromOcr(
    contract: AnalyzeRequest, 
    modifier: Modifier = Modifier,
    onDataChange: (AnalyzeRequest) -> Unit = {},
    onSaveClick: () -> Unit = {},
    isSaving: Boolean = false,
    isAnalyzing: Boolean = false,
    navController: androidx.navigation.NavController? = null,
    contractViewModel: com.taba.lawro.viewmodel.ContractViewModel? = null,
    loadingViewModel: com.taba.lawro.viewmodel.LoadingViewModel? = null
) {
    val context = LocalContext.current // Context를 미리 캡처
    val expandedSections = remember { mutableStateMapOf<String, Boolean>() }
    
    // 편집 가능한 상태로 계약서 데이터 관리
    var editedContract by remember { mutableStateOf(contract) }
    
    // 데이터 변경 시 상위로 알림
    LaunchedEffect(editedContract) {
        onDataChange(editedContract)
    }

    // 데이터 업데이트 헬퍼 함수들
    fun updateEmployer(update: (com.taba.lawro.data_class.Employer?) -> com.taba.lawro.data_class.Employer?) {
        editedContract = editedContract.copy(employer = update(editedContract.employer))
    }
    
    fun updateEmployee(update: (com.taba.lawro.data_class.Employee?) -> com.taba.lawro.data_class.Employee?) {
        editedContract = editedContract.copy(employee = update(editedContract.employee))
    }
    
    fun updateContractPeriod(update: (com.taba.lawro.data_class.ContractPeriod?) -> com.taba.lawro.data_class.ContractPeriod?) {
        editedContract = editedContract.copy(contractPeriod = update(editedContract.contractPeriod))
    }
    
    fun updateJobDetails(update: (com.taba.lawro.data_class.JobDetails?) -> com.taba.lawro.data_class.JobDetails?) {
        editedContract = editedContract.copy(jobDetails = update(editedContract.jobDetails))
    }
    
    fun updateWorkingHours(update: (com.taba.lawro.data_class.WorkingHours?) -> com.taba.lawro.data_class.WorkingHours?) {
        editedContract = editedContract.copy(workingHours = update(editedContract.workingHours))
    }
    
    fun updateWages(update: (com.taba.lawro.data_class.Wages?) -> com.taba.lawro.data_class.Wages?) {
        editedContract = editedContract.copy(wages = update(editedContract.wages))
    }
    
    fun updateAccommodation(update: (com.taba.lawro.data_class.Accommodation?) -> com.taba.lawro.data_class.Accommodation?) {
        editedContract = editedContract.copy(accommodation = update(editedContract.accommodation))
    }
    
    fun updateHolidaysAndVacations(update: (com.taba.lawro.data_class.HolidaysAndVacations?) -> com.taba.lawro.data_class.HolidaysAndVacations?) {
        editedContract = editedContract.copy(holidaysAndVacations = update(editedContract.holidaysAndVacations))
    }
    
    fun updatePayment(update: (com.taba.lawro.data_class.Payment?) -> com.taba.lawro.data_class.Payment?) {
        editedContract = editedContract.copy(payment = update(editedContract.payment))
    }
    
    fun updateFourMajorInsurances(update: (com.taba.lawro.data_class.FourMajorInsurances?) -> com.taba.lawro.data_class.FourMajorInsurances?) {
        editedContract = editedContract.copy(fourMajorInsurances = update(editedContract.fourMajorInsurances))
    }
    
    fun updateSignatureDate(update: (com.taba.lawro.data_class.SignatureDate?) -> com.taba.lawro.data_class.SignatureDate?) {
        editedContract = editedContract.copy(signatureDate = update(editedContract.signatureDate))
    }

    LazyColumn(
        modifier = modifier
            .wrapContentWidth()
            .padding(12.dp)
    ) {
        item {
            ExpandableSection(
                title = stringResource(R.string.employer_info),
                expanded = expandedSections.getOrElse("employer") { false },
                onExpandToggle = {
                    expandedSections["employer"] = !expandedSections.getOrElse("employer") { false }
                }
            ) {
                LabeledTextField(
                    stringResource(R.string.company_name), 
                    editedContract.employer?.companyName ?: ""
                ) { newValue ->
                    updateEmployer { it?.copy(companyName = newValue) ?: com.taba.lawro.data_class.Employer(companyName = newValue, null, null, null, null) }
                }
                LabeledTextField(
                    stringResource(R.string.phone_number), 
                    editedContract.employer?.phoneNumber ?: ""
                ) { newValue ->
                    updateEmployer { it?.copy(phoneNumber = newValue) ?: com.taba.lawro.data_class.Employer(null, phoneNumber = newValue, null, null, null) }
                }
                LabeledTextField(
                    stringResource(R.string.address), 
                    editedContract.employer?.address ?: ""
                ) { newValue ->
                    updateEmployer { it?.copy(address = newValue) ?: com.taba.lawro.data_class.Employer(null, null, address = newValue, null, null) }
                }
                LabeledTextField(
                    stringResource(R.string.representative_name), 
                    editedContract.employer?.representativeName ?: ""
                ) { newValue ->
                    updateEmployer { it?.copy(representativeName = newValue) ?: com.taba.lawro.data_class.Employer(null, null, null, representativeName = newValue, null) }
                }
                LabeledTextField(
                    stringResource(R.string.business_registration_number), 
                    editedContract.employer?.businessRegistrationNumber ?: ""
                ) { newValue ->
                    updateEmployer { it?.copy(businessRegistrationNumber = newValue) ?: com.taba.lawro.data_class.Employer(null, null, null, null, businessRegistrationNumber = newValue) }
                }
            }
        }

        item {
            ExpandableSection(
                title = stringResource(R.string.employee_info),
                expanded = expandedSections.getOrElse("employee") { false },
                onExpandToggle = {
                    expandedSections["employee"] = !expandedSections.getOrElse("employee") { false }
                }
            ) {
                LabeledTextField(
                    stringResource(R.string.name), 
                    editedContract.employee?.name ?: ""
                ) { newValue ->
                    updateEmployee { it?.copy(name = newValue) ?: com.taba.lawro.data_class.Employee(name = newValue, null, null) }
                }
                LabeledTextField(
                    stringResource(R.string.birth_date), 
                    editedContract.employee?.birthDate ?: ""
                ) { newValue ->
                    updateEmployee { it?.copy(birthDate = newValue) ?: com.taba.lawro.data_class.Employee(null, birthDate = newValue, null) }
                }
                LabeledTextField(
                    stringResource(R.string.home_address), 
                    editedContract.employee?.homeAddress ?: ""
                ) { newValue ->
                    updateEmployee { it?.copy(homeAddress = newValue) ?: com.taba.lawro.data_class.Employee(null, null, homeAddress = newValue) }
                }
            }
        }

        item {
            ExpandableSection(
                title = stringResource(R.string.work_conditions),
                expanded = expandedSections.getOrElse("contract") { false },
                onExpandToggle = {
                    expandedSections["contract"] = !expandedSections.getOrElse("contract") { false }
                }
            ) {
                LabeledTextField(stringResource(R.string.contract_period), editedContract.contractPeriod?.newContractMonths+"개월" ?: "")
                LabeledTextField(stringResource(R.string.workplace), editedContract.workplace ?: "")
                LabeledTextField(stringResource(R.string.work_start_date), editedContract.contractPeriod?.workplaceChangePeriod?.startDate ?: "")
                LabeledTextField(stringResource(R.string.work_end_date), editedContract.contractPeriod?.workplaceChangePeriod?.endDate ?: "")
                EditableBooleanField(stringResource(R.string.probation_status), editedContract.contractPeriod?.probation?.inUse ?: false) { newValue ->
                    updateContractPeriod { contractPeriod ->
                        contractPeriod?.copy(
                            probation = contractPeriod.probation?.copy(inUse = newValue) 
                                ?: com.taba.lawro.data_class.Probation(inUse = newValue, null)
                        ) ?: com.taba.lawro.data_class.ContractPeriod(
                            null,
                            null,
                            com.taba.lawro.data_class.Probation(inUse = newValue, null)
                        )
                    }
                }
                LabeledTextField(stringResource(R.string.probation_period), editedContract.contractPeriod?.probation?.months ?: "")
            }
        }

        item {
            ExpandableSection(
                title = stringResource(R.string.job_details),
                expanded = expandedSections.getOrElse("job") { false },
                onExpandToggle = {
                    expandedSections["job"] = !expandedSections.getOrElse("job") { false }
                }
            ) {
                LabeledTextField(stringResource(R.string.industry), editedContract.jobDetails?.industry ?: "")
                LabeledTextField(stringResource(R.string.business_content), editedContract.jobDetails?.businessContent ?: "")
                LabeledTextField(stringResource(R.string.job_content), editedContract.jobDetails?.jobContent ?: "")
            }
        }

        item {
            ExpandableSection(
                title = stringResource(R.string.working_hours),
                expanded = expandedSections.getOrElse("hours") { false },
                onExpandToggle = {
                    expandedSections["hours"] = !expandedSections.getOrElse("hours") { false }
                }
            ) {
                LabeledTextField(stringResource(R.string.start_time), editedContract.workingHours?.startTime ?: "")
                LabeledTextField(stringResource(R.string.end_time), editedContract.workingHours?.endTime ?: "")
                LabeledTextField(stringResource(R.string.overtime_hours), editedContract.workingHours?.overtimeHours ?: "")
                LabeledTextField(stringResource(R.string.shift_work_status), editedContract.workingHours?.shiftWork ?: "")
                LabeledTextField(stringResource(R.string.break_time), editedContract.dailyBreakMinutes ?: "")
            }
        }

        item {
            ExpandableSection(
                title = stringResource(R.string.wage_info),
                expanded = expandedSections.getOrElse("wage") { false },
                onExpandToggle = {
                    expandedSections["wage"] = !expandedSections.getOrElse("wage") { false }
                }
            ) {
                LabeledTextField(stringResource(R.string.total_payment), editedContract.wages?.monthlyTotal ?: "")
                LabeledTextField(stringResource(R.string.base_salary), editedContract.wages?.baseSalary ?: "")
                editedContract.wages?.allowances?.forEach {
                    LabeledTextField(stringResource(R.string.allowance) + " - ${it.item ?: ""}", it.amount ?: "")
                }
                LabeledTextField(stringResource(R.string.bonus), editedContract.wages?.bonus ?: "")
                LabeledTextField(stringResource(R.string.probation_salary), editedContract.wages?.probationSalary ?: "")
                LabeledTextField(stringResource(R.string.extra_pay_rate), editedContract.wages?.extraPayRate ?: "")
            }
        }

        item {
            ExpandableSection(
                title = stringResource(R.string.accommodation_and_meal),
                expanded = expandedSections.getOrElse("housing") { false },
                onExpandToggle = {
                    expandedSections["housing"] = !expandedSections.getOrElse("housing") { false }
                }
            ) {
                EditableBooleanField(stringResource(R.string.housing_provided), editedContract.accommodation?.provided ?: false) { newValue ->
                    updateAccommodation { accommodation ->
                        accommodation?.copy(provided = newValue) 
                            ?: com.taba.lawro.data_class.Accommodation(provided = newValue, null, null, null, null, null)
                    }
                }
                LabeledTextField(stringResource(R.string.housing_type), editedContract.accommodation?.types?.joinToString() ?: "")
                LabeledTextField(stringResource(R.string.employee_housing_cost), editedContract.accommodation?.employeeHousingCost ?: "")
                EditableBooleanField(stringResource(R.string.meal_provided), editedContract.accommodation?.mealsProvided ?: false) { newValue ->
                    updateAccommodation { accommodation ->
                        accommodation?.copy(mealsProvided = newValue) 
                            ?: com.taba.lawro.data_class.Accommodation(null, null, null, mealsProvided = newValue, null, null)
                    }
                }
                LabeledTextField(stringResource(R.string.meal_type), editedContract.accommodation?.mealTypes?.joinToString() ?: "")
                LabeledTextField(stringResource(R.string.employee_meal_cost), editedContract.accommodation?.employeeMealCost ?: "")
            }
        }

        item {
            ExpandableSection(
                title = stringResource(R.string.holiday_and_vacation),
                expanded = expandedSections.getOrElse("holiday") { false },
                onExpandToggle = {
                    expandedSections["holiday"] = !expandedSections.getOrElse("holiday") { false }
                }
            ) {
                EditableBooleanField(stringResource(R.string.sunday), editedContract.holidaysAndVacations?.sunday ?: false) { newValue ->
                    updateHolidaysAndVacations { holidays ->
                        holidays?.copy(sunday = newValue) 
                            ?: com.taba.lawro.data_class.HolidaysAndVacations(sunday = newValue, null, null)
                    }
                }
                EditableBooleanField(stringResource(R.string.public_holiday_paid), editedContract.holidaysAndVacations?.publicHolidays?.paid ?: false) { newValue ->
                    updateHolidaysAndVacations { holidays ->
                        holidays?.copy(
                            publicHolidays = holidays.publicHolidays?.copy(paid = newValue) 
                                ?: com.taba.lawro.data_class.PublicHolidays(paid = newValue, null)
                        ) ?: com.taba.lawro.data_class.HolidaysAndVacations(
                            null,
                            com.taba.lawro.data_class.PublicHolidays(paid = newValue, null),
                            null
                        )
                    }
                }
                EditableBooleanField(stringResource(R.string.public_holiday_unpaid), editedContract.holidaysAndVacations?.publicHolidays?.unpaid ?: false) { newValue ->
                    updateHolidaysAndVacations { holidays ->
                        holidays?.copy(
                            publicHolidays = holidays.publicHolidays?.copy(unpaid = newValue) 
                                ?: com.taba.lawro.data_class.PublicHolidays(null, unpaid = newValue)
                        ) ?: com.taba.lawro.data_class.HolidaysAndVacations(
                            null,
                            com.taba.lawro.data_class.PublicHolidays(null, unpaid = newValue),
                            null
                        )
                    }
                }
                LabeledTextField(stringResource(R.string.saturday), editedContract.holidaysAndVacations?.saturday ?: "")
            }
        }

        item {
            ExpandableSection(
                title = stringResource(R.string.payment_method),
                expanded = expandedSections.getOrElse("payment") { false },
                onExpandToggle = {
                    expandedSections["payment"] = !expandedSections.getOrElse("payment") { false }
                }
            ) {
                LabeledTextField(stringResource(R.string.payday), editedContract.payment?.payday ?: "")
                LabeledTextField(stringResource(R.string.method), editedContract.payment?.method ?: "")
                EditableBooleanField(stringResource(R.string.employer_controls_account), editedContract.payment?.employerControlsAccount ?: false) { newValue ->
                    updatePayment { payment ->
                        payment?.copy(employerControlsAccount = newValue) 
                            ?: com.taba.lawro.data_class.Payment(null, null, employerControlsAccount = newValue)
                    }
                }
            }
        }
        item {
            ExpandableSection(
                title = stringResource(R.string.four_major_insurances),
                expanded = expandedSections.getOrElse("insurance") { false },
                onExpandToggle = {
                    expandedSections["insurance"] = !expandedSections.getOrElse("insurance") { false }
                }
            ) {
                EditableBooleanField(stringResource(R.string.health_insurance), editedContract.fourMajorInsurances?.healthInsurance ?: false) { newValue ->
                    updateFourMajorInsurances { insurance ->
                        insurance?.copy(healthInsurance = newValue) 
                            ?: com.taba.lawro.data_class.FourMajorInsurances(healthInsurance = newValue, null, null, null)
                    }
                }
                EditableBooleanField(stringResource(R.string.national_pension), editedContract.fourMajorInsurances?.nationalPension ?: false) { newValue ->
                    updateFourMajorInsurances { insurance ->
                        insurance?.copy(nationalPension = newValue) 
                            ?: com.taba.lawro.data_class.FourMajorInsurances(null, nationalPension = newValue, null, null)
                    }
                }
                EditableBooleanField(stringResource(R.string.employment_insurance), editedContract.fourMajorInsurances?.employmentInsurance ?: false) { newValue ->
                    updateFourMajorInsurances { insurance ->
                        insurance?.copy(employmentInsurance = newValue) 
                            ?: com.taba.lawro.data_class.FourMajorInsurances(null, null, employmentInsurance = newValue, null)
                    }
                }
                EditableBooleanField(stringResource(R.string.industrial_accident_insurance), editedContract.fourMajorInsurances?.industrialAccidentInsurance ?: false) { newValue ->
                    updateFourMajorInsurances { insurance ->
                        insurance?.copy(industrialAccidentInsurance = newValue) 
                            ?: com.taba.lawro.data_class.FourMajorInsurances(null, null, null, industrialAccidentInsurance = newValue)
                    }
                }
            }
        }

        item {
            ExpandableSection(
                title = stringResource(R.string.other_clauses),
                expanded = expandedSections.getOrElse("other") { false },
                onExpandToggle = {
                    expandedSections["other"] = !expandedSections.getOrElse("other") { false }
                }
            ) {
                EditableBooleanField(stringResource(R.string.contract_rules_compliance), editedContract.contractAndRulesCompliance ?: false) { newValue ->
                    editedContract = editedContract.copy(contractAndRulesCompliance = newValue)
                }
                LabeledTextField(stringResource(R.string.other_terms), editedContract.otherTerms ?: "")
            }
        }

        item {
            ExpandableSection(
                title = stringResource(R.string.signature_info),
                expanded = expandedSections.getOrElse("signature") { false },
                onExpandToggle = {
                    expandedSections["signature"] = !expandedSections.getOrElse("signature") { false }
                }
            ) {
                LabeledTextField(
                    label = stringResource(R.string.employer_signature), 
                    value = editedContract.signatureDate?.employerSignature ?: "",
                    onValueChange = { newValue ->
                        updateSignatureDate { signatureDate ->
                            signatureDate?.copy(employerSignature = newValue) 
                                ?: com.taba.lawro.data_class.SignatureDate(employerSignature = newValue, null, null)
                        }
                    }
                )
                LabeledTextField(
                    label = stringResource(R.string.employee_signature), 
                    value = editedContract.signatureDate?.employeeSignature ?: "",
                    onValueChange = { newValue ->
                        updateSignatureDate { signatureDate ->
                            signatureDate?.copy(employeeSignature = newValue) 
                                ?: com.taba.lawro.data_class.SignatureDate(null, employeeSignature = newValue, null)
                        }
                    }
                )
                LabeledTextField(
                    label = stringResource(R.string.signature_date), 
                    value = editedContract.signatureDate?.date ?: "",
                    onValueChange = { newValue ->
                        updateSignatureDate { signatureDate ->
                            signatureDate?.copy(date = newValue) 
                                ?: com.taba.lawro.data_class.SignatureDate(null, null, date = newValue)
                        }
                    }
                )
            }
        }

        item {
            Spacer(modifier = Modifier.height(24.dp))
            Button(
                onClick = {
                    loadingViewModel?.setLoading(true) // 전체 화면 로딩 시작
                    // 40초 후에 분석 결과 생성 및 화면 이동
                    CoroutineScope(Dispatchers.Main).launch {
                        delay(40000) // 40초 대기
                        contractViewModel?.setNewDummyAnalysisResult(context)
                        loadingViewModel?.setLoading(false) // 전체 화면 로딩 끝
                        navController?.navigate("new_analysis_result")
                    }
                },
                enabled = !isSaving && !isAnalyzing,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 12.dp)
            ) {
                if (isSaving) {
                    CircularProgressIndicator(modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(stringResource(R.string.saving))
                } else if (isAnalyzing) {
                    CircularProgressIndicator(modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(stringResource(R.string.analyzing))
                } else {
                    Text(stringResource(R.string.edit_complete))
                }
            }
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

@Composable
fun ExpandableSection(
    title: String,
    expanded: Boolean,
    onExpandToggle: () -> Unit,
    content: @Composable ColumnScope.() -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        elevation = CardDefaults.cardElevation(4.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { onExpandToggle() },
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(text = title, fontWeight = FontWeight.Bold, modifier = Modifier.weight(1f))
                Icon(
                    imageVector = if (expanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                    contentDescription = null
                )
            }
            if (expanded) {
                Spacer(modifier = Modifier.height(8.dp))
                content()
            }
        }
    }
}

@Composable
fun LabeledTextField(
    label: String, 
    value: String,
    onValueChange: (String) -> Unit = {}
) {
    var text by remember { mutableStateOf(value) }

    // 값이 변경될 때마다 상위로 알림
    LaunchedEffect(text) {
        onValueChange(text)
    }

    Column(modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp)) {
        Text(
            text = label,
            fontWeight = FontWeight.Bold,
            fontSize = 14.sp,
            modifier = Modifier.padding(bottom = 4.dp)
        )
        Surface(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            shadowElevation = 4.dp,
            color = Color.White
        ) {
            TextField(
                value = text,
                textStyle = LocalTextStyle.current.copy(fontSize = 12.sp),
                onValueChange = { text = it },
                placeholder = { Text(label, color = Color.Gray) },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 12.dp),
                colors = TextFieldDefaults.colors(
                    focusedIndicatorColor = Color.Transparent,
                    unfocusedIndicatorColor = Color.Transparent,
                    disabledIndicatorColor = Color.Transparent,
                    focusedContainerColor = Color.White,
                    unfocusedContainerColor = Color.White
                ),
                singleLine = true
            )
        }
    }
}

@Composable
fun EditableBooleanField(label: String, value: Boolean, onValueChange: (Boolean) -> Unit) {
    Column(modifier = Modifier.padding(vertical = 4.dp)) {
        Text(text = label,
            fontWeight = FontWeight.SemiBold,
            fontSize = 14.sp,
            modifier =
            Modifier.padding(start= 4.dp, bottom = 4.dp))
        Row {
            listOf(stringResource(R.string.yes) to true, stringResource(R.string.no) to false).forEach { (text, boolValue) ->
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier
                        .padding(end = 16.dp)
                        .clickable { onValueChange(boolValue) }
                ) {
                    RadioButton(
                        selected = value == boolValue,
                        onClick = { onValueChange(boolValue) }
                    )
                    Text(text = text)
                }
            }
        }
    }
}


