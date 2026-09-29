"""taxonomy/v2.yaml 과 GUIDE.md 를 읽어 파이프라인이 쓰는 형태로 바꾼다.

라벨 정의는 yaml 한 곳에만 두고, 프롬프트·스키마·검증이 모두 여기서 파생된다.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_DIR = REPO_ROOT / "taxonomy"
RAW_LAWS_DIR = REPO_ROOT / "backend" / "data" / "raw_laws"

CONTENT_TYPES = ("query", "contract_clause", "law_article")


@dataclass(frozen=True)
class Label:
    id: str
    name: str
    parent: str
    description: str = ""


@dataclass(frozen=True)
class Attribute:
    id: str
    name: str
    applies_to: tuple[str, ...]
    source: str  # "llm" | "rule"
    values: tuple[str, ...] = ()  # 비어 있으면 자유 형식(legal_refs)
    default: str | None = None
    descriptions: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Taxonomy:
    version: str
    labels: dict[str, Label]
    # 대분류 id -> 적용 가능한 content_type (없으면 전체)
    parent_applies_to: dict[str, tuple[str, ...]]
    parent_names: dict[str, str]
    attributes: dict[str, Attribute]

    def labels_for(self, content_type: str) -> list[Label]:
        return [
            label
            for label in self.labels.values()
            if content_type in self.parent_applies_to.get(label.parent, CONTENT_TYPES)
        ]

    def attributes_for(self, content_type: str, source: str = "llm") -> list[Attribute]:
        return [
            a for a in self.attributes.values() if content_type in a.applies_to and a.source == source
        ]


@lru_cache
def load_taxonomy(path: Path = TAXONOMY_DIR / "v2.yaml") -> Taxonomy:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    labels: dict[str, Label] = {}
    parent_applies_to: dict[str, tuple[str, ...]] = {}
    parent_names: dict[str, str] = {}
    for parent in raw["categories"]:
        parent_names[parent["id"]] = parent["name"]
        if "applies_to" in parent:
            parent_applies_to[parent["id"]] = tuple(parent["applies_to"])
        for child in parent["children"]:
            labels[child["id"]] = Label(
                id=child["id"],
                name=child["name"],
                parent=parent["id"],
                description=child.get("description", ""),
            )

    attributes: dict[str, Attribute] = {}
    for a in raw["attributes"]:
        values, descriptions = [], {}
        for v in a.get("values", []):
            if isinstance(v, dict):
                values.append(v["id"])
                if v.get("description"):
                    descriptions[v["id"]] = v["description"]
            else:
                values.append(v)
        attributes[a["id"]] = Attribute(
            id=a["id"],
            name=a["name"],
            applies_to=tuple(a["applies_to"]),
            source=a["source"],
            values=tuple(values),
            default=a.get("default"),
            descriptions=descriptions,
        )

    return Taxonomy(
        version=str(raw["version"]),
        labels=labels,
        parent_applies_to=parent_applies_to,
        parent_names=parent_names,
        attributes=attributes,
    )


@lru_cache
def load_guide_sections(path: Path = TAXONOMY_DIR / "GUIDE.md") -> str:
    """가이드 중 라벨을 붙이는 데 필요한 §3~§7 만 프롬프트에 넣는다.

    §2 설계 결정(왜 이렇게 나눴는가)과 §8 이후(대응표·한계·이력)는 판단에 필요 없고 토큰만 늘린다.
    """
    text = path.read_text(encoding="utf-8")
    start = re.search(r"^## 3\. ", text, re.MULTILINE)
    end = re.search(r"^## 8\. ", text, re.MULTILINE)
    if not start or not end:
        raise ValueError("GUIDE.md 의 섹션 구조(## 3. ~ ## 8.)를 찾을 수 없습니다")
    return text[start.start() : end.start()].strip()


@lru_cache
def load_law_articles() -> dict[tuple[str, str], dict]:
    """(법령명, 조문번호) -> 조문. legal_refs 검증과 law_article 입력에 쓴다."""
    articles: dict[tuple[str, str], dict] = {}
    for f in sorted(RAW_LAWS_DIR.glob("*.json")):
        if f.name.startswith("_"):
            continue
        for a in json.loads(f.read_text(encoding="utf-8")):
            articles[(a["law_name"], a["article_no"])] = a
    return articles


@lru_cache
def law_names() -> tuple[str, ...]:
    manifest = json.loads((RAW_LAWS_DIR / "_manifest.json").read_text(encoding="utf-8"))
    return tuple(law["law_name"] for law in manifest["laws"])
