"""작성 언어 감지 — LLM 에 맡기지 않는다 (GUIDE D10).

대상 언어가 6개뿐이고 문자 체계가 대부분 달라서 유니코드 범위와 베트남어 성조 문자만으로 충분하다.
"""

from __future__ import annotations

import re

_HANGUL = re.compile(r"[가-힣ᄀ-ᇿ㄰-㆏]")
_THAI = re.compile(r"[฀-๿]")
_KANA = re.compile(r"[぀-ヿ]")
_HAN = re.compile(r"[一-鿿]")
# 베트남어에만 쓰이는 성조·모음 결합 문자 (프랑스어 등과 겹치지 않는 것 위주)
_VIETNAMESE = re.compile(r"[ăđơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]", re.IGNORECASE)
_LATIN = re.compile(r"[A-Za-z]")
# 대문자·숫자만으로 된 토큰은 이름(NGUYEN VAN A)이나 코드(E-9, EPS-TOPIK)라 언어를 알려주지 않는다
_CAPS_TOKEN = re.compile(r"\b[A-Z0-9][A-Z0-9\-.]*\b")


def detect_language(text: str) -> str:
    text = _CAPS_TOKEN.sub(" ", text).strip() or text
    # 일본어는 한자를 섞어 쓰므로 가나가 하나라도 있으면 일본어로 본다
    if _KANA.search(text):
        return "ja"
    # 문자 수가 가장 많은 문자 체계를 고른다. "E-9인데 ..." 는 한국어, "Can I get 퇴직금?" 은 영어
    counts = {
        "ko": len(_HANGUL.findall(text)),
        "th": len(_THAI.findall(text)),
        "zh": len(_HAN.findall(text)),
        "latin": len(_LATIN.findall(text)) + len(_VIETNAMESE.findall(text)),
    }
    script, n = max(counts.items(), key=lambda kv: kv[1])
    if not n:
        return "other"
    if script == "latin":
        return "vi" if _VIETNAMESE.search(text) else "en"
    return script
