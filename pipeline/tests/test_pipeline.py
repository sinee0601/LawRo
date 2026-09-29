"""API 를 호출하지 않는 파이프라인 단위 테스트."""

import pytest

from pipeline.lang import detect_language
from pipeline.prompt import prompt_fingerprint, system_prompt
from pipeline.schema import output_schema, validate
from pipeline.sources import load_law_items, load_seed_items
from pipeline.store import cache_key
from pipeline.taxonomy import load_taxonomy


@pytest.fixture(scope="module")
def tax():
    return load_taxonomy()


def test_meta_labels_only_for_law_articles(tax):
    query_labels = {label.id for label in tax.labels_for("query")}
    law_labels = {label.id for label in tax.labels_for("law_article")}
    assert "META.PENALTY" in law_labels
    assert not any(label.startswith("META.") for label in query_labels)
    assert "OUT_OF_SCOPE.OTHER_LEGAL" in law_labels  # GUIDE D12


def test_schema_enums_match_applicable_attributes(tax):
    query = output_schema(tax, "query")["properties"]
    clause = output_schema(tax, "contract_clause")["properties"]
    assert "intent" in query and "compliance" not in query
    assert "compliance" in clause and "intent" not in clause
    assert "language" not in query  # 규칙으로 계산 (GUIDE D10)


def test_validate_cleans_secondary_and_hallucinated_refs(tax):
    raw = {
        "issue": "x",
        "primary": "WAGE.UNPAID",
        "secondary": ["WAGE.UNPAID", "STAY.STATUS", "STAY.STATUS"],
        "intent": "dispute",
        "urgency": "medium",
        "employment_type": "unknown",
        "worker_status": "employed",
        "workplace_size": "unknown",
        "visa_type": "unknown",
        "legal_refs": [
            {"law": "근로기준법", "article": "제43조"},
            {"law": "근로기준법", "article": "제999조"},
        ],
    }
    v = validate(tax, "query", raw)
    assert v.labels["secondary"] == ["STAY.STATUS"]
    assert v.labels["legal_refs"] == [{"law": "근로기준법", "article": "제43조"}]
    assert "ref_not_in_corpus:근로기준법 제999조" in v.issues
    assert sum(i.startswith("secondary_duplicate") for i in v.issues) == 2


def test_validate_rejects_label_from_other_content_type(tax):
    with pytest.raises(ValueError):
        validate(tax, "query", {"primary": "META.PENALTY"})


def test_out_of_scope_drops_attributes(tax):
    v = validate(tax, "query", {"primary": "OUT_OF_SCOPE.NON_LEGAL", "secondary": [], "intent": "info", "legal_refs": []})
    assert "intent" not in v.labels


def test_language_rule_matches_seed_labels():
    items = [it for it in load_seed_items() if it.content_type != "law_article"]
    wrong = [(it.id, it.gold["lang"], detect_language(it.text)) for it in items if detect_language(it.text) != it.gold["lang"]]
    assert not wrong


@pytest.mark.parametrize(
    "text,lang",
    [("E-9인데 사장님이 동의를 안 해줘요", "ko"), ("Can I get 퇴직금?", "en"), ("我是E-9，这个合法吗？", "zh"), ("12345", "other")],
)
def test_language_mixed_scripts(text, lang):
    assert detect_language(text) == lang


def test_cache_key_changes_with_prompt(tax):
    fp = prompt_fingerprint(tax, "query")
    assert cache_key("query", "a", "m", fp) == cache_key("query", "a", "m", fp)
    assert cache_key("query", "a", "m", fp) != cache_key("query", "a", "m2", fp)
    assert prompt_fingerprint(tax, "query") != prompt_fingerprint(tax, "law_article")


def test_prompt_contains_guide_rules_but_not_design_rationale(tax):
    prompt = system_prompt(tax, "query")
    assert "R11" in prompt and "경계 사례" in prompt
    assert "## 2. 설계 결정" not in prompt


def test_sources():
    seeds = load_seed_items()
    assert len(seeds) == 161 and all(it.gold for it in seeds)
    laws = load_law_items()
    assert 1250 < len(laws) <= 1318
