"""시드 정답 대비 추출 품질 평가.

    python -m pipeline.evaluate --model solar-pro2

store 에 저장된 결과 중 현재 taxonomy·프롬프트로 만든 것만 평가한다 (store 의 cache_key 로 매칭).
리포트는 pipeline/reports/ 에 마크다운으로 남긴다.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from pipeline.extract import plan_jobs
from pipeline.prompt import PROMPT_VERSION, prompt_fingerprint
from pipeline.sources import Item, load_law_gold_items, load_seed_items
from pipeline.splits import load_splits
from pipeline.store import DEFAULT_DB, Store
from pipeline.taxonomy import CONTENT_TYPES, REPO_ROOT, load_guide_sections, load_taxonomy

REPORT_DIR = REPO_ROOT / "pipeline" / "reports"
ATTRS = (
    "intent", "urgency", "employment_type", "worker_status", "workplace_size", "visa_type", "compliance", "provision_type",
)


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


def bootstrap_ci(hits: list[bool], n_boot: int = 2000, seed: int = 0) -> tuple[float, float]:
    """정확도의 95% 구간. 시드 100여 건이면 폭이 10%p 가까이 된다 — 작은 차이를 개선으로 읽지 않기 위한 기준."""
    if not hits:
        return 0.0, 0.0
    rng = random.Random(seed)
    n = len(hits)
    stats = sorted(sum(hits[rng.randrange(n)] for _ in range(n)) / n for _ in range(n_boot))
    return stats[int(0.025 * n_boot)], stats[int(0.975 * n_boot) - 1]


def per_label_table(pairs: list[tuple[str, str]]) -> tuple[list[str], float]:
    """대분류 단위 정밀도·재현율·F1. macro-F1 은 정답에 한 번이라도 나온 대분류의 평균이다."""
    gold_c, pred_c, tp_c = Counter(), Counter(), Counter()
    for gold, pred in pairs:
        g, p = _parent(gold), _parent(pred)
        gold_c[g] += 1
        pred_c[p] += 1
        tp_c[g] += g == p
    rows = ["| 대분류 | 정답 수 | 예측 수 | P | R | F1 |", "|---|---:|---:|---:|---:|---:|"]
    f1s = []
    for label in sorted(gold_c, key=lambda k: -gold_c[k]):
        tp = tp_c[label]
        p = tp / pred_c[label] if pred_c[label] else 0.0
        r = tp / gold_c[label]
        f1 = 2 * p * r / (p + r) if p + r else 0.0
        f1s.append(f1)
        rows.append(f"| {label} | {gold_c[label]} | {pred_c[label]} | {p:.2f} | {r:.2f} | {f1:.2f} |")
    return rows, sum(f1s) / len(f1s) if f1s else 0.0


def evaluate(pairs: list[tuple[Item, dict]], show_errors: bool = True) -> tuple[str, dict]:
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

    hits = [r["labels"]["primary"] == it.gold["primary"] for it, r in groups["전체"]]
    lo, hi = bootstrap_ci(hits)
    summary.update(primary_exact_ci=(lo, hi), macro_f1_parent=0.0)
    lines += ["", f"primary 세분류 정확도 95% 신뢰구간 (bootstrap, 표본 단위): {lo:.1%} ~ {hi:.1%}", ""]

    table, macro = per_label_table([(it.gold["primary"], r["labels"]["primary"]) for it, r in groups["전체"]])
    summary["macro_f1_parent"] = macro
    lines += ["## 대분류별 (primary)", "", f"macro-F1 {macro:.3f}", "", *table, ""]

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

    # 게이트의 대응 비교(같은 항목의 정오 변화)용
    summary["item_hits"] = {it.id: r["labels"]["primary"] == it.gold["primary"] for it, r in groups["전체"]}

    errors = [(it, r) for it, r in groups["전체"] if r["labels"]["primary"] != it.gold["primary"]]
    lines += ["## primary 오답", ""]
    if not show_errors:
        # test 오답을 보고 프롬프트를 고치면 test 가 dev 가 된다
        lines.append(f"평가 전용 세트라 오답 {len(errors)}건의 내용은 표시하지 않는다.")
        return "\n".join(lines), summary
    lines += ["| id | 본문 | 정답 | 예측 | 모델이 쓴 쟁점 |", "|---|---|---|---|---|"]
    for it, r in errors:
        text = it.text.replace("\n", " ").replace("|", "/")[:60]
        issue = r["labels"].get("issue", "").replace("|", "/")[:80]
        lines.append(f"| {it.id} | {text} | {it.gold['primary']} | {r['labels']['primary']} | {issue} |")

    return "\n".join(lines), summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", default="solar-pro2")
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--split", choices=["dev", "test", "all", "laws"], default="dev",
                        help="laws = 무작위 조문 표본 60건 정답")
    args = parser.parse_args(argv)

    tax = load_taxonomy()
    items = load_law_gold_items() if args.split == "laws" else load_seed_items()
    if args.split in ("dev", "test"):
        splits = load_splits()
        items = [it for it in items if splits.get(it.id) == args.split]
    jobs = plan_jobs(tax, items, args.model)
    results = Store(Path(args.db)).fetch([j.key for j in jobs])
    pairs = [(j.item, results[j.key]) for j in jobs if j.key in results and results[j.key]["status"] == "ok"]
    missing = len(jobs) - len(pairs)
    if not pairs:
        print("평가할 결과가 없습니다. 먼저 python -m pipeline.run --source seeds 를 실행하세요.")
        return 1

    # test 와 조문 표본은 프롬프트를 고칠 때 보지 않는다
    body, summary = evaluate(pairs, show_errors=args.split not in ("test", "laws"))
    header = (
        f"# 추출 평가: {args.model} / taxonomy v{tax.version} / prompt {PROMPT_VERSION} / split {args.split}\n\n"
        f"시드 {len(jobs)}건 중 평가 {len(pairs)}건 (결과 없음·실패 {missing}건)\n"
    )
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"eval_{args.model}_{PROMPT_VERSION}_{args.split}"
    out = REPORT_DIR / f"{stem}.md"
    out.write_text(header + "\n" + body + "\n", encoding="utf-8")
    # 회귀 게이트가 읽는 요약. 어떤 프롬프트로 만든 점수인지 지문을 함께 남긴다
    (REPORT_DIR / f"{stem}.json").write_text(
        json.dumps(
            {
                "model": args.model,
                "split": args.split,
                "taxonomy_version": tax.version,
                "prompt_version": PROMPT_VERSION,
                "prompt_fp": {ct: prompt_fingerprint(tax, ct) for ct in CONTENT_TYPES},
                "missing": missing,
                **summary,
            },
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
    print(header)
    print({k: round(v, 3) if isinstance(v, float) else v for k, v in summary.items()})
    print(f"리포트: {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
