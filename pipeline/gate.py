"""프롬프트·분류 체계 회귀 게이트 (CI 에서 API 호출 없이 동작).

    python -m pipeline.gate            # 확인 (CI)
    python -m pipeline.gate --promote  # 현재 test 평가를 새 기준선으로 (의도한 변경일 때만)

흐름: 프롬프트나 taxonomy 를 바꾼다 → 로컬에서 run --source seeds, evaluate --split test →
eval_*_test.json 을 커밋 → CI 가 현재 프롬프트 지문과 맞는 test 평가가 있는지, 기준선보다 나빠지지 않았는지 본다.

비교는 같은 test 항목의 정오 변화로 한다 (대응 비교). test 79건의 정확도 신뢰구간은 폭이 11%p 라
두 점수를 따로 비교하면 웬만한 퇴행을 못 잡는다.
"""

from __future__ import annotations

import argparse
import json
import math
import sys

from pipeline.prompt import prompt_fingerprint
from pipeline.taxonomy import CONTENT_TYPES, REPO_ROOT, load_taxonomy

REPORT_DIR = REPO_ROOT / "pipeline" / "reports"
BASELINE = REPORT_DIR / "baseline.json"

# 기준선보다 이만큼 넘게 떨어지면 막는다
MAX_EXACT_DROP = 0.025  # test 79건 기준 약 2건
MAX_MACRO_F1_DROP = 0.03
# 맞던 게 틀린 건수가 틀리던 게 맞은 건수보다 유의하게 많으면 막는다 (단측 부호 검정)
SIGN_TEST_ALPHA = 0.05


def current_fingerprints() -> dict[str, str]:
    tax = load_taxonomy()
    return {ct: prompt_fingerprint(tax, ct) for ct in CONTENT_TYPES}


def find_current_report(fps: dict[str, str]) -> dict | None:
    for path in sorted(REPORT_DIR.glob("eval_*_test.json")):
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("prompt_fp") == fps:
            report["_path"] = path.name
            return report
    return None


def sign_test_p(worse: int, better: int) -> float:
    """정오가 바뀐 항목만 보는 단측 부호 검정. H0: 나빠질 확률 = 좋아질 확률."""
    n = worse + better
    if n == 0:
        return 1.0
    return sum(math.comb(n, k) for k in range(worse, n + 1)) / 2**n


def compare(base: dict, cur: dict) -> tuple[list[str], list[str]]:
    """(실패 사유, 참고 메시지)"""
    failures, notes = [], []
    shared = base["item_hits"].keys() & cur["item_hits"].keys()
    worse = sorted(i for i in shared if base["item_hits"][i] and not cur["item_hits"][i])
    better = sorted(i for i in shared if not base["item_hits"][i] and cur["item_hits"][i])
    p = sign_test_p(len(worse), len(better))
    d_exact = cur["primary_exact"] - base["primary_exact"]
    d_f1 = cur["macro_f1_parent"] - base["macro_f1_parent"]
    notes.append(
        f"primary 세분류 {base['primary_exact']:.1%} → {cur['primary_exact']:.1%} ({d_exact:+.1%}), "
        f"macro-F1 {base['macro_f1_parent']:.3f} → {cur['macro_f1_parent']:.3f} ({d_f1:+.3f})"
    )
    # test 오답 내용은 보지 않는 원칙이라 id 대신 건수만 보여준다
    notes.append(f"같은 항목 {len(shared)}건 중 맞던→틀림 {len(worse)}건, 틀리던→맞음 {len(better)}건 (부호 검정 p={p:.3f})")
    if cur.get("missing"):
        failures.append(f"test {cur['missing']}건의 추출 결과가 없거나 실패했다")
    if len(shared) < len(base["item_hits"]):
        failures.append(f"기준선 항목 중 {len(base['item_hits']) - len(shared)}건이 현재 평가에 없다")
    if d_exact < -MAX_EXACT_DROP:
        failures.append(f"primary 세분류 정확도가 {-d_exact:.1%} 떨어졌다 (허용 {MAX_EXACT_DROP:.1%})")
    if d_f1 < -MAX_MACRO_F1_DROP:
        failures.append(f"macro-F1 이 {-d_f1:.3f} 떨어졌다 (허용 {MAX_MACRO_F1_DROP})")
    if p < SIGN_TEST_ALPHA:
        failures.append(f"맞던 항목이 틀린 경우가 유의하게 많다 (p={p:.3f})")
    return failures, notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--promote", action="store_true")
    args = parser.parse_args(argv)

    fps = current_fingerprints()
    current = find_current_report(fps)
    if current is None:
        print("현재 프롬프트 지문과 맞는 test 평가가 없습니다.")
        print("프롬프트나 taxonomy 를 바꿨다면 다음을 실행하고 eval_*_test.json 을 커밋하세요:")
        print("  python -m pipeline.run --source seeds && python -m pipeline.evaluate --split test")
        return 1

    if args.promote:
        keep = {k: v for k, v in current.items() if not k.startswith("_")}
        BASELINE.write_text(json.dumps(keep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"기준선 갱신: {current['_path']} (primary {current['primary_exact']:.1%})")
        return 0

    if not BASELINE.exists():
        print("기준선이 없습니다. python -m pipeline.gate --promote 로 만드세요.")
        return 1
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    failures, notes = compare(base, current)
    print(f"기준선 {base['model']}/{base['prompt_version']} vs 현재 {current['_path']}")
    for n in notes:
        print(f"  {n}")
    for f in failures:
        print(f"  실패: {f}")
    if not failures:
        print("  통과")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
