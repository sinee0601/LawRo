# 추출 평가: solar-pro2 / taxonomy v1.2.0 / prompt p1 / split dev

시드 82건 중 평가 82건 (결과 없음·실패 0건)

## 카테고리

| 그룹 | n | primary 세분류 | primary 대분류 |
|---|---:|---:|---:|
| 전체 | 82 | 90.2% (74/82) | 91.5% (75/82) |
| 가이드 예시와 동일 | 15 | 86.7% (13/15) | 86.7% (13/15) |
| content_type=query | 73 | 90.4% (66/73) | 91.8% (67/73) |
| source=seed:bench | 51 | 98.0% (50/51) | 98.0% (50/51) |
| query 언어=ko | 27 | 88.9% (24/27) | 88.9% (24/27) |
| 가이드 예시 아님 | 67 | 91.0% (61/67) | 92.5% (62/67) |
| query 언어≠ko | 46 | 91.3% (42/46) | 93.5% (43/46) |
| source=seed:hard | 31 | 77.4% (24/31) | 80.6% (25/31) |
| content_type=contract_clause | 5 | 80.0% (4/5) | 80.0% (4/5) |
| content_type=law_article | 4 | 100.0% (4/4) | 100.0% (4/4) |

primary 세분류 정확도 95% 신뢰구간 (bootstrap, 표본 단위): 84.1% ~ 96.3%

## 대분류별 (primary)

macro-F1 0.864

| 대분류 | 정답 수 | 예측 수 | P | R | F1 |
|---|---:|---:|---:|---:|---:|
| WAGE | 20 | 19 | 1.00 | 0.95 | 0.97 |
| STAY | 11 | 11 | 1.00 | 1.00 | 1.00 |
| LEAVE | 10 | 10 | 0.90 | 0.90 | 0.90 |
| TERMINATION | 10 | 10 | 1.00 | 1.00 | 1.00 |
| INJURY | 10 | 10 | 0.90 | 0.90 | 0.90 |
| SOCIAL_INSURANCE | 7 | 7 | 0.86 | 0.86 | 0.86 |
| RETIREMENT | 3 | 2 | 1.00 | 0.67 | 0.80 |
| META | 3 | 3 | 1.00 | 1.00 | 1.00 |
| MISTREATMENT | 2 | 3 | 0.67 | 1.00 | 0.80 |
| OUT_OF_SCOPE | 2 | 4 | 0.25 | 0.50 | 0.33 |
| CONTRACT | 2 | 1 | 1.00 | 0.50 | 0.67 |
| HOUSING | 1 | 1 | 1.00 | 1.00 | 1.00 |
| WORKTIME | 1 | 1 | 1.00 | 1.00 | 1.00 |


secondary (micro): P 0.58 / R 0.86 / F1 0.69

## 속성

정답에 값이 있는 항목만 센다. `unknown` 도 정답으로 취급한다 (추측 금지 원칙, GUIDE D9).

| 속성 | 정확도 | 틀린 예 (정답→예측) |
|---|---:|---|
| intent | 94.3% (66/70) | procedure→info ×2, dispute→info ×2 |
| urgency | 88.6% (62/70) | low→high ×6, low→medium ×2 |
| employment_type | 98.6% (73/74) | fixed_term→unknown ×1 |
| worker_status | 85.0% (17/20) | employed→left ×2, unknown→employed ×1 |
| workplace_size | 100.0% (24/24) |  |
| visa_type | 95.0% (19/20) | unknown→E-9 ×1 |
| compliance | 50.0% (2/4) | violation→needs_review ×1, needs_review→compliant ×1 |

language (규칙 기반): 100.0% (78/78)

## 근거 조문 (legal_refs)

- 정확 일치 (n=30): P 0.33 / R 0.44 / F1 0.38
- 코퍼스에 없는 조문 인용(검증에서 제거): 0건

## primary 오답

| id | 본문 | 정답 | 예측 | 모델이 쓴 쟁점 |
|---|---|---|---|---|
| q061 | Tôi được nghỉ phép năm bao nhiêu ngày? | LEAVE.ANNUAL | OUT_OF_SCOPE.OTHER_LEGAL | 베트남 근로자가 받을 수 있는 연차유급휴가 일수는 얼마인가? |
| h008 | I got into a car accident on my day off. Who pays my hospita | SOCIAL_INSURANCE.HEALTH | OUT_OF_SCOPE.OTHER_LEGAL | Who pays the hospital bill for a car accident that occurred on the worker's day  |
| h013 | Tôi làm theo ngày ở công trường, làm được 8 tháng rồi. Nghỉ  | RETIREMENT.SEVERANCE | SOCIAL_INSURANCE.EMPLOYMENT | 일용직 근로자가 퇴사 시 실업급여를 받을 수 있는지 여부 |
| h020 | 콜센터에서 일하는데 손님이 욕하고 성희롱까지 해요. 회사는 참으라고만 해요 | INJURY.SAFETY | MISTREATMENT.HARASSMENT | 고객의 폭언과 성희롱에 대해 회사가 아무런 조치를 취하지 않는 상황에서 어떻게 대응해야 하는가? |
| h031 | 감기로 3일 쉬었는데 무단결근이라고 월급 깎는대요 | WAGE.PAYMENT | LEAVE.SICK | 감기로 3일 병가를 냈으나 무단결근으로 처리되어 월급이 감액되는 것이 정당한가? |
| h034 | 회사 차 운전하다가 사고 났는데 수리비를 저한테 다 내래요 | OUT_OF_SCOPE.OTHER_LEGAL | INJURY.COMPENSATION | 회사 차량 운전 중 발생한 사고 수리비를 근로자가 전액 부담해야 하는지 여부 |
| h035 | Is working in Korea better than Japan for Vietnamese workers | OUT_OF_SCOPE.NON_LEGAL | OUT_OF_SCOPE.OTHER_LEGAL | 한국에서의 근무가 베트남 근로자들에게 일본보다 더 나은지 여부 |
| c007 | 근로자 성명: NGUYEN VAN A / 생년월일: 1998.03.12 | CONTRACT.WRITTEN | OUT_OF_SCOPE.NON_LEGAL | 근로계약서 조항에 대한 법적 검토 및 분류 |
