# LawRo 분류 체계 가이드 v1.2

`v1.yaml` 의 각 라벨을 **어떻게 붙이는지**에 대한 기준이다.
사람 라벨링(골든셋)과 LLM 추출 프롬프트가 이 문서를 같은 기준으로 쓴다.
기준이 바뀌면 `v1.yaml` 과 이 문서를 함께 고치고 버전을 올린다 (§9).

---

## 1. 목적과 범위

LawRo 에 들어오는 세 종류의 콘텐츠를 **하나의 분류 체계**로 표현한다.

| content_type | 예 | 쓰임 |
|---|---|---|
| `query` | "사장이 기숙사비를 월급에서 빼요" | 검색 필터, 지원센터·FAQ 추천, 긴급 상담 우선 처리 |
| `contract_clause` | "무단 퇴사 시 위약금 100만원" | 위험 조항 탐지, 관련 조문 연결 |
| `law_article` | 근로기준법 제43조(임금 지급) | 검색 대상 문서에 카테고리 메타데이터 부여 |

세 종류가 같은 라벨을 쓰기 때문에 "질문의 카테고리 = 조문의 카테고리"로 검색 범위를 좁힐 수 있다.
이것이 분류 체계를 콘텐츠 종류별로 따로 두지 않은 이유다.

---

## 2. 설계 결정

### D1. 카테고리는 "법적 쟁점" 기준으로 나눈다 (키워드·법령 기준이 아니다)
- 같은 "기숙사"라는 단어라도 "기숙사비를 월급에서 빼도 되나"는 **임금 전액지급 원칙**(근로기준법 제43조)의 문제이고,
  "기숙사에 화장실이 없다"는 **기숙사 시설 기준**(제100조)의 문제다. 답을 찾을 조문이 다르면 다른 라벨이어야 한다.
- 법령 단위로 나누지 않은 이유: 근로기준법 하나에 임금·근로시간·해고·기숙사가 모두 들어 있어, 법령 단위로는 검색 범위를 좁히는 효과가 없다.

### D2. primary 는 정확히 1개, secondary 는 최대 2개
- 실제 질문은 여러 쟁점에 걸친다. 순수 멀티라벨로 두면 라벨 수가 늘수록 평가·라우팅이 흐려지고,
  순수 단일 라벨로 두면 정보가 손실된다.
- 검색 필터·라우팅은 primary 하나로 결정하고, secondary 는 추천·분석용 보조 신호로만 쓴다.
- 2개로 제한한 이유: 3개 이상이 필요한 질문은 대부분 질문 자체가 여러 개다 (§4 R6).

### D3. 기존 벤치 라벨 `probation` 은 카테고리에서 속성으로 옮겼다
- "수습기간에도 최저임금을 받나요?"의 쟁점은 최저임금이다. 수습은 **누구에게** 적용되는지를 말해 줄 뿐이다.
- 그래서 `employment_type=probation` 속성으로 표현하고, 수습 기간 자체의 길이·효력을 묻는 경우만 `CONTRACT.PROBATION` 으로 둔다.
- 기존 라벨 체계는 주제(임금)와 대상(수습생)이 한 축에 섞여 있었다. 축을 분리하면 "수습생의 임금 질문"을 두 축 조합으로 표현할 수 있다.

### D4. 산재보험은 SOCIAL_INSURANCE 가 아니라 INJURY 에 둔다
- 형식상 4대보험이지만, 사용자는 "다쳤다"는 사건에서 출발하고, 절차(근로복지공단 산재 신청)와 근거 법령(산재보험법)이 다르다.
- 사용자 관점의 쟁점을 우선했다 (D1).

### D5. 퇴직금은 SOCIAL_INSURANCE 에서 분리해 RETIREMENT 로 둔다
- 초안은 "4대보험·퇴직금"을 묶었으나, 퇴직금은 보험이 아니라 사용자의 지급 의무이고 근거 법령(근로자퇴직급여 보장법)도 다르다.
- 외국인근로자의 **출국만기보험**은 이름은 보험이지만 퇴직금을 대신하는 제도라 `RETIREMENT.EPS_DEPARTURE` 에 둔다.

### D6. HOUSING 을 독립 대분류로 둔다
- 일반 노동 분류에서는 작은 주제지만, 외국인근로자 상담에서는 기숙사 문제가 반복적으로 나온다.
- 비용 공제는 WAGE 로 보내므로(D1) HOUSING 에는 시설·생활 문제만 남는다. 데이터가 쌓였을 때 건수가 너무 적으면 v2 에서 CONTRACT 하위로 합치는 것을 검토한다.

### D7. 범위 밖을 두 가지로 나눈다
- `OUT_OF_SCOPE.OTHER_LEGAL`(전세 사기, 교통사고)과 `OUT_OF_SCOPE.NON_LEGAL`(날씨)은 후속 처리가 다르다.
  전자는 다른 상담기관으로 안내해야 하고, 후자는 정중히 거절하면 된다.
- 지난 RAG 지연 측정에서 무관 질의 30건은 모두 NON_LEGAL 이었다. OTHER_LEGAL 은 임계값만으로 걸러지지 않을 가능성이 높아 따로 측정할 가치가 있다.

### D8. META 는 law_article 에만 쓴다
- 법령에는 "목적", "정의", "벌칙"처럼 특정 쟁점에 속하지 않는 조문이 많다 (산업안전보건법·출입국관리법의 상당수가 행정 절차).
- 이것들을 억지로 쟁점 카테고리에 넣으면 검색 필터가 오히려 부정확해진다. 질문과 계약서에는 이런 성격이 없으므로 쓰지 않는다.
- 조문 제목 키워드로 대략 세어 보면 1,318건 중 **최소 375건(28%)** 이 목적·정의·벌칙·조직·기금·위임 같은 조문이다
  (법령별 19~51%. 임금채권보장법·최저임금법은 절반 가까이가 기금·위원회 조문. 제목이 빈 삭제 조문 11건은 제외).
  키워드에 걸리지 않는 인증·지정 조문까지 치면 더 많다. 이 조문들이 검색 결과에 섞이면 질문에 대한 답이 되지 못한다.

### D12. 코퍼스 안에도 범위 밖 조문이 있다
- 출입국관리법에는 선박 검색, 승무원 상륙허가, 난민, 국민의 출국금지처럼 외국인근로자와 무관한 조문이 30여 개 있다.
- META 는 "쟁점과 무관한 형식 조항"이고, 이 조문들은 "쟁점이 있지만 LawRo 범위 밖"이라 성격이 다르다.
  그래서 law_article 에도 `OUT_OF_SCOPE.OTHER_LEGAL` 을 쓴다. 이후 검색 색인에서 뺄지 판단하는 근거가 된다.

### D9. 속성은 "명시된 경우에만" 채운다
- `workplace_size`, `visa_type` 등은 답을 바꾸는 중요한 정보지만, 질문에 없으면 LLM 이 그럴듯하게 추측하기 쉽다.
- 추측한 값은 틀렸을 때 잘못된 답(예: 5인 미만인데 해고 제한을 적용)으로 이어진다. 모르면 `unknown` 이 맞는 답이다.

### D10. 작성 언어는 LLM 에 맡기지 않는다
- 언어 감지는 규칙·라이브러리로 충분히 정확하다. LLM 에 맡기면 비용이 들고 가끔 틀린다.
- "LLM 이 꼭 필요한 곳에만 LLM 을 쓴다"는 원칙의 첫 적용 사례다.

### D11. 사업장 규모는 5인 기준 하나만 둔다
- 근로기준법의 해고 제한(제23조), 가산수당(제56조), 연차휴가(제60조) 등은 상시 5인 미만 사업장에 적용되지 않는다.
- 답이 달라지는 경계가 5인 하나뿐이라, 30인·300인 같은 구간을 두는 것은 라벨링 부담만 늘린다.

---

## 3. 라벨링 절차

한 콘텐츠에 대해 아래 순서로 판단한다.

1. **범위 확인** — 노동·체류와 무관하면 `OUT_OF_SCOPE` 의 두 하위 중 하나로 끝낸다. 속성은 채우지 않는다.
2. **최종 쟁점 찾기** — "이 사람이 결국 무엇에 대한 판단(예/아니오, 금액, 방법)을 원하는가?"를 한 문장으로 적는다.
   배경으로 설명한 상황이 아니라 **실제로 던진 질문**이 기준이다 (R11).
3. **primary 결정** — 그 쟁점에 답하는 조문이 속한 세분류를 고른다. §4 규칙과 §5 경계 사례를 확인한다.
4. **secondary 결정** — 결론에 영향을 주지는 않지만 함께 다뤄야 할 쟁점이 있으면 최대 2개.
5. **속성** — 텍스트에 명시된 것만 채운다. 나머지는 `unknown` 또는 기본값.

---

## 4. 판단 규칙

| # | 규칙 | 예 |
|---|---|---|
| R1 | 쟁점이 **돈의 액수·지급**이면 WAGE, **시간의 길이·한도**면 WORKTIME | "연장근로 수당 얼마?" → WAGE.ALLOWANCE / "연장근로 주 몇 시간까지?" → WORKTIME.LIMIT |
| R2 | 쉬는 날의 **부여 여부·일수**는 LEAVE, 그날에 대해 **사용자가 주는 돈**은 WAGE, **보험에서 나오는 급여**는 SOCIAL_INSURANCE | "주휴일을 줘야 하나?" → LEAVE.WEEKLY_HOLIDAY / "주휴수당 받나?" → WAGE.ALLOWANCE / "육아휴직 급여 얼마?" → SOCIAL_INSURANCE.EMPLOYMENT |
| R3 | 무언가를 임금에서 **빼는 것**이 쟁점이면 무엇을 빼든 WAGE.PAYMENT | 기숙사비·식비·벌금·유니폼비 공제 |
| R4 | 대상(수습·기간제·단시간·일용)은 카테고리가 아니라 `employment_type` 속성 | "알바도 주휴수당?" → WAGE.ALLOWANCE + part_time |
| R5 | 해고 **이후 받을 돈**(퇴직금·실업급여·체불임금)이 쟁점이면 그 돈의 카테고리 | "해고됐는데 실업급여 받나?" → SOCIAL_INSURANCE.EMPLOYMENT, secondary TERMINATION.DISMISSAL |
| R6 | 서로 독립된 질문이 여러 개면, 첫 질문 기준으로 primary 를 정하고 나머지는 secondary. 3개 이상이면 `notes` 에 "multi_question" 표시 | 이후 파이프라인에서 질문 분리 대상으로 쓴다 |
| R7 | 진짜로 우열을 가릴 수 없을 때만 우선순위: MISTREATMENT > INJURY > STAY > TERMINATION > WAGE > 나머지 | 위해가 크고 시급한 쪽을 먼저. 이 규칙을 쓴 경우 `notes` 에 "tie_break" 표시 |

| R8 | 보험·제도는 **이름이 아니라 기능**으로 분류한다 | 출국만기보험(퇴직금 대체) → RETIREMENT.EPS_DEPARTURE / 보증보험(체불 대비) → WAGE.UNPAID / 귀국비용보험·상해보험 → SOCIAL_INSURANCE.EPS |
| R9 | (law_article) 근로자가 **직접 주장·이용하는 권리·의무**면 쟁점 카테고리, 기관 조직·기금·인증·등록·사업주 지원사업이면 META.ADMIN | 산업안전보건법 제52조(근로자의 작업중지) → INJURY.SAFETY / 제84조(안전인증) → META.ADMIN |
| R10 | 심사청구·재심사 같은 **불복 절차**는 해당 제도의 카테고리 | 산재 심사청구 → INJURY.COMPENSATION / 고용보험 심사청구 → SOCIAL_INSURANCE.EMPLOYMENT |
| R11 | 상황 설명과 질문이 다른 쟁점이면 **질문한 쟁점**이 primary, 상황의 쟁점은 secondary. R5 도 질문이 그 돈에 대한 것일 때만 적용한다 | "월급이 밀렸는데 신고하면 비자에 문제 있나요?" → STAY.STATUS, secondary WAGE.UNPAID |
| R12 | 퇴직할 때 **무엇을 얼마나 언제까지** 받는지는 WAGE.SETTLEMENT, 기한이 지나 **받지 못한 것의 구제**는 WAGE.UNPAID | "그만두면 남은 연차는 돈으로 받나요?" → WAGE.SETTLEMENT / "퇴사한 지 두 달인데 마지막 월급을 못 받았어요" → WAGE.UNPAID |

R7 을 자주 쓰게 된다면 규칙이 아니라 분류 체계가 잘못된 것이다. 골든셋 라벨링 중 R7 사용 비율을 기록한다.

---

## 5. 경계 사례

라벨링하다 판단이 갈린 사례를 여기에 계속 추가한다.

| 콘텐츠 | 판단 | 근거 |
|---|---|---|
| 회사가 기숙사 비용을 임금에서 공제할 수 있나요? | WAGE.PAYMENT, secondary HOUSING.DORMITORY | R3. 공제의 적법성은 전액지급 원칙(근로기준법 제43조) 문제 |
| 기숙사 시설에 대한 기준이 있나요? | HOUSING.DORMITORY | 비용이 아닌 시설 자체 |
| 수습기간에도 최저임금을 받나요? | WAGE.MINIMUM, employment_type=probation | D3, R4 |
| 수습기간은 최대 얼마나 되나요? | CONTRACT.PROBATION | 수습 기간 자체가 쟁점 |
| 야간에 일하면 수당을 더 받나요? | WAGE.ALLOWANCE | R1. 야간근로의 제한(WORKTIME.SHIFT)이 아니라 가산금 |
| 회사가 도산하면 밀린 임금을 받을 수 있나요? | WAGE.UNPAID | 대지급금(임금채권보장법) |
| 산재로 일을 못하면 휴업급여를 받나요? | INJURY.COMPENSATION | D4. 보험 급여지만 산재 |
| 외국인도 국민연금에 가입해야 하나요? | SOCIAL_INSURANCE.PENSION | 출국 시 반환일시금 질문도 여기 |
| 4대보험 가입은 의무인가요? | SOCIAL_INSURANCE.ENROLLMENT | 기존 벤치 라벨을 다시 붙이다 발견한 공백. 특정 보험을 고를 수 없고 산재도 포함되지만, 쟁점은 "가입 의무"라는 한 가지다. D4 의 예외로 산재가 섞여도 여기에 둔다 |
| 출국하면 퇴직금은 어떻게 받나요? | RETIREMENT.EPS_DEPARTURE, secondary STAY.STATUS | D5. 출국만기보험 |
| 고용주가 여권을 보관해도 되나요? | STAY.DOCUMENTS | 여권 압수가 **진행 중**이면 urgency=high, secondary MISTREATMENT.FORCED_LABOR |
| 해고를 당하면 예고를 받아야 하나요? | TERMINATION.DISMISSAL | |
| 부당해고를 당하면 어디에 구제를 신청하나요? | TERMINATION.UNFAIR_REMEDY, intent=procedure | |
| 일을 그만두면 위약금을 내야 한다고 계약서에 있어요 | CONTRACT.PROHIBITED_TERMS | 위약금 예정 금지(근로기준법 제20조). 퇴사 절차가 아니라 조항의 효력 |
| 사장이 한국인 직원보다 월급을 적게 줘요 | MISTREATMENT.DISCRIMINATION, secondary WAGE.PAYMENT | 쟁점은 금액이 아니라 국적에 따른 차별(근로기준법 제6조) |
| 전세 보증금을 못 돌려받고 있어요 | OUT_OF_SCOPE.OTHER_LEGAL | D7 |
| (조문) 근로기준법 제109조 벌칙 | META.PENALTY | D8 |
| 손님이 매일 욕을 해요 | INJURY.SAFETY, secondary MISTREATMENT.HARASSMENT | 직장 내 괴롭힘(근로기준법 제76조의2)은 사용자·동료가 가해자일 때다. 고객 폭언은 사업주의 건강장해 예방 의무(산업안전보건법 제41조) |
| 쉴 곳이 없어서 창고 바닥에서 쉬어요 | INJURY.SAFETY | 휴게**시설**(산업안전보건법 제128조의2)은 시설 문제. 휴게**시간**의 길이가 쟁점이면 WORKTIME.BREAK |
| 위험한 작업도 하루 8시간 넘게 시켜요 | WORKTIME.LIMIT, secondary INJURY.SAFETY | R1: 시간의 한도가 쟁점. 근거는 산업안전보건법 제139조지만 질문자가 묻는 건 시간 |
| 계약직이라고 상여금을 안 줘요 | CONTRACT.FIXED_TERM | 고용형태 차별은 기간제법 차별 시정(노동위원회)으로 다룬다. 국적·성별 차별만 MISTREATMENT.DISCRIMINATION |
| 지각했다고 월급에서 10만원을 뺐어요 | WAGE.PAYMENT | R3. 감급 제재의 한도(근로기준법 제95조)도 결국 임금에서 빼는 문제 |
| 사장이 외국인등록증을 돈 빌려준 담보로 가져갔어요 | STAY.DOCUMENTS, urgency=high | 등록증을 채무 담보로 잡는 것 자체가 금지(출입국관리법 제33조의3). 진행 중이라 high |
| 한국에 올 때 브로커한테 수수료를 냈어요 | MISTREATMENT.FORCED_LABOR | 중간착취의 배제(근로기준법 제9조) |
| 육아휴직 급여는 얼마 받나요? | SOCIAL_INSURANCE.EMPLOYMENT, secondary LEAVE.MATERNITY_FAMILY | R2: 보험에서 나오는 급여 |
| 회사가 문 닫았는데 보증보험으로 월급 받을 수 있나요? | WAGE.UNPAID | R8: 보증보험은 체불 대비 |
| (조문) 출입국관리법 제69조 선박등의 검색 및 심사 | OUT_OF_SCOPE.OTHER_LEGAL | D12 |
| (조문) 고용보험법 제20조 고용창출의 지원 | META.ADMIN | R9: 사업주 대상 지원사업 |
| 사장님이 3달째 월급을 안 줘요. 노동청에 신고하면 비자에 문제 생기나요? | STAY.STATUS, secondary WAGE.UNPAID | R11. 체불은 배경이고 질문은 체류 영향 |
| E-9인데 사장이 다른 공장 가서 일하래요. 합법인가요? | STAY.STATUS, secondary STAY.WORKPLACE_CHANGE | R11. 묻는 것은 허가 없이 다른 곳에서 일하는 것의 적법성(불법취업 위험). 근로자가 직접 옮기는 사업장 변경 절차와 다르다 |
| 부당해고 구제신청이랑 실업급여 신청 같이 할 수 있나요? | TERMINATION.UNFAIR_REMEDY, secondary SOCIAL_INSURANCE.EMPLOYMENT | R11. 질문은 두 절차의 병행이지 실업급여 액수가 아니므로 R5 를 적용하지 않는다 |
| 퇴사하면 남은 연차는 돈으로 받나요? | WAGE.SETTLEMENT, secondary LEAVE.ANNUAL | R12. 연차의 일수가 아니라 정산받을 돈 |
| 조장이 매일 '외국 돼지'라고 욕해요 | MISTREATMENT.HARASSMENT, secondary MISTREATMENT.DISCRIMINATION | 반복적 모욕이라는 행위 형태가 쟁점. 임금·배치 등 **처우의 차이**가 쟁점이면 DISCRIMINATION |
| 임신했는데 무거운 짐 나르는 일에서 빼 줄 수 있나요? | LEAVE.MATERNITY_FAMILY | 임산부 보호(근로기준법 제74조). 보호 대상 속성이 생기기 전까지 출산 관련 보호는 여기에 모은다 (§9) |
| 쉬는 날 교통사고가 났는데 병원비는 누가 내나요? | SOCIAL_INSURANCE.HEALTH, secondary SOCIAL_INSURANCE.EPS | 업무 외 사고라 산재는 아니지만 치료비 부담은 건강보험 문제. E-9 이면 상해보험도 해당 |
| (조문) 외국인고용법 제23조 보증보험 등의 가입 | WAGE.UNPAID, secondary SOCIAL_INSURANCE.EPS | 한 조문에 기능이 둘(보증보험·상해보험)이면 제1항 기준 |

---

## 6. 속성 라벨링 규칙

| 속성 | 규칙 |
|---|---|
| `intent` | 문장 형태보다 목적을 본다. "월급을 안 주는데 신고할 수 있나요?"는 의문문이지만 문제가 이미 발생했으므로 `dispute`. 신고 방법이 핵심이면 `procedure` 가 아니라 `dispute` 를 우선한다 (문제 발생 여부가 긴급도·후속 처리에 더 중요) |
| `urgency` | `high` 는 신체 위험, 진행 중인 폭행·감금·여권 압수, 며칠 내 출국·체류 만료처럼 **즉시 조치가 필요한 경우만**. 체불·해고 통보는 심각해도 `medium` |
| `employment_type` | "알바"는 `part_time`, "일당"은 `daily`, "계약직·1년 계약"은 `fixed_term`. 언급이 없으면 `unknown` (정규직으로 가정하지 않는다) |
| `worker_status` | "잘렸어요", "그만뒀어요" → `left`. 시제가 불분명하면 `unknown` |
| `workplace_size` | 인원이 명시된 경우만. "작은 식당" 같은 표현만으로 `under_5` 를 추측하지 않는다 (D9) |
| `visa_type` | "E-9", "고용허가제로 왔다" → `E-9`. "방문취업" → `H-2` |
| `legal_refs` | 코퍼스 12개 법령 안에서만, 최대 3개. 확신이 없으면 비워 둔다 (틀린 조문은 없는 것보다 나쁘다) |
| `compliance` | 계약서 조항만. 금액·기간 등 판단에 필요한 사실이 조항에 다 있으면 `violation`/`compliant`, 외부 사실에 달려 있으면 `needs_review` |

---

## 7. content_type 별 주의

- **query**: 짧고 구어체이며 다국어다. 번역하지 말고 원문 그대로 판단한다. 번역 단계를 두면 비용이 늘고 오류가 누적된다.
- **contract_clause**: OCR 오류가 섞인다. 숫자(금액·시간)가 깨졌으면 `compliance=needs_review` 로 두고 `notes` 에 "ocr_noise" 를 남긴다.
- **law_article**: 조문 제목만 보지 말고 본문을 본다. 벌칙 조문은 인용한 조문의 쟁점이 아니라 META.PENALTY 로 둔다.

---

## 8. 기존 벤치 라벨(`bench/queries.jsonl`) → v1 대응

| 기존 | v1 | 비고 |
|---|---|---|
| wage | WAGE.* | 세분류로 나뉜다 |
| worktime | WORKTIME.* | |
| holiday | LEAVE.* | |
| insurance | SOCIAL_INSURANCE.* | 산재는 INJURY 로 (D4) |
| dismissal | TERMINATION.* | |
| probation | 주로 WAGE.MINIMUM + `employment_type=probation` | D3. 수습 기간 자체를 묻는 경우만 CONTRACT.PROBATION |
| housing | WAGE.PAYMENT 또는 HOUSING.DORMITORY | R3 |
| injury | INJURY.COMPENSATION | |
| visa | STAY.* | |
| severance | RETIREMENT.SEVERANCE | |
| irrelevant | OUT_OF_SCOPE.NON_LEGAL | |

---

## 9. 알려진 한계

- **코퍼스 공백**: 남녀고용평등법(직장 내 성희롱·육아휴직), 노동조합법, 파견법이 코퍼스에 없다.
  MISTREATMENT, LEAVE.MATERNITY_FAMILY 질문은 분류는 되지만 `legal_refs` 를 채우지 못하는 경우가 생긴다.
  골든셋에서 이 비율을 재서 코퍼스 확장 우선순위의 근거로 쓴다.
- **HOUSING 규모**: D6 참고. 실제 분포를 보고 v2 에서 유지 여부를 결정한다.
- **대상 축이 고용 형태뿐이다**: 근로기준법에는 연소자(제64~72조)·임산부(제74조) 보호 조문이 있지만 v1 에는 이 대상을 표현할 속성이 없다.
  당분간 연소자의 근로시간 제한은 WORKTIME, 취직 최저연령은 CONTRACT.WRITTEN 으로 둔다. 질문 데이터에서 자주 나오면 `protected_group` 속성을 검토한다.
- **업무 중 손해의 근로자 배상 책임**: "회사 차로 사고 났는데 수리비를 다 내래요" 같은 질문은 사용자에게는 노동 문제지만 코퍼스에 직접 조문이 없어
  `OUT_OF_SCOPE.OTHER_LEGAL` 로 둔다 (배상액을 월급에서 빼면 WAGE.PAYMENT). 실제 질문에서 자주 나오면 세분류 추가를 검토한다.
- **INJURY.SAFETY 와 조문 수의 불균형**: 산업안전보건법(184조)의 대부분이 이 세분류나 META 로 가서 조문 기준 분포가 크게 치우친다.
  카테고리별 성능은 콘텐츠 종류별로 따로 본다.

---

## 10. 버전 관리

- **MAJOR**: 라벨 삭제·병합·분할 → 기존 라벨 데이터를 다시 추출(백필)해야 한다
- **MINOR**: 라벨·속성 값 추가 → 새 라벨에 해당할 수 있는 콘텐츠만 다시 추출
- **PATCH**: 설명·경계 사례 보완 → 재추출 불필요 (단, 프롬프트가 바뀌므로 골든셋 평가는 다시 돌린다)

추출 결과마다 `taxonomy_version` 을 함께 저장해, 버전이 바뀌었을 때 영향받는 데이터만 골라 다시 처리할 수 있게 한다.

### 변경 이력
- 1.0.0 (2026-09-28): 최초 버전. 기존 벤치 라벨 11개를 대분류 13개·세분류 40개로 재설계.
  벤치 질의 100건을 다시 라벨링하며 SOCIAL_INSURANCE.ENROLLMENT 를 추가했다 (`seed/bench_v1.jsonl`)
- 1.1.0 (2026-09-28): 12개 법령 조문 1,318건의 제목을 전수 검토해 빈틈을 채웠다.
  - 세분류 추가: RETIREMENT.PENSION_PLAN(퇴직연금), SOCIAL_INSURANCE.EPS(귀국비용·상해보험), STAY.EPS_PROCESS(고용허가·입국·취업교육)
  - 범위 확장: WAGE.ALLOWANCE 에 휴업수당, MISTREATMENT.FORCED_LABOR 에 중간착취, OUT_OF_SCOPE 를 law_article 에도 사용(D12)
  - 규칙 추가: R8(기능 기준), R9(권리·의무 vs 행정), R10(불복 절차), R2 보완(보험 급여)
  - 경계 사례 11개 추가. 기존 라벨의 의미는 바뀌지 않아 MINOR (시드 100건 재라벨링 불필요)
- 1.2.0 (2026-09-28): 분쟁·긴급·경계 사례 61건(`seed/hard_v1.jsonl`)을 라벨링하며 판단이 갈린 9건을 정리했다.
  - 세분류 추가: WAGE.SETTLEMENT(퇴직 시 금품청산·미사용 연차수당). WAGE.UNPAID 는 "이미 받지 못한 임금의 구제"로 범위를 명확히 했다
  - 규칙 추가: R11(질문한 쟁점이 primary), R12(정산 vs 체불)
  - 경계 사례 8개 추가, 한계에 업무상 손해배상 추가
  - 시드 재라벨링 2건: h032 primary 를 STAY.WORKPLACE_CHANGE → STAY.STATUS (R11), h010 secondary 에 WAGE.SETTLEMENT.
    벤치 시드 100건에는 퇴직 정산 질문이 없어 영향 없음
