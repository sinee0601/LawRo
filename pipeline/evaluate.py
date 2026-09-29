"""시드 정답 대비 추출 품질 평가.

    python -m pipeline.evaluate --model solar-pro2

store 에 저장된 결과 중 현재 taxonomy·프롬프트로 만든 것만 평가한다 (store 의 cache_key 로 매칭).
리포트는 pipeline/reports/ 에 마크다운으로 남긴다.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from pipeline.extract import plan_jobs
from pipeline.prompt import PROMPT_VERSION
from pipeline.sources import Item, load_seed_items
from pipeline.store import DEFAULT_DB, Store
from pipeline.taxonomy import REPO_ROOT, load_guide_sections, load_taxonomy

REPORT_DIR = REPO_ROOT / "pipeline" / "reports"
ATTRS = ("intent", "urgency", "employment_type", "worker_status", "workplace_size", "visa_type", "compliance")


def _parent(label: str) -> str:
    return label.split(".")[0]


def _ratio(num: int, den: int) -> str:
    return f"{num / den:.1%} ({num}/{den})" if den else "-"


def _prf(tp: int, fp: int, fn: int) -> str:
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return f"P {p:.2f} / R {r:.2f} / F1 {f:.2f}"


def _normalize(text: str) -> str:
    return re.sub(r"[\s\W_]+", "", text)


def leaked_ids(items: list[Item]) -> set[str]:
    """프롬프트에 들어가는 가이드 예시와 본문이 같은 시드.

    정답이 프롬프트에 있는 셈이라 따로 떼어 보고한다. 번역본(q041 등)은 잡지 못하므로
    '나머지' 그룹도 완전히 깨끗하지는 않다.
    """
    guide = _normalize(load_guide_sections())
    exact = {it.id for it in items if len(_normalize(it.text)) >= 8 and _normalize(it.text) in guide}
    # 판단 대기였다가 경계 사례로 옮겨 적은 시드는 문장이 조금 달라도 같은 사례다
    resolved = {it.id for it in items if "[확정]" in (it.gold or {}).get("notes", "")}
    return exact | resolved


def evaluate(pairs: list[tuple[Item, dict]]) -> tuple[str, dict]:
    """(시드, 추출 결과) 쌍으로 지표를 계산해 마크다운과 요약 수치를 돌려준다."""
    leaked = leaked_ids([it for it, _ in pairs])
    groups: dict[str, list[tuple[Item, dict]]] = defaultdict(list)
    for item, row in pairs:
        groups["전체"].append((item, row))
        groups["가이드 예시와 동일" if item.id in leaked else "가이드 예시 아님"].append((item, row))
        groups[f"content_type={item.content_type}"].append((item, row))
        groups[f"source={item.source}"].append((item, row))
        if item.content_type == "query":
            groups["query 언어=ko" if item.gold["lang"] == "ko" else "query 언어≠ko"].append((item, row))

    lines = ["## 카테고리", "", "| 그룹 | n | primary 세분류 | primary 대분류 |", "|---|---:|---:|---:|"]
    summary: dict = {}
    for name, rows in groups.items():
        n = len(rows)
        exact = sum(r["labels"]["primary"] == it.gold["primary"] for it, r in rows)
        parent = sum(_parent(r["labels"]["primary"]) == _parent(it.gold["primary"]) for it, r in rows)
        lines.append(f"| {name} | {n} | {_ratio(exact, n)} | {_ratio(parent, n)} |")
        if name == "전체":
            summary.update(n=n, primary_exact=exact / n, primary_parent=parent / n)
        if name == "가이드 예시 아님":
            summary.update(n_clean=n, primary_exact_clean=exact / n)

    # secondary: 라벨 집합 기준 micro P/R
    tp = fp = fn = 0
    for it, r in groups["전체"]:
        gold, pred = set(it.gold.get("secondary", [])), set(r["labels"]["secondary"])
        tp, fp, fn = tp + len(gold & pred), fp + len(pred - gold), fn + len(gold - pred)
    lines += ["", f"secondary (micro): {_prf(tp, fp, fn)}", ""]

    lines += ["## 속성", "", "정답에 값이 있는 항목만 센다. `unknown` 도 정답으로 취급한다 (추측 금지 원칙, GUIDE D9).", ""]
    lines += ["| 속성 | 정확도 | 틀린 예 (정답→예측) |", "|---|---:|---|"]
    for attr in ATTRS:
        rows = [(it, r) for it, r in groups["전체"] if attr in it.gold and attr in r["labels"]]
        if not rows:
            continue
        correct = sum(r["labels"][attr] == it.gold[attr] for it, r in rows)
        wrong = Counter(f"{it.gold[attr]}→{r['labels'][attr]}" for it, r in rows if r["labels"][attr] != it.gold[attr])
        lines.append(f"| {attr} | {_ratio(correct, len(rows))} | {', '.join(f'{k} ×{v}' for k, v in wrong.most_common(4))} |")
        summary[f"attr_{attr}"] = correct / len(rows)

    lang_rows = [(it, r) for it, r in groups["전체"] if it.content_type != "law_article"]
    lang_ok = sum(r["language"] == it.gold["lang"] for it, r in lang_rows)
    lines += ["", f"language (규칙 기반): {_ratio(lang_ok, len(lang_rows))}", ""]

    # legal_refs: 정답에 legal_refs 가 있는 hard 시드만
    ref_rows = [(it, r) for it, r in groups["전체"] if "legal_refs" in it.gold]
    tp = fp = fn = 0
    for it, r in ref_rows:
        gold = {(x["law"], x["article"]) for x in it.gold["legal_refs"]}
        pred = {(x["law"], x["article"]) for x in r["labels"]["legal_refs"]}
        tp, fp, fn = tp + len(gold & pred), fp + len(pred - gold), fn + len(gold - pred)
    hallucinated = sum(i.startswith("ref_not_in_corpus") for _, r in groups["전체"] for i in r["issues"])
    lines += [
        "## 근거 조문 (legal_refs)",
        "",
        f"- 정확 일치 (n={len(ref_rows)}): {_prf(tp, fp, fn)}",
        f"- 코퍼스에 없는 조문 인용(검증에서 제거): {hallucinated}건",
        "",
    ]

    errors = [(it, r) for it, r in groups["전체"] if r["labels"]["primary"] != it.gold["primary"]]
    lines += ["## primary 오답", "", "| id | 본문 | 정답 | 예측 | 모델이 쓴 쟁점 |", "|---|---|---|---|---|"]
    for it, r in errors:
        text = it.text.replace("\n", " ").replace("|", "/")[:60]
        issue = r["labels"].get("issue", "").replace("|", "/")[:80]
        lines.append(f"| {it.id} | {text} | {it.gold['primary']} | {r['labels']['primary']} | {issue} |")

    return "\n".join(lines), summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", default="solar-pro2")
    parser.add_argument("--db", default=str(DEFAULT_DB))
    args = parser.parse_args(argv)

    tax = load_taxonomy()
    items = load_seed_items()
    jobs = plan_jobs(tax, items, args.model)
    results = Store(Path(args.db)).fetch([j.key for j in jobs])
    pairs = [(j.item, results[j.key]) for j in jobs if j.key in results and results[j.key]["status"] == "ok"]
    missing = len(jobs) - len(pairs)
    if not pairs:
        print("평가할 결과가 없습니다. 먼저 python -m pipeline.run --source seeds 를 실행하세요.")
        return 1

    body, summary = evaluate(pairs)
    header = (
        f"# 추출 평가: {args.model} / taxonomy v{tax.version} / prompt {PROMPT_VERSION}\n\n"
        f"시드 {len(jobs)}건 중 평가 {len(pairs)}건 (결과 없음·실패 {missing}건)\n"
    )
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / f"eval_{args.model}_{PROMPT_VERSION}.md"
    out.write_text(header + "\n" + body + "\n", encoding="utf-8")
    print(header)
    print({k: round(v, 3) if isinstance(v, float) else v for k, v in summary.items()})
    print(f"리포트: {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
