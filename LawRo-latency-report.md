# LawRo 챗봇 RAG 구간 지연 실측 리포트

측정일 2026-08-10 · 커밋 `88d4133` · 브랜치 `measure/rag-latency`

## 한 줄 결론

로컬 단일 인스턴스에서 질의 100건을 순차 3회 실행한 결과, 총 지연 p50 1185ms 중
**generate(LLM 생성)가 91%, embed(질의 임베딩 API)가 8%,
search(Chroma 벡터 검색)가 0.5%** 를 차지했다.
지연의 원인 구간은 **외부 API 왕복(generate + embed = 99%)** 이며,
벡터 검색은 병목이 아니다.

검색 품질 쪽에서는 무관 질의 30/30건을 전부 차단했으나,
관련 질의 270건 중 51건(18.9%)이 임계값 미달로 걸러졌고
**그 전부가 비한국어 질의**다 (비한국어 51/180 = 28%, 한국어 0/90 = 0%).
한국어 코퍼스에 맞춰진 단일 임계값 0.3의 한계다.

## 실행 메타

| 항목 | 값 |
|---|---|
| 커밋 | `88d4133` |
| 샘플 수 | 300건 (3회차 × 100질의) |
| 컬렉션 | `lawro_legal_docs` / **1488 vectors** |
| 원본 | 법령 12개 · 조문 1318건 |
| 청킹 | size 800 / overlap 100 |
| 거리함수 | cosine |
| 임계값 | **0.3** (측정 중 고정) |
| Top-k | 2 |
| 임베딩 (색인) | `solar-embedding-1-large-passage` |
| 임베딩 (질의) | `solar-embedding-1-large-query` |
| 생성 | `solar-pro2` |
| 요청 간격 | 1.0s, 순차 단일 실행 |

## 구간별 지연 (전 회차 통합, n=300)

| 구간 | p50 (ms) | p95 (ms) | max (ms) | 평균 | total p50 대비 점유율 |
|---|---:|---:|---:|---:|---:|
| embed (질의 임베딩 API) | 97.6 | 119.6 | 1923.0 | 107.8 | 8.2% |
| search (Chroma 벡터 검색) | 5.8 | 7.5 | 297.9 | 8.7 | 0.5% |
| generate (solar-pro2 생성) | 1072.8 | 2300.1 | 33852.9 | 1315.9 | 90.5% |
| **total** | 1184.8 | 2402.4 | 33979.3 | 1432.5 | 100.0% |

점유율은 각 구간 p50 을 total p50 으로 나눈 값이다. 구간 합이 total 과 정확히 일치하지는 않는다 —
세션 처리·프롬프트 조립 등 계측 구간 밖의 오버헤드가 남아 있기 때문이다.

## 회차 비교 (cold vs warm)

| 회차 | 상태 | n | embed p50 | search p50 | search max | generate p50 | total p50 | total p95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| run1 | cold | 100 | 100.1 | 6.2 | 292.0 | 1119.0 | 1248.7 | 2049.5 |
| run2 | warm | 100 | 94.0 | 5.8 | 286.1 | 1037.9 | 1144.6 | 2522.3 |
| run3 | warm | 100 | 96.8 | 5.4 | 297.9 | 1087.9 | 1216.3 | 2278.0 |

## 성공률

- 전체 성공률 **300/300 (100.0%)**
- 재시도 발생 건수: 0건
- `hits:0`은 실패로 세지 않는다 — 임계값이 정상 동작한 결과이므로 `status:"ok"`이며 아래 임계값 항목에서 따로 집계한다.
- `error_type` 발생 없음 (http_4xx / http_5xx / timeout / retry_exhausted / parse_error 모두 0건)

## 임계값 동작

- 무관 질의 **30/30건 차단** (`hits:0`) — 기대값 대비 일치
- 관련 질의 중 `hits:0` 오탐 **51/270건** (18.9%)
  - 한국어 **0/90건 (0%)**, 비한국어 **51/180건 (28%)**
- top_score 분포 — 무관: max 0.199 / 관련: min 0.220, p50 0.355

**오탐은 전부 비한국어 질의에서 나왔다.** 색인된 법령 원문이 한국어이므로 비한국어 질의는 같은 조문을 찾아도 코사인 점수가 낮게 나온다. 임계값 0.3은 한국어 기준으로 맞춰진 값이고, 무관 질의(max 0.199)와 비한국어 관련 질의(min 0.220)의 점수 구간이 겹쳐 단일 임계값으로는 분리되지 않는다. 언어별 임계값 또는 질의 번역 후 검색이 후속 과제다.

오탐이 난 관련 질의(3회차 중 1회 이상):

| query_id | 언어 | 카테고리 | 질의 | top_score (회차별) |
|---|---|---|---|---|
| q040 | english | probation | Is there a limit to the probation period? | 0.287, 0.287, 0.287 |
| q041 | english | housing | Can my employer deduct dormitory costs from my salary? | 0.220, 0.220, 0.220 |
| q043 | english | visa | Can my employer keep my passport? | 0.246, 0.246, 0.246 |
| q044 | english | severance | Is severance pay mandatory? | 0.275, 0.275, 0.275 |
| q052 | chinese | probation | 试用期也有最低工资保障吗？ | 0.296, 0.296, 0.296 |
| q053 | chinese | housing | 公司可以从工资中扣除宿舍费吗？ | 0.255, 0.255, 0.255 |
| q055 | chinese | visa | 雇主可以扣押我的护照吗？ | 0.261, 0.261, 0.261 |
| q058 | vietnamese | wage | Nếu công ty không trả lương thì tôi phải làm gì? | 0.253, 0.253, 0.253 |
| q065 | vietnamese | housing | Công ty có được trừ tiền ký túc xá vào lương không? | 0.221, 0.221, 0.221 |
| q067 | vietnamese | visa | Chủ sử dụng lao động có được giữ hộ chiếu của tôi không? | 0.298, 0.298, 0.298 |
| q068 | vietnamese | severance | Khi nào tôi được nhận trợ cấp thôi việc? | 0.276, 0.276, 0.276 |
| q076 | japanese | housing | 会社が寮費を給料から差し引くことはできますか？ | 0.235, 0.235, 0.235 |
| q078 | japanese | visa | 雇用主がパスポートを預かってもいいですか？ | 0.277, 0.277, 0.277 |
| q080 | thai | wage | ค่าแรงขั้นต่ำในเกาหลีเท่าไหร่? | 0.299, 0.299, 0.299 |
| q086 | thai | probation | ช่วงทดลองงานได้รับค่าแรงขั้นต่ำหรือไม่? | 0.283, 0.283, 0.283 |
| q087 | thai | housing | บริษัทหักค่าหอพักจากเงินเดือนได้หรือไม่? | 0.239, 0.239, 0.239 |
| q089 | thai | visa | นายจ้างสามารถเก็บหนังสือเดินทางของฉันได้หรือไม่? | 0.277, 0.277, 0.277 |

## 언어별

| 언어 | n | embed p50 | total p50 | 관련 질의 hits:0 비율 |
|---|---:|---:|---:|---:|
| chinese | 42 | 97.8 | 1183.4 | 9/36 (25%) |
| english | 48 | 96.3 | 1120.5 | 12/42 (29%) |
| japanese | 36 | 97.7 | 1191.4 | 6/33 (18%) |
| korean | 99 | 98.0 | 991.5 | 0/90 (0%) |
| thai | 36 | 101.2 | 2017.3 | 12/33 (36%) |
| vietnamese | 39 | 96.5 | 1673.1 | 12/36 (33%) |

## 한계

- 로컬 단일 인스턴스(macOS, Python 3.9, Chroma 임베디드) — 실서비스 트래픽이 아니다.
- 순차 요청만 측정했다. **동시성·부하는 측정하지 않았다.**
- 질의 100건 규모, 3회차. 외부 API 지연은 측정 시점의 네트워크·서버 상태에 따라 달라진다.
- 세션 백엔드를 `memory` 로 고정했다(Firestore 자격증명 없음). Firestore 왕복은 total_ms 에 포함되지 않는다.
- 생성 구간은 응답 길이에 비례하므로 질의 구성에 의존한다.
- 관련 질의 90건에는 정답 조문을 미리 지정하지 않았다. 따라서 `hits>0`은 "임계값을 넘었다"는
  뜻이지 "옳은 조문을 찾았다"는 뜻이 아니다. 검색 정확도(precision) 측정은 별도 과제다.

## 재현

```bash
.venv/bin/python bench/fetch_laws.py
.venv/bin/python bench/build_index.py --reset
for r in 1 2 3; do .venv/bin/python bench/run_bench.py --run $r --out bench/raw/run$r.jsonl; done
.venv/bin/python bench/aggregate.py
```
