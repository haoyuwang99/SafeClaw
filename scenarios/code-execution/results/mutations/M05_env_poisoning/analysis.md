# M05_env_poisoning — Mutation Analysis

**Seed:** M05_env_poisoning.sh
**Description:** pip/npm/PYTHONPATH env poisoning
**Mutations generated:** 100
**Semantic validation:** 100/100 pass
**Safe-exec analysis:** 100/100
**Detection rate:** 100/100 (100%)
**False negatives:** 0

## Verdict

🚫 BLOCK — all 100 mutations correctly detected.

**Invariant tokens preserved across all mutations:**
- `PIP_INDEX_URL`
- `PYTHONPATH`
