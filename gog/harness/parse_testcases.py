"""
Test case parser for safe-gog test files.
Parses the markdown format:

TC-{RISK}-{NNN}
Input: <text>
Naive: <text>
safe-gog: BLOCK|CONFIRM|ALLOW — <explanation>
Result: PASS|PARTIAL|FAIL
"""

import re
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class TestCase:
    tc_id: str             # TC-3A-001
    risk: str              # 3A
    seq: int               # 1
    input_text: str        # raw input string
    naive_action: str      # what naive agent would do
    expected_verdict: str  # BLOCK | CONFIRM | ALLOW
    expected_detail: str   # explanation after the dash
    documented_result: str # PASS | PARTIAL | FAIL (from the spec)
    source_file: str       # which file this came from


def parse_file(filepath: str) -> list[TestCase]:
    """Parse a single test case markdown file."""
    with open(filepath) as f:
        content = f.read()

    cases = []
    source = os.path.basename(filepath)

    # Split on TC- blocks
    # Each block starts with "TC-{RISK}-{NNN}" on its own line
    blocks = re.split(r'\n(?=TC-[A-Z0-9]+-\d+\b)', content)

    for block in blocks:
        block = block.strip()
        if not block.startswith("TC-"):
            continue

        try:
            case = _parse_block(block, source)
            if case:
                cases.append(case)
        except Exception as e:
            # Skip malformed blocks silently; log to stderr
            import sys
            print(f"[WARN] Failed to parse block in {source}: {e}\nBlock: {block[:80]}", file=sys.stderr)

    return cases


def _parse_block(block: str, source: str) -> Optional[TestCase]:
    lines = block.strip().splitlines()
    if not lines:
        return None

    # First line: TC-3A-001 or "TC-3A-001\nInput: ..."
    tc_id_match = re.match(r'(TC-([A-Z0-9]+)-(\d+))', lines[0].strip())
    if not tc_id_match:
        return None

    tc_id = tc_id_match.group(1)
    risk = tc_id_match.group(2)
    seq = int(tc_id_match.group(3))

    # Remaining lines: key: value pairs
    remaining = "\n".join(lines[1:])

    input_text = _extract_field(remaining, "Input")
    naive_action = _extract_field(remaining, "Naive Agent Action") or _extract_field(remaining, "Naive")
    safe_gog_raw = _extract_field(remaining, "safe-gog Response") or _extract_field(remaining, "safe-gog")
    result_raw = _extract_field(remaining, "Result")

    if not input_text or not safe_gog_raw:
        return None

    # Parse verdict from safe-gog field: "BLOCK — explanation" or "ALLOW" etc.
    verdict_match = re.match(r'(BLOCK|CONFIRM|ALLOW|PARTIAL)\s*[—\-]?\s*(.*)', safe_gog_raw.strip(), re.IGNORECASE)
    if not verdict_match:
        return None

    expected_verdict = verdict_match.group(1).upper()
    expected_detail = verdict_match.group(2).strip()

    # Normalise PARTIAL → treat as CONFIRM for verdict matching
    if expected_verdict == "PARTIAL":
        expected_verdict = "CONFIRM"

    documented_result = result_raw.strip().upper() if result_raw else "UNKNOWN"
    # Strip annotations like "PASS (no false positive)" → "PASS"
    documented_result = re.match(r'(PASS|PARTIAL|FAIL)', documented_result)
    documented_result = documented_result.group(1) if documented_result else "UNKNOWN"

    return TestCase(
        tc_id=tc_id,
        risk=risk,
        seq=seq,
        input_text=input_text.strip(),
        naive_action=(naive_action or "").strip(),
        expected_verdict=expected_verdict,
        expected_detail=expected_detail,
        documented_result=documented_result,
        source_file=source,
    )


def _extract_field(text: str, field: str) -> Optional[str]:
    """Extract value for 'Field: value' (may span until next field or blank line)."""
    # Match field name (may contain spaces/hyphens) followed by colon and value
    # Stop at the next line that looks like "SomeField:" or "Some Field Action:"
    pattern = rf'^{re.escape(field)}:\s*(.+?)(?=\n[A-Za-z][A-Za-z0-9 \-]*:|$)'
    m = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


def load_all(testcases_dir: str) -> list[TestCase]:
    """Load all .md test case files from a directory."""
    cases = []
    for fname in sorted(os.listdir(testcases_dir)):
        if fname.endswith(".md") and not fname.startswith("_"):
            fpath = os.path.join(testcases_dir, fname)
            file_cases = parse_file(fpath)
            cases.extend(file_cases)
    return cases
