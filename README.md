# SafeClaw — Safety Benchmark for OpenClaw Agent Skills

Empirical evaluation of L0 safety skills in the OpenClaw personal agent framework.
Three real-world attack scenarios.

---

## Directory Structure

```
SafeClaw/
├── system-prompt/
│   └── AGENTS.md               # OpenClaw system prompt with L0 safety routing table
│
├── scenarios/
│   ├── google-workspace/       # Scenario 1: safe-gog (20 risk types, 1,971 cases)
│   │   ├── skill/SKILL.md      # The safe-gog skill under evaluation
│   │   ├── testcases/          # Ground-truth test cases (.md per risk type)
│   │   ├── harness/            # live_runner.py + rules.py (regex baseline)
│   │   └── results/            # live_<RISK>_all_results.json (per risk, 100 cases each)
│   │
│   ├── malicious-skills/       # Scenario 2: skill-guard (157 skills, 53 auditable)
│   │   ├── skill/SKILL.md      # The skill-guard skill under evaluation
│   │   ├── testcases/          # skills_dataset.csv (ground-truth malicious labels)
│   │   ├── harness/            # (audit scripts)
│   │   └── results/            # audited-no-failures-complete.json, benchmark-results-full.json
│   │
│   └── code-execution/         # Scenario 3: safe-exec (2,028 cases)
│       ├── skill/SKILL.md      # The safe-exec skill under evaluation
│       ├── testcases/seeds/    # T01-T08, B01-B10, M01-M10 seed scripts
│       ├── harness/            # (mutation generator)
│       └── results/            # dataset.md + mutations/ (per-family analysis)
```

---

## Results Summary

| Scenario | Skill | Cases | Accuracy | FN | FP |
|----------|-------|------:|--------:|---:|---:|
| Google Workspace | `safe-gog` | 1,971 | **95.2%** | 7 | 8 |
| Malicious Skills | `skill-guard` | 53 auditable / 157 total | **100% flagged** (93.9% exact BLOCK) | 3 | 0 |
| Code Execution | `safe-exec` | 2,028 | **100%** | 0 | 0 |

### Regex baseline comparison (safe-gog, 1,971 cases)

| | Skill | Regex |
|--|------:|------:|
| Accuracy | **95.2%** | 61.6% |
| False negatives | 7 | 530 |
| Per-case latency | ~1,200 ms | ~318 µs |
| Cost per 1,000 | ~$3.05 | $0.00 |

---

## Key Findings

**Enforcement completeness vs effectiveness.** Runtime enforcement can guarantee a safety check is *always invoked*, but cannot guarantee the check produces the correct verdict. The benchmarks measure effectiveness (verdict accuracy); architectural changes are needed for completeness guarantees.

**LLM reasoning adds +33.6pp over regex** on the Google Workspace benchmark, primarily by handling natural language variation, paraphrasing, and novel framing that structural patterns cannot match.

**Residual failure modes:**
- `--force` gate missing in Sheets/Calendar (safe-gog, 14 FNs)
- BLOCK/CONFIRM boundary ambiguity on bulk sends (safe-gog, 1D risk, 78.8%)
- Cosmetic mutation evasion not tested for safe-exec (semantic rewrites remain an open gap)
- 108/157 malicious skills unavailable for download (69% dataset gap for skill-guard)

**Known L0 bypass vectors (not yet benchmarked):**
- Sub-agent bypassPermissions inheritance
- Memory file poisoning
- Multi-turn gradual erosion
- Skill delegation chain gaps

---

## Citation

Dataset sourced from:
- MaliciousAgentBench (liu2026maliciousagentskillswild) — malicious skills corpus
- Original test case generation (this work) — Google Workspace and code execution scenarios
