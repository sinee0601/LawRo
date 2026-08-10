"""
국가법령정보 공동활용 API로 외국인 노동자 관련 법령 본문을 조문 단위로 수집한다.

사용 전 준비:
  1. https://open.law.go.kr 에서 오픈 API 활용 신청 (승인 즉시 발급)
  2. backend/.env 에 LAW_GO_KR_OC=<이메일 아이디 앞부분> 추가

실행:
  .venv/bin/python bench/fetch_laws.py

산출물:
  backend/data/raw_laws/<법령명>.json  — 조문 단위 레코드 배열
  backend/data/raw_laws/_manifest.json — 수집 메타(법령별 조문 수, 시행일자, 수집 시각)
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "backend" / "data" / "raw_laws"

SEARCH_URL = "https://www.law.go.kr/DRF/lawSearch.do"
SERVICE_URL = "https://www.law.go.kr/DRF/lawService.do"

# 지원서 질의 카테고리(임금·근로시간·휴일·4대보험·해고·수습·숙소)를 커버하는 법령 집합
TARGET_LAWS = [
    "근로기준법",
    "최저임금법",
    "외국인근로자의 고용 등에 관한 법률",
    "산업안전보건법",
    "산업재해보상보험법",
    "고용보험법",
    "국민건강보험법",
    "국민연금법",
    "임금채권보장법",
    "근로자퇴직급여 보장법",
    "기간제 및 단시간근로자 보호 등에 관한 법률",
    "출입국관리법",
]

REQUEST_SLEEP = 0.5  # 공공 API 예의상 간격


class LawApiError(RuntimeError):
    """법제처가 JSON 대신 HTML 안내 페이지를 돌려준 경우(미신청 API, 잘못된 OC 등)."""


def _parse_json(resp: requests.Response) -> Dict[str, Any]:
    """오류 시 HTTP 200 + HTML 안내 페이지가 오므로 본문을 보고 판별한다."""
    try:
        return resp.json()
    except ValueError:
        body = re.sub(r"(?s)<(script|style|head).*?</\1>", " ", resp.text)
        message = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)).strip()
        raise LawApiError(message[:300] or "빈 응답") from None


def _as_list(node: Any) -> List[Any]:
    """법령 API는 원소가 1개면 dict, 여러 개면 list로 준다."""
    if node is None:
        return []
    if isinstance(node, list):
        return node
    return [node]


def _clean(text: Any) -> str:
    if text is None:
        return ""
    if isinstance(text, list):
        return "\n".join(_clean(t) for t in text)
    return str(text).replace("\xa0", " ").strip()


def search_law(oc: str, name: str) -> Optional[Dict[str, str]]:
    """법령명으로 검색해 현행 법령의 일련번호(MST)를 찾는다."""
    resp = requests.get(
        SEARCH_URL,
        params={"OC": oc, "target": "law", "type": "JSON", "query": name, "display": "20"},
        timeout=30,
    )
    resp.raise_for_status()
    payload = _parse_json(resp)

    items = _as_list(payload.get("LawSearch", {}).get("law"))
    if not items:
        return None

    # 법령명이 정확히 일치하는 현행 법령을 우선한다(시행령/시행규칙 배제)
    for item in items:
        if _clean(item.get("법령명한글")) == name:
            return {
                "mst": _clean(item.get("법령일련번호")),
                "name": _clean(item.get("법령명한글")),
                "enforce_date": _clean(item.get("시행일자")),
            }
    return None


def fetch_articles(oc: str, mst: str) -> Dict[str, Any]:
    resp = requests.get(
        SERVICE_URL,
        params={"OC": oc, "target": "law", "type": "JSON", "MST": mst},
        timeout=30,
    )
    resp.raise_for_status()
    return _parse_json(resp).get("법령", {})


def render_article(article: Dict[str, Any]) -> str:
    """조문 하나를 항·호까지 펼쳐 하나의 텍스트로 만든다."""
    parts: List[str] = []

    title = _clean(article.get("조문제목"))
    body = _clean(article.get("조문내용"))
    if body:
        parts.append(body)
    elif title:
        parts.append(title)

    for hang in _as_list(article.get("항")):
        if not isinstance(hang, dict):
            continue
        hang_text = _clean(hang.get("항내용"))
        if hang_text:
            parts.append(hang_text)

        for ho in _as_list(hang.get("호")):
            if not isinstance(ho, dict):
                continue
            ho_text = _clean(ho.get("호내용"))
            if ho_text:
                parts.append("  " + ho_text)

            for mok in _as_list(ho.get("목")):
                if not isinstance(mok, dict):
                    continue
                mok_text = _clean(mok.get("목내용"))
                if mok_text:
                    parts.append("    " + mok_text)

    return "\n".join(p for p in parts if p)


def collect(oc: str, name: str) -> Optional[Dict[str, Any]]:
    found = search_law(oc, name)
    if not found:
        print(f"  [SKIP] 검색 결과 없음: {name}")
        return None

    time.sleep(REQUEST_SLEEP)
    law = fetch_articles(oc, found["mst"])
    basic = law.get("기본정보", {})
    articles_node = law.get("조문", {}).get("조문단위")

    records: List[Dict[str, Any]] = []
    for article in _as_list(articles_node):
        if not isinstance(article, dict):
            continue
        # 편/장/절 제목 줄은 조문여부가 "전문"으로 온다 — 본문이 아니므로 제외
        if _clean(article.get("조문여부")) == "전문":
            continue

        text = render_article(article)
        if len(text) < 20:  # 삭제 조문 등
            continue

        no = _clean(article.get("조문번호"))
        branch = _clean(article.get("조문가지번호"))
        label = f"제{no}조" + (f"의{branch}" if branch and branch != "0" else "")

        records.append(
            {
                "law_name": found["name"],
                "article_no": label,
                "article_title": _clean(article.get("조문제목")),
                "text": text,
                "enforce_date": _clean(basic.get("시행일자")) or found["enforce_date"],
                "source_url": f"https://www.law.go.kr/DRF/lawService.do?target=law&MST={found['mst']}",
            }
        )

    if not records:
        print(f"  [SKIP] 조문 파싱 0건: {name}")
        return None

    print(f"  [OK] {found['name']}: 조문 {len(records)}건 (시행 {records[0]['enforce_date']})")
    return {"meta": found, "records": records}


def main() -> int:
    load_dotenv(REPO_ROOT / "backend" / ".env")
    oc = os.getenv("LAW_GO_KR_OC")
    if not oc:
        print(
            "LAW_GO_KR_OC 가 없습니다.\n"
            "  1) https://open.law.go.kr 에서 오픈 API 활용 신청\n"
            "  2) backend/.env 에 LAW_GO_KR_OC=<이메일 아이디 앞부분> 추가",
            file=sys.stderr,
        )
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest: List[Dict[str, Any]] = []

    for name in TARGET_LAWS:
        print(f"수집: {name}", flush=True)
        try:
            result = collect(oc, name)
        except LawApiError as exc:
            # 계정 설정 문제이므로 나머지 법령도 전부 같은 결과다. 즉시 중단한다.
            print(f"\n[중단] 법제처 API가 데이터 대신 안내 페이지를 반환했습니다:\n  {exc}\n", file=sys.stderr)
            return 1
        except requests.HTTPError as exc:
            print(f"  [FAIL] HTTP {exc.response.status_code}: {name}", file=sys.stderr)
            continue
        except Exception as exc:  # 파싱 실패는 건너뛰되 기록
            print(f"  [FAIL] {type(exc).__name__}: {name} — {exc}", file=sys.stderr)
            continue

        if result is None:
            continue

        safe = result["meta"]["name"].replace("/", "_").replace(" ", "_")
        (OUT_DIR / f"{safe}.json").write_text(
            json.dumps(result["records"], ensure_ascii=False, indent=2), encoding="utf-8"
        )
        manifest.append(
            {
                "law_name": result["meta"]["name"],
                "mst": result["meta"]["mst"],
                "article_count": len(result["records"]),
                "enforce_date": result["records"][0]["enforce_date"],
            }
        )
        time.sleep(REQUEST_SLEEP)

    total = sum(m["article_count"] for m in manifest)
    (OUT_DIR / "_manifest.json").write_text(
        json.dumps(
            {
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "law_count": len(manifest),
                "article_total": total,
                "laws": manifest,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"\n완료: 법령 {len(manifest)}개 / 조문 {total}건 → {OUT_DIR}")
    return 0 if manifest else 1


if __name__ == "__main__":
    sys.exit(main())
