# 추출 평가: solar-pro2 / taxonomy v2.0.0 / prompt p2 / split all

시드 161건 중 평가 161건 (결과 없음·실패 0건)

## 카테고리

| 그룹 | n | primary 세분류 | primary 대분류 |
|---|---:|---:|---:|
| 전체 | 161 | 91.9% (148/161) | 94.4% (152/161) |
| 가이드 예시 아님 | 139 | 91.4% (127/139) | 94.2% (131/139) |
| content_type=query | 143 | 91.6% (131/143) | 94.4% (135/143) |
| source=seed:bench | 100 | 97.0% (97/100) | 97.0% (97/100) |
| query 언어=ko | 59 | 89.8% (53/59) | 94.9% (56/59) |
| 가이드 예시와 동일 | 22 | 95.5% (21/22) | 95.5% (21/22) |
| query 언어≠ko | 84 | 92.9% (78/84) | 94.0% (79/84) |
| source=seed:hard | 61 | 83.6% (51/61) | 90.2% (55/61) |
| content_type=contract_clause | 10 | 90.0% (9/10) | 90.0% (9/10) |
| content_type=law_article | 8 | 100.0% (8/8) | 100.0% (8/8) |

primary 세분류 정확도 95% 신뢰구간 (bootstrap, 표본 단위): 87.6% ~ 95.7%

## 대분류별 (primary)

macro-F1 0.945

| 대분류 | 정답 수 | 예측 수 | P | R | F1 |
|---|---:|---:|---:|---:|---:|
| WAGE | 43 | 43 | 0.98 | 0.98 | 0.98 |
| OUT_OF_SCOPE | 15 | 16 | 0.88 | 0.93 | 0.90 |
| SOCIAL_INSURANCE | 14 | 15 | 0.87 | 0.93 | 0.90 |
| WORKTIME | 13 | 13 | 1.00 | 1.00 | 1.00 |
| INJURY | 13 | 12 | 1.00 | 0.92 | 0.96 |
| LEAVE | 12 | 12 | 0.92 | 0.92 | 0.92 |
| TERMINATION | 11 | 11 | 1.00 | 1.00 | 1.00 |
| MISTREATMENT | 11 | 13 | 0.85 | 1.00 | 0.92 |
| RETIREMENT | 10 | 8 | 0.88 | 0.70 | 0.78 |
| STAY | 9 | 9 | 1.00 | 1.00 | 1.00 |
| CONTRACT | 8 | 7 | 1.00 | 0.88 | 0.93 |
| HOUSING | 1 | 1 | 1.00 | 1.00 | 1.00 |
| GENERAL | 1 | 1 | 1.00 | 1.00 | 1.00 |


secondary (micro): P 0.50 / R 0.68 / F1 0.58

## 속성

정답에 값이 있는 항목만 센다. `unknown` 도 정답으로 취급한다 (추측 금지 원칙, GUIDE D9).

| 속성 | 정확도 | 틀린 예 (정답→예측) |
|---|---:|---|
| intent | 85.3% (110/129) | procedure→info ×10, calculation→info ×5, dispute→info ×3, info→dispute ×1 |
| urgency | 89.9% (116/129) | medium→low ×7, low→medium ×5, high→medium ×1 |
| employment_type | 97.1% (134/138) | fixed_term→unknown ×2, probation→unknown ×1, unknown→fixed_term ×1 |
| worker_status | 80.0% (32/40) | employed→left ×3, unknown→employed ×3, employed→unknown ×1, unknown→left ×1 |
| workplace_size | 100.0% (49/49) |  |
| visa_type | 90.0% (36/40) | unknown→E-9 ×4 |
| compliance | 66.7% (6/9) | needs_review→violation ×2, violation→needs_review ×1 |
| provision_type | 87.5% (7/8) | administration→right_duty ×1 |

language (규칙 기반): 100.0% (153/153)

## 근거 조문 (legal_refs)

- 정확 일치 (n=58): P 0.43 / R 0.56 / F1 0.49
- 코퍼스에 없는 조문 인용(검증에서 제거): 0건

## primary 오답

| id | 본문 | 정답 | 예측 | 모델이 쓴 쟁점 |
|---|---|---|---|---|
| q061 | Tôi được nghỉ phép năm bao nhiêu ngày? | LEAVE.ANNUAL | OUT_OF_SCOPE.OTHER_LEGAL | 베트남 근로자가 받을 수 있는 연차유급휴가 일수는 얼마인가? |
| q068 | Khi nào tôi được nhận trợ cấp thôi việc? | RETIREMENT.SEVERANCE | SOCIAL_INSURANCE.EMPLOYMENT | 실업급여를 언제 받을 수 있나요? |
| q090 | เงินชดเชยเมื่อลาออกได้รับเมื่อใด? | RETIREMENT.SEVERANCE | WAGE.SETTLEMENT | 퇴직 시 금품청산 기한은 언제인가? |
| h003 | 지금 사장이 여권 달라고 해서 안 주니까 때렸어요 어떡해요 | MISTREATMENT.HARASSMENT | MISTREATMENT.FORCED_LABOR | 고용주가 여권을 요구하여 주지 않자 폭행한 상황에서 어떻게 대처해야 하는가 |
| h011 | 직원 3명인 식당인데 사장님이 내일부터 나오지 말래요. 이유도 안 알려줘요. | TERMINATION.DISMISSAL | TERMINATION.UNFAIR_REMEDY | 사장이 이유 없이 해고 통보를 했을 때 법적 구제 방법이 있는가? |
| h013 | Tôi làm theo ngày ở công trường, làm được 8 tháng rồi. Nghỉ  | RETIREMENT.SEVERANCE | SOCIAL_INSURANCE.EMPLOYMENT | 일용직 근로자가 퇴사 시 실업급여를 받을 수 있는지 여부 |
| h020 | 콜센터에서 일하는데 손님이 욕하고 성희롱까지 해요. 회사는 참으라고만 해요 | INJURY.SAFETY | MISTREATMENT.HARASSMENT | 고객의 폭언과 성희롱에 대해 회사가 적절한 조치를 취하지 않는 상황에서 어떻게 대처해야 하는가? |
| h023 | 저 17살인데 밤 11시까지 알바해도 되나요? | WORKTIME.SHIFT | WORKTIME.LIMIT | 17세 청소년이 밤 11시까지 아르바이트를 해도 되는지 여부 |
| h029 | Khi về nước tôi có lấy lại được tiền lương hưu đã đóng không | SOCIAL_INSURANCE.PENSION | RETIREMENT.EPS_DEPARTURE | 출국 시 납부한 퇴직연금(퇴직금)을 돌려받을 수 있는지 여부 |
| h031 | 감기로 3일 쉬었는데 무단결근이라고 월급 깎는대요 | WAGE.PAYMENT | LEAVE.SICK | 감기로 3일 병가를 사용했는데 무단결근으로 처리되어 월급이 감액되는 것이 정당한가? |
| h034 | 회사 차 운전하다가 사고 났는데 수리비를 저한테 다 내래요 | OUT_OF_SCOPE.OTHER_LEGAL | MISTREATMENT.FORCED_LABOR | 회사 차량 운전 중 발생한 사고 수리비를 근로자가 전액 부담해야 하는지 여부 |
| h035 | Is working in Korea better than Japan for Vietnamese workers | OUT_OF_SCOPE.NON_LEGAL | OUT_OF_SCOPE.OTHER_LEGAL | Is working in Korea better than Japan for Vietnamese workers? |
| c007 | 근로자 성명: NGUYEN VAN A / 생년월일: 1998.03.12 | CONTRACT.WRITTEN | OUT_OF_SCOPE.NON_LEGAL | 근로계약서 조항에 대한 분류 및 라벨링 |
