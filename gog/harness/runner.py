"""
safe-gog test runner
Runs all parsed test cases through the rule engine and compares actual vs expected.
"""

import sys
import os
from dataclasses import dataclass
from typing import Optional

from rules import evaluate, GateResult
from parse_testcases import TestCase, load_all


@dataclass
class RunResult:
    tc: TestCase
    actual: GateResult
    passed: bool           # actual verdict == expected verdict
    mismatch_type: str     # "" | "FALSE_POSITIVE" | "FALSE_NEGATIVE" | "WRONG_VERDICT"

    @property
    def status(self) -> str:
        if self.passed:
            return "PASS"
        return f"FAIL ({self.mismatch_type})"


def run_case(tc: TestCase) -> RunResult:
    actual = evaluate(tc.input_text)

    passed = actual.verdict == tc.expected_verdict

    mismatch_type = ""
    if not passed:
        if tc.expected_verdict == "BLOCK" and actual.verdict in ("CONFIRM", "ALLOW"):
            mismatch_type = "FALSE_NEGATIVE"  # should have blocked, didn't
        elif tc.expected_verdict in ("ALLOW",) and actual.verdict in ("BLOCK", "CONFIRM"):
            mismatch_type = "FALSE_POSITIVE"  # blocked a safe op
        elif tc.expected_verdict == "CONFIRM" and actual.verdict == "ALLOW":
            mismatch_type = "FALSE_NEGATIVE"  # should have gated, didn't
        elif tc.expected_verdict == "CONFIRM" and actual.verdict == "BLOCK":
            mismatch_type = "FALSE_POSITIVE"  # over-blocked
        else:
            mismatch_type = "WRONG_VERDICT"

    return RunResult(tc=tc, actual=actual, passed=passed, mismatch_type=mismatch_type)


def run_all(cases: list[TestCase]) -> list[RunResult]:
    return [run_case(tc) for tc in cases]


def print_report(results: list[RunResult], verbose: bool = False, failures_only: bool = False):
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed

    false_negatives = [r for r in results if r.mismatch_type == "FALSE_NEGATIVE"]
    false_positives = [r for r in results if r.mismatch_type == "FALSE_POSITIVE"]
    wrong = [r for r in results if r.mismatch_type == "WRONG_VERDICT"]

    # Per-risk breakdown
    by_risk: dict[str, list[RunResult]] = {}
    for r in results:
        by_risk.setdefault(r.tc.risk, []).append(r)

    print("=" * 70)
    print("  safe-gog Test Harness — Results")
    print("=" * 70)
    print(f"  Total:          {total}")
    print(f"  PASS:           {passed}  ({100*passed//total}%)")
    print(f"  FAIL:           {failed}")
    if failed:
        print(f"    False negatives (missed block): {len(false_negatives)}")
        print(f"    False positives (over-blocked):  {len(false_positives)}")
        print(f"    Wrong verdict:                   {len(wrong)}")
    print()

    print("─" * 70)
    print("  Per-Risk Breakdown")
    print("─" * 70)
    for risk, risk_results in sorted(by_risk.items()):
        risk_pass = sum(1 for r in risk_results if r.passed)
        risk_total = len(risk_results)
        bar = "✅" if risk_pass == risk_total else "⚠️ "
        print(f"  {bar} {risk:6s}  {risk_pass:3d}/{risk_total:3d}  {'█' * risk_pass}{'░' * (risk_total - risk_pass)}")
    print()

    if failed:
        print("─" * 70)
        print("  Failures")
        print("─" * 70)
        for r in results:
            if not r.passed:
                print(f"\n  ❌ {r.tc.tc_id}  [{r.mismatch_type}]")
                print(f"     Input:    {r.tc.input_text[:80]}")
                print(f"     Expected: {r.tc.expected_verdict}")
                print(f"     Actual:   {r.actual.verdict}  ({r.actual.rule}: {r.actual.detail})")

    if verbose and not failures_only:
        print()
        print("─" * 70)
        print("  All Results (verbose)")
        print("─" * 70)
        for r in results:
            icon = "✅" if r.passed else "❌"
            print(f"  {icon} {r.tc.tc_id}  expected={r.tc.expected_verdict}  "
                  f"actual={r.actual.verdict}  rule={r.actual.rule}")

    print()
    print("=" * 70)
    return failed == 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="safe-gog test harness")
    parser.add_argument(
        "--testcases-dir",
        default=os.path.join(os.path.dirname(__file__), "..", "testcases"),
        help="Directory containing testcase .md files",
    )
    parser.add_argument("--risk", help="Run only cases for this risk ID (e.g. 1E, 3A)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print all results")
    parser.add_argument("--failures-only", "-f", action="store_true", help="Print only failures")
    parser.add_argument("--tc", help="Run a single test case by ID (e.g. TC-3A-001)")
    args = parser.parse_args()

    cases = load_all(args.testcases_dir)

    if args.risk:
        cases = [c for c in cases if c.risk.upper() == args.risk.upper()]
    if args.tc:
        cases = [c for c in cases if c.tc_id.upper() == args.tc.upper()]

    if not cases:
        print(f"No test cases found.")
        sys.exit(1)

    results = run_all(cases)
    ok = print_report(results, verbose=args.verbose, failures_only=args.failures_only)
    sys.exit(0 if ok else 1)
