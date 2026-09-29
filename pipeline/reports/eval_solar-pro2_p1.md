# 추출 평가: solar-pro2 / taxonomy v1.2.0 / prompt p1

시드 161건 중 평가 161건 (결과 없음·실패 0건)

## 카테고리

| 그룹 | n | primary 세분류 | primary 대분류 |
|---|---:|---:|---:|
| 전체 | 161 | 90.7% (146/161) | 92.5% (149/161) |
| 가이드 예시 아님 | 140 | 90.7% (127/140) | 92.9% (130/140) |
| content_type=query | 143 | 91.6% (131/143) | 93.0% (133/143) |
| source=seed:bench | 100 | 97.0% (97/100) | 97.0% (97/100) |
| query 언어=ko | 59 | 91.5% (54/59) | 93.2% (55/59) |
| 가이드 예시와 동일 | 21 | 90.5% (19/21) | 90.5% (19/21) |
| query 언어≠ko | 84 | 91.7% (77/84) | 92.9% (78/84) |
| source=seed:hard | 61 | 80.3% (49/61) | 85.2% (52/61) |
| content_type=contract_clause | 10 | 80.0% (8/10) | 90.0% (9/10) |
| content_type=law_article | 8 | 87.5% (7/8) | 87.5% (7/8) |

secondary (micro): P 0.42 / R 0.79 / F1 0.55

## 속성

정답에 값이 있는 항목만 센다. `unknown` 도 정답으로 취급한다 (추측 금지 원칙, GUIDE D9).

| 속성 | 정확도 | 틀린 예 (정답→예측) |
|---|---:|---|
| intent | 86.7% (111/128) | dispute→info ×9, procedure→info ×7, procedure→dispute ×1 |
| urgency | 84.4% (108/128) | low→medium ×7, medium→low ×6, low→high ×6, high→medium ×1 |
| employment_type | 97.8% (134/137) | fixed_term→unknown ×2, probation→unknown ×1 |
| worker_status | 76.9% (30/39) | employed→left ×4, unknown→employed ×3, employed→unknown ×1, unknown→left ×1 |
| workplace_size | 100.0% (48/48) |  |
| visa_type | 89.7% (35/39) | unknown→E-9 ×4 |
| compliance | 66.7% (6/9) | violation→needs_review ×1, needs_review→compliant ×1, needs_review→violation ×1 |

language (규칙 기반): 100.0% (153/153)

## 근거 조문 (legal_refs)

- 정확 일치 (n=58): P 0.42 / R 0.55 / F1 0.48
- 코퍼스에 없는 조문 인용(검증에서 제거): 0건

## primary 오답

| id | 본문 | 정답 | 예측 | 모델이 쓴 쟁점 |
|---|---|---|---|---|
| q061 | Tôi được nghỉ phép năm bao nhiêu ngày? | LEAVE.ANNUAL | OUT_OF_SCOPE.OTHER_LEGAL | 베트남 근로자가 받을 수 있는 연차유급휴가 일수는 얼마인가? |
| q068 | Khi nào tôi được nhận trợ cấp thôi việc? | RETIREMENT.SEVERANCE | SOCIAL_INSURANCE.EMPLOYMENT | 실업급여를 받을 수 있는 시기는 언제인가요? |
| q090 | เงินชดเชยเมื่อลาออกได้รับเมื่อใด? | RETIREMENT.SEVERANCE | WAGE.SETTLEMENT | 퇴직 시 금품청산 기한은 언제인가? |
| h003 | 지금 사장이 여권 달라고 해서 안 주니까 때렸어요 어떡해요 | MISTREATMENT.HARASSMENT | STAY.DOCUMENTS | 사장이 여권을 요구하여 주지 않자 폭행한 상황에서 어떻게 대처해야 하는가? |
| h008 | I got into a car accident on my day off. Who pays my hospita | SOCIAL_INSURANCE.HEALTH | OUT_OF_SCOPE.OTHER_LEGAL | Who pays the hospital bill for a car accident that occurred on the worker's day  |
| h013 | Tôi làm theo ngày ở công trường, làm được 8 tháng rồi. Nghỉ  | RETIREMENT.SEVERANCE | SOCIAL_INSURANCE.EMPLOYMENT | 일용직 근로자가 퇴사 시 실업급여를 받을 수 있는지 여부 |
| h020 | 콜센터에서 일하는데 손님이 욕하고 성희롱까지 해요. 회사는 참으라고만 해요 | INJURY.SAFETY | MISTREATMENT.HARASSMENT | 고객의 폭언과 성희롱에 대해 회사가 아무런 조치를 취하지 않는 상황에서 어떻게 대응해야 하는가? |
| h023 | 저 17살인데 밤 11시까지 알바해도 되나요? | WORKTIME.SHIFT | WORKTIME.LIMIT | 17세 청소년이 밤 11시까지 아르바이트를 해도 되는지 여부 |
| h029 | Khi về nước tôi có lấy lại được tiền lương hưu đã đóng không | SOCIAL_INSURANCE.PENSION | RETIREMENT.EPS_DEPARTURE | 출국 시 퇴직금 대체 보험(출국만기보험)을 받을 수 있는지 여부 |
| h031 | 감기로 3일 쉬었는데 무단결근이라고 월급 깎는대요 | WAGE.PAYMENT | LEAVE.SICK | 감기로 3일 병가를 냈으나 무단결근으로 처리되어 월급이 감액되는 것이 정당한가? |
| h034 | 회사 차 운전하다가 사고 났는데 수리비를 저한테 다 내래요 | OUT_OF_SCOPE.OTHER_LEGAL | INJURY.COMPENSATION | 회사 차량 운전 중 발생한 사고 수리비를 근로자가 전액 부담해야 하는지 여부 |
| h035 | Is working in Korea better than Japan for Vietnamese workers | OUT_OF_SCOPE.NON_LEGAL | OUT_OF_SCOPE.OTHER_LEGAL | 한국에서의 근무가 베트남 근로자들에게 일본보다 더 나은지 여부 |
| c003 | 월 급여에는 연장·야간·휴일근로수당이 모두 포함된 것으로 한다. | WAGE.ALLOWANCE | WAGE.PAYMENT | 월 급여에 연장·야간·휴일근로수당이 포함된 것으로 하는 조항의 적법성 여부 |
| c007 | 근로자 성명: NGUYEN VAN A / 생년월일: 1998.03.12 | CONTRACT.WRITTEN | OUT_OF_SCOPE.NON_LEGAL | 근로계약서 조항에 대한 법적 검토 및 분류 |
| a005 | 제69조(선박등의 검색 및 심사) ① 선박등이 출입국항에 출ㆍ입항할 때에는 출입국관리공무원의 검색을 받아야  | OUT_OF_SCOPE.OTHER_LEGAL | META.ADMIN | 출입국항에 출·입항하는 선박등의 검색 및 심사 절차는 어떻게 되는가? |
