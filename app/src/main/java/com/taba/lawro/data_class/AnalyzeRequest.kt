package com.taba.lawro.data_class

import com.google.gson.annotations.SerializedName

data class AnalyzeRequest(
    @SerializedName("employer") val employer: Employer?,
    @SerializedName("employee") val employee: Employee?,
    @SerializedName("contract_period") val contractPeriod: ContractPeriod?,
    @SerializedName("workplace") val workplace: String?,
    @SerializedName("job_details") val jobDetails: JobDetails?,
    @SerializedName("working_hours") val workingHours: WorkingHours?,
    @SerializedName("daily_break_minutes") val dailyBreakMinutes: String?,
    @SerializedName("holidays_and_leaves") val holidaysAndVacations: HolidaysAndVacations?,
    @SerializedName("wages") val wages: Wages?,
    @SerializedName("wage_payment") val payment: Payment?,
    @SerializedName("accommodation_meals") val accommodation: Accommodation?,
    @SerializedName("four_major_insurances") val fourMajorInsurances: FourMajorInsurances?,
    @SerializedName("contract_and_rules_compliance") val contractAndRulesCompliance: Boolean?,
    @SerializedName("other_terms") val otherTerms: String?,
    @SerializedName("signature_date") val signatureDate: SignatureDate?
)

data class Employer(
    @SerializedName("company_name") val companyName: String?,
    @SerializedName("phone_number") val phoneNumber: String?,
    @SerializedName("address") val address: String?,
    @SerializedName("representative_name") val representativeName: String?,
    @SerializedName("business_registration_number") val businessRegistrationNumber: String?
)

data class Employee(
    @SerializedName("name") val name: String?,
    @SerializedName("date_of_birth") val birthDate: String?,
    @SerializedName("home_country_address") val homeAddress: String?
)

data class ContractPeriod(
    @SerializedName("new_contract_months") val newContractMonths: String?,
    @SerializedName("workplace_change_period") val workplaceChangePeriod: WorkplaceChangePeriod?,
    @SerializedName("probation_period") val probation: Probation?
)

data class WorkplaceChangePeriod(
    @SerializedName("start_date") val startDate: String?,
    @SerializedName("end_date") val endDate: String?
)

data class Probation(
    @SerializedName("is_used") val inUse: Boolean?,
    @SerializedName("months") val months: String?
)

data class JobDetails(
    @SerializedName("industry") val industry: String?,
    @SerializedName("business_content") val businessContent: String?,
    @SerializedName("job_description") val jobContent: String?
)

data class WorkingHours(
    @SerializedName("start_time") val startTime: String?,
    @SerializedName("end_time") val endTime: String?,
    @SerializedName("overtime_hours") val overtimeHours: String?,
    @SerializedName("shift_work") val shiftWork: String?
)

data class HolidaysAndVacations(
    @SerializedName("sunday") val sunday: Boolean?,
    @SerializedName("legal_holidays") val publicHolidays: PublicHolidays?,
    @SerializedName("saturday") val saturday: String?
)

data class PublicHolidays(
    @SerializedName("paid") val paid: Boolean?,
    @SerializedName("unpaid") val unpaid: Boolean?
)

data class Wages(
    @SerializedName("monthly_total_wage") val monthlyTotal: String?,
    @SerializedName("base_pay") val baseSalary: String?,
    @SerializedName("allowances") val allowances: List<Allowance>?,
    @SerializedName("bonus") val bonus: String?,
    @SerializedName("probation_period_wage") val probationSalary: String?,
    @SerializedName("overtime_night_holiday_rate") val extraPayRate: String?
)

data class Allowance(
    @SerializedName("item") val item: String?,
    @SerializedName("amount") val amount: String?
)

data class Payment(
    @SerializedName("payment_date") val payday: String?,
    @SerializedName("payment_method") val method: String?,
    @SerializedName("employer_account_control") val employerControlsAccount: Boolean?
)

data class Accommodation(
    @SerializedName("accommodation_provided") val provided: Boolean?,
    @SerializedName("accommodation_types") val types: List<String>?,
    @SerializedName("employee_accommodation_fee") val employeeHousingCost: String?,
    @SerializedName("meals_provided") val mealsProvided: Boolean?,
    @SerializedName("provided_meals") val mealTypes: List<String>?,
    @SerializedName("employee_meal_fee") val employeeMealCost: String?
)

data class FourMajorInsurances(
    @SerializedName("health_insurance") val healthInsurance: Boolean?,
    @SerializedName("national_pension") val nationalPension: Boolean?,
    @SerializedName("employment_insurance") val employmentInsurance: Boolean?,
    @SerializedName("industrial_accident_insurance") val industrialAccidentInsurance: Boolean?
)

data class SignatureDate(
    @SerializedName("employer_signature") val employerSignature: String?,
    @SerializedName("employee_signature") val employeeSignature: String?,
    @SerializedName("date") val date: String?
)

// 분석 API 요청을 위한 데이터 클래스
data class AnalyzeApiRequest(
    val user_id: String,
    val contract_id: String
)

// 프로필 조회 응답을 위한 데이터 클래스
data class ProfileResponse(
    val success: Boolean,
    val user: UserProfile
)

data class UserProfile(
    @SerializedName("user_id") val userId: String,
    @SerializedName("email") val email: String,
    @SerializedName("full_name") val fullName: String,
    @SerializedName("created_at") val createdAt: String
)

// 계약서 저장 요청을 위한 데이터 클래스
data class SaveAnalysisRequest(
    @SerializedName("contract_id") val contractId: String,
    @SerializedName("user_id") val userId: String,
    @SerializedName("analysis_result") val analysisResult: AnalyzeRequest
)

// 계약서 저장 응답을 위한 데이터 클래스
data class SaveAnalysisResponse(
    @SerializedName("success") val success: Boolean,
    @SerializedName("message") val message: String,
    @SerializedName("contract_id") val contractId: String,
    @SerializedName("saved_at") val savedAt: String
)

// 서버 응답을 감싸는 래퍼 클래스
data class AnalyzeResponse(
    @SerializedName("message") val message: String?,
    @SerializedName("structured_result") val structuredResult: AnalyzeRequest?,
    @SerializedName("processing_info") val processingInfo: ProcessingInfo?
)

data class ProcessingInfo(
    @SerializedName("total_time") val totalTime: Double?,
    @SerializedName("ocr_time") val ocrTime: Double?,
    @SerializedName("parse_time") val parseTime: Double?,
    @SerializedName("image_count") val imageCount: Int?,
    @SerializedName("timestamp") val timestamp: Double?
)
