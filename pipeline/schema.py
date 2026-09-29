"""content_type 별 출력 JSON 스키마와 사후 검증.

스키마(response_format)로 형식과 라벨 값을 강제하고, 스키마로 표현할 수 없는 규칙
(secondary 중복, 존재하지 않는 조문 인용 등)은 validate() 에서 걸러 issues 로 남긴다.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pipeline.taxonomy import Taxonomy, law_names, load_law_articles

MAX_SECONDARY = 2
MAX_LEGAL_REFS = 3
ARTICLE_PATTERN = r"^제\d+조(의\d+)?$"


def output_schema(tax: Taxonomy, content_type: str) -> dict:
    label_ids = [label.id for label in tax.labels_for(content_type)]
    properties: dict = {
        # 라벨 전에 쟁점을 한 문장으로 먼저 쓰게 한다 (GUIDE §3 의 2번 단계)
        "issue": {"type": "string", "description": "질문자가 판단받고 싶은 최종 쟁점 한 문장"},
        "primary": {"type": "string", "enum": label_ids},
        "secondary": {
            "type": "array",
            "items": {"type": "string", "enum": label_ids},
            "maxItems": MAX_SECONDARY,
        },
    }
    for attr in tax.attributes_for(content_type):
        if attr.values:
            properties[attr.id] = {"type": "string", "enum": list(attr.values)}
    properties["legal_refs"] = {
        "type": "array",
        "maxItems": MAX_LEGAL_REFS,
        "items": {
            "type": "object",
            "properties": {
                "law": {"type": "string", "enum": list(law_names())},
                "article": {"type": "string", "pattern": ARTICLE_PATTERN},
            },
            "required": ["law", "article"],
            "additionalProperties": False,
        },
    }
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


@dataclass
class Validated:
    labels: dict
    issues: list[str] = field(default_factory=list)


def validate(tax: Taxonomy, content_type: str, raw: dict) -> Validated:
    """LLM 출력을 taxonomy 기준으로 정리한다. 고칠 수 없는 오류는 ValueError."""
    issues: list[str] = []
    allowed = {label.id for label in tax.labels_for(content_type)}

    primary = raw.get("primary")
    if primary not in allowed:
        raise ValueError(f"invalid primary: {primary!r}")

    secondary: list[str] = []
    for label in raw.get("secondary") or []:
        if label not in allowed:
            issues.append(f"secondary_invalid:{label}")
        elif label == primary or label in secondary:
            issues.append(f"secondary_duplicate:{label}")
        else:
            secondary.append(label)
    if len(secondary) > MAX_SECONDARY:
        issues.append("secondary_truncated")
        secondary = secondary[:MAX_SECONDARY]

    labels: dict = {"issue": raw.get("issue", ""), "primary": primary, "secondary": secondary}

    # 범위 밖이면 속성을 채우지 않는다 (GUIDE §3 의 1번 단계)
    out_of_scope = primary.startswith("OUT_OF_SCOPE.")
    for attr in tax.attributes_for(content_type):
        if not attr.values or out_of_scope:
            continue
        value = raw.get(attr.id)
        if value not in attr.values:
            issues.append(f"attr_invalid:{attr.id}={value!r}")
            value = attr.default
        labels[attr.id] = value

    articles = load_law_articles()
    refs: list[dict] = []
    for ref in raw.get("legal_refs") or []:
        key = (ref.get("law"), ref.get("article"))
        if key not in articles:
            # 코퍼스에 없는 조문 = 환각. 틀린 조문은 없는 것보다 나쁘다 (GUIDE §6)
            issues.append(f"ref_not_in_corpus:{key[0]} {key[1]}")
        elif key in {(r["law"], r["article"]) for r in refs}:
            issues.append(f"ref_duplicate:{key[0]} {key[1]}")
        else:
            refs.append({"law": key[0], "article": key[1]})
    if len(refs) > MAX_LEGAL_REFS:
        issues.append("refs_truncated")
        refs = refs[:MAX_LEGAL_REFS]
    labels["legal_refs"] = refs

    return Validated(labels=labels, issues=issues)
