"""
Phase 2 — 질의 세트 100건을 bench/queries.jsonl 로 고정한다.

매 실행마다 질의가 달라지면 3회차 비교가 성립하지 않으므로 파일로 못 박는다.

구성:
  관련 90건 — 임금·근로시간·휴일·4대보험·해고·수습·숙소·산재·체류·퇴직
  무관 10건 — 법령과 무관(날씨·맛집 등). 임계값 미달로 hits:0 이 나와야 정상이며,
              "기준 미달을 걸러냈는가"를 보여주는 유일한 실측 근거다.
  언어      — 지원 6개 언어(korean/english/chinese/vietnamese/japanese/thai)에 배분

실행:
  .venv/bin/python bench/build_queries.py
"""

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "queries.jsonl"

# (lang, category, text) — expect_hits 는 무관 질의만 0, 나머지는 None(기대값 미지정)
RELEVANT = [
    # --- korean 30 ---
    ("korean", "wage", "최저임금은 얼마인가요?"),
    ("korean", "wage", "월급을 제때 안 주면 어떻게 하나요?"),
    ("korean", "wage", "야간에 일하면 수당을 더 받나요?"),
    ("korean", "wage", "연장근로를 하면 수당을 얼마나 더 받나요?"),
    ("korean", "wage", "회사가 도산하면 밀린 임금을 받을 수 있나요?"),
    ("korean", "wage", "사장이 임금을 일방적으로 깎을 수 있나요?"),
    ("korean", "worktime", "하루에 최대 몇 시간까지 일할 수 있나요?"),
    ("korean", "worktime", "일주일에 최대 몇 시간 일할 수 있나요?"),
    ("korean", "worktime", "휴게시간은 얼마나 주어야 하나요?"),
    ("korean", "worktime", "연장근로는 주 몇 시간까지 가능한가요?"),
    ("korean", "holiday", "연차휴가는 며칠인가요?"),
    ("korean", "holiday", "주휴일은 반드시 줘야 하나요?"),
    ("korean", "holiday", "1년 미만 근무했는데 연차가 있나요?"),
    ("korean", "holiday", "출산전후휴가는 며칠인가요?"),
    ("korean", "insurance", "외국인도 국민연금에 가입해야 하나요?"),
    ("korean", "insurance", "건강보험료는 누가 부담하나요?"),
    ("korean", "insurance", "고용보험에 가입하면 실업급여를 받을 수 있나요?"),
    ("korean", "insurance", "4대보험 가입은 의무인가요?"),
    ("korean", "dismissal", "해고를 당하면 예고를 받아야 하나요?"),
    ("korean", "dismissal", "부당해고를 당하면 어디에 구제를 신청하나요?"),
    ("korean", "dismissal", "회사가 정당한 이유 없이 해고할 수 있나요?"),
    ("korean", "probation", "수습기간에도 최저임금을 받나요?"),
    ("korean", "probation", "수습기간은 최대 얼마나 되나요?"),
    ("korean", "housing", "회사가 기숙사 비용을 임금에서 공제할 수 있나요?"),
    ("korean", "housing", "기숙사 시설에 대한 기준이 있나요?"),
    ("korean", "injury", "일하다 다쳤는데 치료비는 누가 내나요?"),
    ("korean", "injury", "산재로 일을 못하면 휴업급여를 받나요?"),
    ("korean", "visa", "고용주가 여권을 보관해도 되나요?"),
    ("korean", "visa", "외국인근로자가 사업장을 변경할 수 있나요?"),
    ("korean", "severance", "퇴직금은 언제부터 받을 수 있나요?"),
    # --- english 14 ---
    ("english", "wage", "What is the minimum wage in Korea?"),
    ("english", "wage", "What happens if my employer does not pay my wages?"),
    ("english", "wage", "Do I get extra pay for night work?"),
    ("english", "worktime", "How many hours can I work per week?"),
    ("english", "worktime", "How long a break am I entitled to during the workday?"),
    ("english", "holiday", "Am I entitled to paid annual leave?"),
    ("english", "holiday", "How long is maternity leave?"),
    ("english", "insurance", "Do foreign workers have to join the national pension?"),
    ("english", "dismissal", "How much notice must my employer give before dismissal?"),
    ("english", "probation", "Is there a limit to the probation period?"),
    ("english", "housing", "Can my employer deduct dormitory costs from my salary?"),
    ("english", "injury", "Who pays for treatment if I get injured at work?"),
    ("english", "visa", "Can my employer keep my passport?"),
    ("english", "severance", "Is severance pay mandatory?"),
    # --- chinese 12 ---
    ("chinese", "wage", "韩国的最低工资是多少？"),
    ("chinese", "wage", "拖欠工资时应该怎么办？"),
    ("chinese", "wage", "加班费怎么计算？"),
    ("chinese", "worktime", "每周最多可以工作多少小时？"),
    ("chinese", "holiday", "年休假有几天？"),
    ("chinese", "insurance", "外国劳动者需要加入国民年金吗？"),
    ("chinese", "dismissal", "被解雇前公司必须提前通知吗？"),
    ("chinese", "probation", "试用期也有最低工资保障吗？"),
    ("chinese", "housing", "公司可以从工资中扣除宿舍费吗？"),
    ("chinese", "injury", "工伤的医疗费由谁承担？"),
    ("chinese", "visa", "雇主可以扣押我的护照吗？"),
    ("chinese", "severance", "退职金什么时候可以领取？"),
    # --- vietnamese 12 ---
    ("vietnamese", "wage", "Mức lương tối thiểu ở Hàn Quốc là bao nhiêu?"),
    ("vietnamese", "wage", "Nếu công ty không trả lương thì tôi phải làm gì?"),
    ("vietnamese", "wage", "Tiền làm thêm giờ được tính thế nào?"),
    ("vietnamese", "worktime", "Một tuần được làm việc tối đa bao nhiêu giờ?"),
    ("vietnamese", "holiday", "Tôi được nghỉ phép năm bao nhiêu ngày?"),
    ("vietnamese", "insurance", "Người lao động nước ngoài có phải tham gia bảo hiểm y tế không?"),
    ("vietnamese", "dismissal", "Công ty có phải báo trước khi sa thải không?"),
    ("vietnamese", "probation", "Trong thời gian thử việc có được hưởng lương tối thiểu không?"),
    ("vietnamese", "housing", "Công ty có được trừ tiền ký túc xá vào lương không?"),
    ("vietnamese", "injury", "Ai trả chi phí điều trị khi bị tai nạn lao động?"),
    ("vietnamese", "visa", "Chủ sử dụng lao động có được giữ hộ chiếu của tôi không?"),
    ("vietnamese", "severance", "Khi nào tôi được nhận trợ cấp thôi việc?"),
    # --- japanese 11 ---
    ("japanese", "wage", "韓国の最低賃金はいくらですか？"),
    ("japanese", "wage", "残業手当はどのように計算されますか？"),
    ("japanese", "worktime", "週に何時間まで働けますか？"),
    ("japanese", "holiday", "年次有給休暇は何日ですか？"),
    ("japanese", "insurance", "外国人も国民年金に加入する必要がありますか？"),
    ("japanese", "dismissal", "解雇される前に予告はありますか？"),
    ("japanese", "probation", "試用期間中も最低賃金は適用されますか？"),
    ("japanese", "housing", "会社が寮費を給料から差し引くことはできますか？"),
    ("japanese", "injury", "労災の治療費は誰が負担しますか？"),
    ("japanese", "visa", "雇用主がパスポートを預かってもいいですか？"),
    ("japanese", "severance", "退職金はいつから受け取れますか？"),
    # --- thai 11 ---
    ("thai", "wage", "ค่าแรงขั้นต่ำในเกาหลีเท่าไหร่?"),
    ("thai", "wage", "ค่าล่วงเวลาคำนวณอย่างไร?"),
    ("thai", "worktime", "ทำงานได้สูงสุดกี่ชั่วโมงต่อสัปดาห์?"),
    ("thai", "holiday", "มีวันลาพักร้อนกี่วัน?"),
    ("thai", "insurance", "แรงงานต่างชาติต้องเข้าประกันบำนาญแห่งชาติหรือไม่?"),
    ("thai", "dismissal", "บริษัทต้องแจ้งล่วงหน้าก่อนเลิกจ้างหรือไม่?"),
    ("thai", "probation", "ช่วงทดลองงานได้รับค่าแรงขั้นต่ำหรือไม่?"),
    ("thai", "housing", "บริษัทหักค่าหอพักจากเงินเดือนได้หรือไม่?"),
    ("thai", "injury", "ใครจ่ายค่ารักษาพยาบาลเมื่อบาดเจ็บจากการทำงาน?"),
    ("thai", "visa", "นายจ้างสามารถเก็บหนังสือเดินทางของฉันได้หรือไม่?"),
    ("thai", "severance", "เงินชดเชยเมื่อลาออกได้รับเมื่อใด?"),
]

IRRELEVANT = [
    ("korean", "오늘 서울 날씨 어때?"),
    ("korean", "근처에 맛있는 식당 추천해줘"),
    ("korean", "어제 축구 경기 결과 알려줘"),
    ("english", "What is the best kimchi recipe?"),
    ("english", "Recommend a good movie to watch tonight."),
    ("chinese", "明天首尔天气怎么样？"),
    ("chinese", "推荐一首好听的歌"),
    ("vietnamese", "Gợi ý cho tôi một quán cà phê ngon ở Seoul"),
    ("japanese", "面白いアニメを教えてください"),
    ("thai", "แนะนำสถานที่ท่องเที่ยวในกรุงโซล"),
]


def main() -> None:
    rows = []
    for i, (lang, category, text) in enumerate(RELEVANT, start=1):
        rows.append(
            {"query_id": f"q{i:03d}", "lang": lang, "category": category, "text": text, "expect_hits": None}
        )
    for j, (lang, text) in enumerate(IRRELEVANT, start=len(RELEVANT) + 1):
        rows.append(
            {"query_id": f"q{j:03d}", "lang": lang, "category": "irrelevant", "text": text, "expect_hits": 0}
        )

    assert len(rows) == 100, f"질의 수가 100이 아닙니다: {len(rows)}"
    assert sum(1 for r in rows if r["category"] == "irrelevant") == 10

    with OUT.open("w", encoding="utf-8") as fp:
        for row in rows:
            fp.write(json.dumps(row, ensure_ascii=False) + "\n")

    from collections import Counter

    print(f"{OUT} — {len(rows)}건")
    print("언어:", dict(Counter(r["lang"] for r in rows)))
    print("카테고리:", dict(Counter(r["category"] for r in rows)))


if __name__ == "__main__":
    main()
