# 추출 평가: solar-pro2 / taxonomy v2.0.0 / prompt p2 / split test

시드 79건 중 평가 79건 (결과 없음·실패 0건)

## 카테고리

| 그룹 | n | primary 세분류 | primary 대분류 |
|---|---:|---:|---:|
| 전체 | 79 | 92.4% (73/79) | 96.2% (76/79) |
| 가이드 예시 아님 | 72 | 91.7% (66/72) | 95.8% (69/72) |
| content_type=query | 70 | 91.4% (64/70) | 95.7% (67/70) |
| source=seed:bench | 49 | 95.9% (47/49) | 95.9% (47/49) |
| query 언어=ko | 32 | 90.6% (29/32) | 100.0% (32/32) |
| 가이드 예시와 동일 | 7 | 100.0% (7/7) | 100.0% (7/7) |
| query 언어≠ko | 38 | 92.1% (35/38) | 92.1% (35/38) |
| source=seed:hard | 30 | 86.7% (26/30) | 96.7% (29/30) |
| content_type=contract_clause | 5 | 100.0% (5/5) | 100.0% (5/5) |
| content_type=law_article | 4 | 100.0% (4/4) | 100.0% (4/4) |

primary 세분류 정확도 95% 신뢰구간 (bootstrap, 표본 단위): 86.1% ~ 97.5%

## 대분류별 (primary)

macro-F1 0.962

| 대분류 | 정답 수 | 예측 수 | P | R | F1 |
|---|---:|---:|---:|---:|---:|
| WAGE | 23 | 24 | 0.96 | 1.00 | 0.98 |
| OUT_OF_SCOPE | 13 | 13 | 1.00 | 1.00 | 1.00 |
| WORKTIME | 12 | 12 | 1.00 | 1.00 | 1.00 |
| RETIREMENT | 7 | 6 | 0.83 | 0.71 | 0.77 |
| SOCIAL_INSURANCE | 6 | 6 | 0.83 | 0.83 | 0.83 |
| CONTRACT | 6 | 6 | 1.00 | 1.00 | 1.00 |
| STAY | 5 | 5 | 1.00 | 1.00 | 1.00 |
| INJURY | 2 | 2 | 1.00 | 1.00 | 1.00 |
| MISTREATMENT | 2 | 2 | 1.00 | 1.00 | 1.00 |
| LEAVE | 2 | 2 | 1.00 | 1.00 | 1.00 |
| TERMINATION | 1 | 1 | 1.00 | 1.00 | 1.00 |


secondary (micro): P 0.25 / R 0.43 / F1 0.32

## 속성

정답에 값이 있는 항목만 센다. `unknown` 도 정답으로 취급한다 (추측 금지 원칙, GUIDE D9).

| 속성 | 정확도 | 틀린 예 (정답→예측) |
|---|---:|---|
| intent | 82.8% (48/58) | procedure→info ×7, dispute→info ×2, info→dispute ×1 |
| urgency | 84.5% (49/58) | low→medium ×4, medium→low ×4, high→medium ×1 |
| employment_type | 95.2% (60/63) | probation→unknown ×1, fixed_term→unknown ×1, unknown→fixed_term ×1 |
| worker_status | 78.9% (15/19) | unknown→employed ×2, employed→left ×1, unknown→left ×1 |
| workplace_size | 100.0% (24/24) |  |
| visa_type | 84.2% (16/19) | unknown→E-9 ×3 |
| compliance | 60.0% (3/5) | needs_review→violation ×2 |
| provision_type | 100.0% (4/4) |  |

language (규칙 기반): 100.0% (75/75)

## 근거 조문 (legal_refs)

- 정확 일치 (n=28): P 0.55 / R 0.69 / F1 0.61
- 코퍼스에 없는 조문 인용(검증에서 제거): 0건

## primary 오답

평가 전용 세트라 오답 6건의 내용은 표시하지 않는다.
