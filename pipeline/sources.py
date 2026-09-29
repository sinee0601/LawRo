"""추출 대상 콘텐츠 로더. 모든 입력은 Item 으로 통일한다."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from pipeline.taxonomy import REPO_ROOT, TAXONOMY_DIR, load_law_articles

BENCH_QUERIES = REPO_ROOT / "bench" / "queries.jsonl"
SEED_DIR = TAXONOMY_DIR / "seed"

# 벤치 시드는 짧은 언어 이름을 쓴다
_LANG = {"korean": "ko", "english": "en", "chinese": "zh", "vietnamese": "vi", "japanese": "ja", "thai": "th"}


@dataclass
class Item:
    id: str
    content_type: str
    text: str
    source: str
    meta: dict = field(default_factory=dict)
    gold: dict | None = None  # 시드처럼 정답 라벨이 있으면 채운다


def _read_jsonl(path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_seed_items() -> list[Item]:
    items: list[Item] = []

    texts = {q["query_id"]: q for q in _read_jsonl(BENCH_QUERIES)}
    for row in _read_jsonl(SEED_DIR / "bench_v1.jsonl"):
        q = texts[row["query_id"]]
        items.append(
            Item(
                id=row["query_id"],
                content_type="query",
                text=q["text"],
                source="seed:bench",
                gold={**row, "lang": _LANG.get(q["lang"], row["lang"])},
            )
        )

    for row in _read_jsonl(SEED_DIR / "hard_v1.jsonl"):
        meta = {"law": row["law"], "article": row["article"]} if row["content_type"] == "law_article" else {}
        items.append(
            Item(
                id=row["id"],
                content_type=row["content_type"],
                text=row["text"],
                source="seed:hard",
                meta=meta,
                gold=row,
            )
        )
    return items


def load_law_items() -> list[Item]:
    return [
        Item(
            id=f"{law}:{no}",
            content_type="law_article",
            text=a["text"],
            source="corpus:laws",
            meta={"law": law, "article": no},
        )
        for (law, no), a in load_law_articles().items()
        # 삭제된 조문은 제목·본문이 비어 있다
        if a["text"].strip() and a.get("article_title", "").strip()
    ]


def load_law_gold_items() -> list[Item]:
    """무작위 조문 표본의 정답 (Claude 블라인드 라벨 + 사람 판정). 조문 정확도 추정용."""
    path = TAXONOMY_DIR / "gold" / "laws_sample_v1.jsonl"
    articles = load_law_articles()
    return [
        Item(
            id=g["id"],
            content_type="law_article",
            text=articles[(g["law"], g["article"])]["text"],
            source="gold:laws",
            meta={"law": g["law"], "article": g["article"]},
            gold=g,
        )
        for g in _read_jsonl(path)
    ]
