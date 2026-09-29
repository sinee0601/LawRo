"""사람 판정용 라벨링 화면 생성과 결과 반영.

    python -m pipeline.annotate build            # pipeline/out/annotate.html 생성
    python -m pipeline.annotate ingest result.json

두 가지 작업을 한 화면에서 한다.
1. adjudicate — 조문 표본에서 Claude(블라인드)와 solar 가 다르게 붙인 라벨 판정.
   후보의 출처는 숨기고 순서를 섞는다 (출처를 알면 판정이 쏠린다).
2. iaa — 시드 일부를 정답을 보지 않고 다시 라벨링해 라벨러 간 일치도(Cohen's kappa)를 잰다.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

from pipeline.extract import plan_jobs
from pipeline.sources import load_law_items, load_seed_items
from pipeline.store import Store
from pipeline.taxonomy import REPO_ROOT, TAXONOMY_DIR, load_taxonomy

GOLD_DIR = TAXONOMY_DIR / "gold"
LAW_GOLD = GOLD_DIR / "laws_sample_v1.jsonl"
IAA_FILE = GOLD_DIR / "iaa_v1.jsonl"
OUT_HTML = REPO_ROOT / "pipeline" / "out" / "annotate.html"
IAA_SIZE = 30


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def adjudication_tasks(model: str = "solar-pro2") -> list[dict]:
    tax = load_taxonomy()
    gold = _read_jsonl(LAW_GOLD)
    items = {it.id: it for it in load_law_items()}
    jobs = plan_jobs(tax, [items[g["id"]] for g in gold], model)
    res = Store().fetch([j.key for j in jobs])
    pred = {j.item.id: res[j.key]["labels"]["primary"] for j in jobs if j.key in res}
    tasks = []
    for g in gold:
        if g["adjudication"] or pred.get(g["id"]) in (None, g["primary"]):
            continue
        cands = [g["primary"], pred[g["id"]]]
        # 항목마다 고정된 순서로 섞는다 (새로고침해도 같은 순서)
        random.Random(hashlib.sha256(g["id"].encode()).hexdigest()).shuffle(cands)
        tasks.append({"id": g["id"], "text": items[g["id"]].text, "candidates": cands})
    return tasks


def iaa_items() -> list[dict]:
    """한국어·영어 질의 중 벤치 15건 + 경계 사례 15건. 사용자가 읽을 수 있는 언어만 고른다."""
    seeds = [it for it in load_seed_items() if it.content_type == "query" and it.gold["lang"] in ("ko", "en")]
    rng = random.Random(20260929)
    bench = rng.sample(sorted([s for s in seeds if s.source == "seed:bench"], key=lambda s: s.id), IAA_SIZE // 2)
    hard = rng.sample(sorted([s for s in seeds if s.source == "seed:hard"], key=lambda s: s.id), IAA_SIZE // 2)
    picked = bench + hard
    rng.shuffle(picked)
    return [{"id": s.id, "text": s.text} for s in picked]


def build() -> Path:
    tax = load_taxonomy()

    def options(content_type: str) -> list[dict]:
        return [
            {"id": label.id, "name": label.name, "group": f"{label.parent} {tax.parent_names[label.parent]}"}
            for label in tax.labels_for(content_type)
        ]

    attrs = {a: list(tax.attributes[a].values) for a in ("intent", "urgency")}
    data = {
        "version": tax.version,
        "adjudicate": adjudication_tasks(),
        "iaa": iaa_items(),
        "lawOptions": options("law_article"),
        "queryOptions": options("query"),
        "attrs": attrs,
    }
    template = (Path(__file__).parent / "annotate_template.html").read_text(encoding="utf-8")
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(template.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False)), encoding="utf-8")
    print(f"판정 {len(data['adjudicate'])}건, 일치도 {len(data['iaa'])}건 → {OUT_HTML.relative_to(REPO_ROOT)}")
    return OUT_HTML


def cohen_kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    if not n:
        return 0.0
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in ca) / n**2
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def ingest(path: Path) -> None:
    result = json.loads(path.read_text(encoding="utf-8"))

    gold = _read_jsonl(LAW_GOLD)
    decided = {r["id"]: r for r in result.get("adjudicate", [])}
    for g in gold:
        if g["id"] in decided:
            d = decided[g["id"]]
            g["adjudication"] = {"by": "user", "choice": d["choice"], "note": d.get("note", "")}
            g["primary"] = d["choice"]
    _write_jsonl(LAW_GOLD, gold)
    print(f"조문 판정 {len(decided)}건 반영 → {LAW_GOLD.relative_to(REPO_ROOT)}")

    rows = result.get("iaa", [])
    if not rows:
        return
    _write_jsonl(IAA_FILE, [{**r, "annotator": "user"} for r in rows])
    seeds = {it.id: it.gold for it in load_seed_items()}
    pairs = [(seeds[r["id"]], r) for r in rows]
    print(f"라벨러 간 일치도 (Claude 시드 라벨 vs 사용자, n={len(pairs)})")
    for field, key in (("primary 세분류", "primary"), ("primary 대분류", None), ("intent", "intent"), ("urgency", "urgency")):
        if key is None:
            a = [g["primary"].split(".")[0] for g, _ in pairs]
            b = [u["primary"].split(".")[0] for _, u in pairs]
        else:
            sub = [(g, u) for g, u in pairs if key in g and u.get(key)]
            a, b = [g[key] for g, _ in sub], [u[key] for _, u in sub]
        agree = sum(x == y for x, y in zip(a, b))
        print(f"  {field}: 일치 {agree}/{len(a)}, kappa {cohen_kappa(a, b):.3f}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    p_ingest = sub.add_parser("ingest")
    p_ingest.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    if args.cmd == "build":
        build()
    else:
        ingest(args.path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
