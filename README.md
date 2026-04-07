# SafeClaw — Safety Layer for OpenClaw Agent Skills

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
│
│── safeskillhub/               # safety skill library
│   │── safe-gog
│   │── safe-ordercli
│   └── safe-...
```
---

## Usage 

* Step 1 — Set the System Prompt Copy the SafeClaw system prompt into your OpenClaw working directory so the agent loads it on startup.
  > AGENTS.md contains the full OpenClaw system prompt plus the L0 safety routing table. The routing table tells the agent which safety skill to invoke for each category of action (workspace calls → safe-gog, skill installs → skill-guard, code execution → safe-exec).
* Step 2 — Install the Safety Skills from `safeskillhub/`.
* Step 3 - Prioritise the Safety Skills in the System Prompt.
