# 추출 평가: solar-pro2 / taxonomy v1.2.0 / prompt p1 / split test

시드 79건 중 평가 79건 (결과 없음·실패 0건)

## 카테고리

| 그룹 | n | primary 세분류 | primary 대분류 |
|---|---:|---:|---:|
| 전체 | 79 | 91.1% (72/79) | 93.7% (74/79) |
| 가이드 예시 아님 | 73 | 90.4% (66/73) | 93.2% (68/73) |
| content_type=query | 70 | 92.9% (65/70) | 94.3% (66/70) |
| source=seed:bench | 49 | 95.9% (47/49) | 95.9% (47/49) |
| query 언어=ko | 32 | 93.8% (30/32) | 96.9% (31/32) |
| 가이드 예시와 동일 | 6 | 100.0% (6/6) | 100.0% (6/6) |
| query 언어≠ko | 38 | 92.1% (35/38) | 92.1% (35/38) |
| source=seed:hard | 30 | 83.3% (25/30) | 90.0% (27/30) |
| content_type=contract_clause | 5 | 80.0% (4/5) | 100.0% (5/5) |
| content_type=law_article | 4 | 75.0% (3/4) | 75.0% (3/4) |

primary 세분류 정확도 95% 신뢰구간 (bootstrap, 표본 단위): 84.8% ~ 96.2%

## 대분류별 (primary)

macro-F1 0.920

| 대분류 | 정답 수 | 예측 수 | P | R | F1 |
|---|---:|---:|---:|---:|---:|
| WAGE | 23 | 24 | 0.96 | 1.00 | 0.98 |
| OUT_OF_SCOPE | 13 | 12 | 1.00 | 0.92 | 0.96 |
| WORKTIME | 12 | 12 | 1.00 | 1.00 | 1.00 |
| RETIREMENT | 7 | 6 | 0.83 | 0.71 | 0.77 |
| SOCIAL_INSURANCE | 6 | 6 | 0.83 | 0.83 | 0.83 |
| CONTRACT | 6 | 6 | 1.00 | 1.00 | 1.00 |
| STAY | 5 | 6 | 0.83 | 1.00 | 0.91 |
| INJURY | 2 | 2 | 1.00 | 1.00 | 1.00 |
| MISTREATMENT | 2 | 1 | 1.00 | 0.50 | 0.67 |
| LEAVE | 2 | 2 | 1.00 | 1.00 | 1.00 |
| TERMINATION | 1 | 1 | 1.00 | 1.00 | 1.00 |


secondary (micro): P 0.19 / R 0.57 / F1 0.29

## 속성

정답에 값이 있는 항목만 센다. `unknown` 도 정답으로 취급한다 (추측 금지 원칙, GUIDE D9).

| 속성 | 정확도 | 틀린 예 (정답→예측) |
|---|---:|---|
| intent | 77.6% (45/58) | dispute→info ×7, procedure→info ×5, procedure→dispute ×1 |
| urgency | 79.3% (46/58) | medium→low ×6, low→medium ×5, high→medium ×1 |
| employment_type | 96.8% (61/63) | probation→unknown ×1, fixed_term→unknown ×1 |
| worker_status | 68.4% (13/19) | employed→left ×2, unknown→employed ×2, employed→unknown ×1, unknown→left ×1 |
| workplace_size | 100.0% (24/24) |  |
| visa_type | 84.2% (16/19) | unknown→E-9 ×3 |
| compliance | 80.0% (4/5) | needs_review→violation ×1 |

language (규칙 기반): 100.0% (75/75)

## 근거 조문 (legal_refs)

- 정확 일치 (n=28): P 0.52 / R 0.66 / F1 0.58
- 코퍼스에 없는 조문 인용(검증에서 제거): 0건

## primary 오답

| id | 본문 | 정답 | 예측 | 모델이 쓴 쟁점 |
|---|---|---|---|---|
| q068 | Khi nào tôi được nhận trợ cấp thôi việc? | RETIREMENT.SEVERANCE | SOCIAL_INSURANCE.EMPLOYMENT | 실업급여를 받을 수 있는 시기는 언제인가요? |
| q090 | เงินชดเชยเมื่อลาออกได้รับเมื่อใด? | RETIREMENT.SEVERANCE | WAGE.SETTLEMENT | 퇴직 시 금품청산 기한은 언제인가? |
| h003 | 지금 사장이 여권 달라고 해서 안 주니까 때렸어요 어떡해요 | MISTREATMENT.HARASSMENT | STAY.DOCUMENTS | 사장이 여권을 요구하여 주지 않자 폭행한 상황에서 어떻게 대처해야 하는가? |
| h023 | 저 17살인데 밤 11시까지 알바해도 되나요? | WORKTIME.SHIFT | WORKTIME.LIMIT | 17세 청소년이 밤 11시까지 아르바이트를 해도 되는지 여부 |
| h029 | Khi về nước tôi có lấy lại được tiền lương hưu đã đóng không | SOCIAL_INSURANCE.PENSION | RETIREMENT.EPS_DEPARTURE | 출국 시 퇴직금 대체 보험(출국만기보험)을 받을 수 있는지 여부 |
| c003 | 월 급여에는 연장·야간·휴일근로수당이 모두 포함된 것으로 한다. | WAGE.ALLOWANCE | WAGE.PAYMENT | 월 급여에 연장·야간·휴일근로수당이 포함된 것으로 하는 조항의 적법성 여부 |
| a005 | 제69조(선박등의 검색 및 심사) ① 선박등이 출입국항에 출ㆍ입항할 때에는 출입국관리공무원의 검색을 받아야  | OUT_OF_SCOPE.OTHER_LEGAL | META.ADMIN | 출입국항에 출·입항하는 선박등의 검색 및 심사 절차는 어떻게 되는가? |
