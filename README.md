# SafeClaw — Safety Layer for OpenClaw Agent Skills

This is the repository for [SafeClaw-R: Towards Safe and Secure Multi-Agent Personal Assistants](https://arxiv.org/html/2603.28807v1).
We formulates safety in multi-agent systems as a runtime enforcement problem — safety policies are applied during execution, not discovered after the fact. SafeClaw-R is the reference implementation: a multi-agent framework that embeds enforcement agent nodes directly into the OpenClaw execution pipeline, enabling consistent, real-time mediation of agent actions against declarative safety policies. This repo also introduces the Safe Skill Factory, a methodology for systematically deriving and refining enforcement policies, and SafeSkillHub for sharing reusable safety specifications across teams. We evaluate SafeClaw-R across three real-world attack surfaces — Google Workspace abuse, malicious third-party skills, and dangerous code execution — demonstrating strong enforcement effectiveness with low false-positive rates.

## We welcome contributions that maintain, extend, or propose new safety skills — if you've encountered a threat pattern in the wild, open a PR to SafeSkillHub and help the community stay ahead of it.

---

## Directory Structure

```
SafeClaw/
├── system-prompt/
│   └── AGENTS.md               # OpenClaw system prompt with L0 safety routing table
│
│── risk-assessment/            # A preliminary risk analysis for OpenClaw built-in skills.
│
├── scenarios/                  # Evaluation
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
└── safeskillhub/               # safety skill library
    │── safe-gog
    │── safe-ordercli
    └── safe-...
```
---

## Usage 

* Step 1 — Set the System Prompt Copy the SafeClaw system prompt into your OpenClaw working directory so the agent loads it on startup.
  > AGENTS.md contains the full OpenClaw system prompt plus the L0 safety routing table. The routing table tells the agent which safety skill to invoke for each category of action (workspace calls → safe-gog, skill installs → skill-guard, code execution → safe-exec).
* Step 2 — Install the Safety Skills from `safeskillhub/`.
* Step 3 - Prioritise the Safety Skills in the System Prompt.

---
If you find this repository helpful, please cite:
```bibtex
@misc{wang2026safeclawrsafesecuremultiagent,
      title={SafeClaw-R: Towards Safe and Secure Multi-Agent Personal Assistants}, 
      author={Haoyu Wang and Zibo Xiao and Yedi Zhang and Christopher M. Poskitt and Jun Sun},
      year={2026},
      eprint={2603.28807},
      archivePrefix={arXiv},
      primaryClass={cs.CR},
      url={https://arxiv.org/abs/2603.28807}, 
}
```
