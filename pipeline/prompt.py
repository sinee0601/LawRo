"""추출 프롬프트.

시스템 프롬프트(분류 체계 + 가이드)는 content_type 별로 고정이고 입력만 바뀐다.
고정 부분을 앞에 두어 Upstage 프롬프트 캐시(cached_tokens)를 받을 수 있게 한다.
"""

from __future__ import annotations

import hashlib

from pipeline.taxonomy import Taxonomy, load_guide_sections

# 프롬프트 문구를 바꾸면 올린다. 결과마다 기록되어 어떤 프롬프트로 만든 라벨인지 추적한다
PROMPT_VERSION = "p1"

_CONTENT_TYPE_NAMES = {
    "query": "사용자 상담 질문",
    "contract_clause": "근로계약서 조항 1개 (OCR 추출)",
    "law_article": "법령 조문 1개",
}


def _render_labels(tax: Taxonomy, content_type: str) -> str:
    lines: list[str] = []
    current_parent = None
    for label in tax.labels_for(content_type):
        if label.parent != current_parent:
            current_parent = label.parent
            lines.append(f"\n[{label.parent}] {tax.parent_names[label.parent]}")
        desc = f" — {label.description}" if label.description else ""
        lines.append(f"- {label.id}: {label.name}{desc}")
    return "\n".join(lines).strip()


def _render_attributes(tax: Taxonomy, content_type: str) -> str:
    lines: list[str] = []
    for attr in tax.attributes_for(content_type):
        if not attr.values:
            continue
        values = ", ".join(
            f"{v}({attr.descriptions[v]})" if v in attr.descriptions else v for v in attr.values
        )
        default = f" / 기본값 {attr.default}" if attr.default else ""
        lines.append(f"- {attr.id} ({attr.name}): {values}{default}")
    return "\n".join(lines)


def system_prompt(tax: Taxonomy, content_type: str) -> str:
    return f"""당신은 한국 노동법 콘텐츠를 분류 체계에 따라 라벨링하는 전문가입니다.
입력은 {_CONTENT_TYPE_NAMES[content_type]}입니다. 아래 분류 체계(v{tax.version})와 라벨링 가이드를 그대로 따르세요.

# 카테고리 (primary 는 정확히 1개, secondary 는 0~2개)
{_render_labels(tax, content_type)}

# 속성 (텍스트에 명시된 경우에만 채우고, 모르면 unknown 또는 기본값)
{_render_attributes(tax, content_type)}
- legal_refs: 근거가 되는 조문 최대 3개. 아래 12개 법령 안에서만, 확신이 없으면 빈 목록

# 라벨링 가이드
{load_guide_sections()}

# 출력
- issue 에 질문자가 판단받고 싶은 최종 쟁점을 한국어 한 문장으로 먼저 쓰고, 그 쟁점에 맞춰 라벨을 고르세요.
- 입력이 한국어가 아니어도 번역하지 말고 원문 그대로 판단하세요.
- 범위 밖(OUT_OF_SCOPE)이면 속성은 기본값으로 두고 legal_refs 는 비우세요."""


def user_prompt(content_type: str, text: str, meta: dict | None = None) -> str:
    if content_type == "law_article" and meta:
        return f"[{meta['law']} {meta['article']}]\n{text}"
    return text


def prompt_fingerprint(tax: Taxonomy, content_type: str) -> str:
    """프롬프트 전체의 해시. 가이드 문구만 바뀌어도(PATCH) 캐시가 무효화되도록 한다."""
    return hashlib.sha256(system_prompt(tax, content_type).encode()).hexdigest()[:12]
