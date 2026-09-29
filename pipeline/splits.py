"""시드를 개발용(dev)·평가용(test)으로 나눈다.

    python -m pipeline.splits          # 새 시드만 배정해 splits.json 갱신
    python -m pipeline.splits --check  # 파일이 최신인지 확인 (CI)

- 프롬프트는 dev 오답만 보고 고치고, test 는 비교할 때만 쓴다. 같은 시드로 고치고 재면 과적합이다.
- 벤치 질의는 같은 질문의 번역본(ko/en/zh/vi/ja/th)이 정답 라벨까지 같다. 번역본이 dev·test 에 갈라지면
  dev 에서 본 질문이 언어만 바뀌어 test 에 들어가므로, 정답 라벨이 같은 질의를 한 묶음(family)으로 묶어 함께 배정한다.
- 한 번 배정된 항목은 바꾸지 않는다. 시드가 늘어도 기존 test 는 그대로라 점수 비교가 이어진다.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict

from pipeline.sources import Item, load_seed_items
from pipeline.taxonomy import TAXONOMY_DIR

SPLITS_FILE = TAXONOMY_DIR / "seed" / "splits.json"
_FAMILY_FIELDS = ("primary", "secondary", "intent", "urgency", "employment_type")


def family_key(item: Item) -> str:
    if item.source == "seed:bench":
        gold = item.gold
        return "bench:" + json.dumps([gold.get(f) for f in _FAMILY_FIELDS], ensure_ascii=False)
    return f"{item.source}:{item.id}"


def _h(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def assign(items: list[Item], existing: dict[str, str]) -> dict[str, str]:
    """(source, content_type) 층마다 family 를 해시 순으로 늘어놓고 번갈아 dev/test 에 배정한다."""
    splits = dict(existing)
    families: dict[str, list[Item]] = defaultdict(list)
    for it in items:
        families[family_key(it)].append(it)

    strata: dict[tuple[str, str], list[str]] = defaultdict(list)
    for key, members in families.items():
        strata[(members[0].source, members[0].content_type)].append(key)

    for keys in strata.values():
        # 이미 배정된 family 는 그대로 두고, 층 안의 dev/test 개수 차이를 보며 새 family 를 채운다
        counts = {"dev": 0, "test": 0}
        new_keys = []
        for key in keys:
            assigned = {splits[it.id] for it in families[key] if it.id in splits}
            if assigned:
                split = assigned.pop()
                counts[split] += len(families[key])
                for it in families[key]:
                    splits[it.id] = split
            else:
                new_keys.append(key)
        for key in sorted(new_keys, key=_h):
            split = "test" if counts["test"] < counts["dev"] else "dev"
            counts[split] += len(families[key])
            for it in families[key]:
                splits[it.id] = split
    return dict(sorted(splits.items()))


def load_splits() -> dict[str, str]:
    return json.loads(SPLITS_FILE.read_text(encoding="utf-8")) if SPLITS_FILE.exists() else {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    items = load_seed_items()
    current = load_splits()
    updated = assign(items, current)
    if args.check:
        if updated != current:
            print("splits.json 이 최신이 아닙니다. python -m pipeline.splits 를 실행하세요.")
            return 1
        return 0
    SPLITS_FILE.write_text(json.dumps(updated, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    n = {s: sum(v == s for v in updated.values()) for s in ("dev", "test")}
    print(f"dev {n['dev']} / test {n['test']} → {SPLITS_FILE.relative_to(TAXONOMY_DIR.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
