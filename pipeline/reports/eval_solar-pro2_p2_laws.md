# 추출 평가: solar-pro2 / taxonomy v2.0.0 / prompt p2 / split laws

시드 60건 중 평가 60건 (결과 없음·실패 0건)

## 카테고리

| 그룹 | n | primary 세분류 | primary 대분류 |
|---|---:|---:|---:|
| 전체 | 60 | 88.3% (53/60) | 88.3% (53/60) |
| 가이드 예시 아님 | 60 | 88.3% (53/60) | 88.3% (53/60) |
| content_type=law_article | 60 | 88.3% (53/60) | 88.3% (53/60) |
| source=gold:laws | 60 | 88.3% (53/60) | 88.3% (53/60) |

primary 세분류 정확도 95% 신뢰구간 (bootstrap, 표본 단위): 80.0% ~ 95.0%

## 대분류별 (primary)

macro-F1 0.795

| 대분류 | 정답 수 | 예측 수 | P | R | F1 |
|---|---:|---:|---:|---:|---:|
| INJURY | 21 | 21 | 1.00 | 1.00 | 1.00 |
| SOCIAL_INSURANCE | 18 | 18 | 0.89 | 0.89 | 0.89 |
| STAY | 6 | 4 | 1.00 | 0.67 | 0.80 |
| CONTRACT | 4 | 4 | 0.75 | 0.75 | 0.75 |
| RETIREMENT | 4 | 3 | 1.00 | 0.75 | 0.86 |
| WAGE | 3 | 4 | 0.75 | 1.00 | 0.86 |
| GENERAL | 2 | 2 | 0.50 | 0.50 | 0.50 |
| LEAVE | 1 | 1 | 1.00 | 1.00 | 1.00 |
| OUT_OF_SCOPE | 1 | 3 | 0.33 | 1.00 | 0.50 |


secondary (micro): P 0.00 / R 0.00 / F1 0.00

## 속성

정답에 값이 있는 항목만 센다. `unknown` 도 정답으로 취급한다 (추측 금지 원칙, GUIDE D9).

| 속성 | 정확도 | 틀린 예 (정답→예측) |
|---|---:|---|
| provision_type | 61.7% (37/60) | administration→right_duty ×13, procedure→right_duty ×7, administration→procedure ×1, procedure→general ×1 |

language (규칙 기반): -

## 근거 조문 (legal_refs)

- 정확 일치 (n=0): P 0.00 / R 0.00 / F1 0.00
- 코퍼스에 없는 조문 인용(검증에서 제거): 0건

## primary 오답

평가 전용 세트라 오답 7건의 내용은 표시하지 않는다.
