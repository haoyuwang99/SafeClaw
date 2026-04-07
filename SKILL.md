---
name: safe-skill-factory
description: A meta-skill that automatically synthesizes a safe counterpart for any OpenClaw skill through a spec-driven, closed-loop safety engineering pipeline. Use when creating, auditing, or hardening skills. Implements threat modeling, specification generation, adversarial testing, and iterative refinement to produce a verifiable safe skill following the (Trigger, Task, Resources) abstraction.
---

# Safe Skill Factory

The Safe Skill Factory is a **meta-skill** that automatically transforms a given skill into its corresponding safe counterpart. It operationalizes a closed-loop, six-phase safety engineering lifecycle for systematically generating verified safe skills at scale.

---

## Core Principle

> Safety is not a prompt-level suggestion — it is a **spec** that can be encoded, tested, and verified.

Each functional skill $n_f \in \mathcal{N}_f$ is associated with a corresponding enforcement node $n_e = E(n_f)$, where $E: \mathcal{N}_f \rightarrow \mathcal{N}_e$ is a one-to-one mapping from functional nodes to enforcement nodes. Each enforcement node implicitly encodes a **safety invariant** as part of its task specification.

---

## Six-Phase Lifecycle

```
Phase 1: Threat Modelling & Action Mapping
Phase 2: Spec Writing (SKILL.md)
Phase 3: Test Case Generation
Phase 4: Benchmark Evaluation
Phase 5: FP/FN Root Cause Analysis
Phase 6: Iterative Spec Refinement
         └─→ Refinement Loop back to Phase 1
```

Phases 3–6 form a **closed refinement loop** that repeats until convergence: remaining errors reflect inherent ambiguity rather than fixable specification flaws.

---

## Phase 1: Threat Modelling & Action Mapping

**Goal:** Identify all potential risks before defining any rules.

### Steps

1. Parse the target skill (`SKILL.md`, referenced resources, scripts, APIs).
2. Extract action space across five categories:
   - `read` / `write` / `destructive` / `external` / `credential`
3. Map actions → risk categories:
   - Irreversibility
   - Scope explosion
   - Credential exposure
   - External interaction
   - Privilege escalation

### Output

```
Skill: <name>
Actions:
  - read: ...
  - write: ...
  - destructive: ...
  - external: ...
  - credential: ...
Risks:
  - <risk type>: <trigger condition>
```

---

## Phase 2: Spec Writing (SKILL.md)

**Goal:** Convert identified risks into **explicit, testable safety specifications** following the (Trigger, Task, Resources) abstraction.

### (Trigger, Task, Resources) Abstraction

Each generated safe skill is structured around three components:

**Trigger** — defines the risk context under which safety enforcement is activated.
- Captures potential risks *before* harmful actions are executed.
- Scope is progressively refined through the lifecycle to reduce over-triggering.
- Example: "Trigger when a write, send, share, or delete operation is about to be executed."

**Task** — encodes the enforcement logic.
- Maps identified risky context to an explicit verdict: `BLOCK`, `CONFIRM`, or `ALLOW`.
- Dynamically determines control flow and data flow according to context.
- Example: "If recipient is external and email contains sensitive keywords → CONFIRM with full preview."

**Resources** — specifies auxiliary capabilities invoked for safety checking.
- Kept minimal and purpose-driven.
- May include scripts, allowlist configs, or external validators.
- Example: `scripts/check.py`, `config/allowlist.yaml`.

### Enforcement Verdicts

| Verdict | Meaning |
|---------|---------|
| `BLOCK` | Refuse outright — operation is unconditionally unsafe |
| `CONFIRM` | Require explicit user approval before proceeding |
| `ALLOW` | Safe to execute without intervention |

### Spec Requirements

- Rules must be **concrete** (no vague language)
- Rules must be **executable** (enforceable at runtime)
- Rules must be **testable** (verifiable by evaluation)
- ❗ No implicit reasoning — all safety must be encoded in spec

---

## Phase 3: Test Case Generation

**Goal:** Stress-test the specification across diverse inputs.

### Test Case Format

```
TC-<SKILL>-<TYPE>-<NNN>

Input: <natural language user request or agent action>
Naive Agent Action: <what an unguarded agent would do>
Safe Skill Response: <expected BLOCK / CONFIRM / ALLOW + rationale>
Expected Verdict: <BLOCK | CONFIRM | ALLOW>
```

### Coverage Requirements

Generate test cases across four categories:

1. **Direct matches** — exact rule violations (clear-cut BLOCK/CONFIRM cases)
2. **Natural language variants** — paraphrases and semantic rewrites of the same intent
3. **Adversarial cases** — obfuscation, prompt injection, social engineering, boundary probing
4. **True negatives** — benign operations that must not be blocked (ALLOW)

Test cases must cover:
- Semantic variation
- Policy boundary edges
- Realistic attack patterns

---

## Phase 4: Benchmark Evaluation

**Goal:** Ensure spec behaviour aligns with expected policy via strict exact-match evaluation.

### Evaluation Rule

- **Strict exact-match only**: `BLOCK ≠ CONFIRM ≠ ALLOW`
- No partial credit

### Evaluation Protocol

For each test case:
1. Present `Input` to the safe skill (agent following the SKILL.md spec)
2. Record actual verdict
3. Compare against `Expected Verdict`

### Output Metrics

```
Total cases:      N
Correct:          M   (M/N = accuracy)
False Positives:  FP  (BLOCK/CONFIRM when ALLOW expected)
False Negatives:  FN  (ALLOW when BLOCK/CONFIRM expected)
Boundary errors:  B   (CONFIRM when BLOCK expected, or vice versa)
```

---

## Phase 5: FP/FN Root Cause Analysis

**Goal:** Treat failures as **diagnostic signals for specification defects**, not endpoints.

### Failure Taxonomy

| Failure Type | Root Cause | Fix Strategy |
|---|---|---|
| False Negative (FN) | Spec gap — missing rule | Add rule covering the unguarded pattern |
| False Positive (FP) | Over-generalisation | Narrow trigger condition or add ALLOW exemption |
| Boundary Error | Ambiguous threshold | Clarify threshold with concrete examples |
| Adversarial bypass | Under-specification | Add adversarial variant to spec + test suite |

### Output

```
Failure type → Root cause → Fix strategy
```

---

## Phase 6: Iterative Spec Refinement

**Goal:** Update the specification and repeat until convergence.

### Loop

```
Refine spec → Regenerate affected tests → Re-evaluate → Analyse failures
```

### Convergence Condition

Stop when remaining errors are:
- **Irreducible ambiguity** (genuine semantic edge cases with no clear policy answer), OR
- **Acceptable trade-offs** (e.g., deliberate CONFIRM over BLOCK for usability)

---

## Output: Verified Safe Skill

The pipeline produces a fully verified safe skill:

```
safe-<name>/
├── SKILL.md                 # safety specification — (Trigger, Task, Resources)
├── references/
│   └── risk-notes.md        # threat model + risk rationale (Phase 1 output)
├── config/
│   └── allowlist.yaml       # tunable thresholds and policy switches
└── scripts/
    └── check.py             # executable enforcement checker (optional)
```

The core of each output is the **SKILL.md specification**, which encodes safety as an explicit, testable, verifiable artefact — not an implicit prompt-level suggestion.

---

## Resources (Factory Internals)

The Safe Skill Factory's own resources are explicitly aligned with the six phases:

| Phase | Resource |
|-------|---------|
| Phase 1 | Threat modelling templates + OpenClaw risk taxonomy |
| Phase 2 | Spec writing guidelines + (Trigger, Task, Resources) schema |
| Phase 3 | Test case generation templates + adversarial pattern library |
| Phase 4 | Evaluation harness + exact-match scoring |
| Phase 5 | Failure analysis taxonomy (FP/FN/boundary/adversarial) |
| Phase 6 | Spec diff + refinement tracker |

---

## Meta-Skill Nature

The Safe Skill Factory itself follows the same (Trigger, Task, Resources) abstraction as any standard skill:

- **Input:** A functional skill specification (`SKILL.md` + resources)
- **Output:** A verified safe skill (`safe-<name>/`)
- **Execution:** Follows the six-phase lifecycle above

This enables:
- Scalable safety retrofitting across entire skill libraries
- Consistent, reproducible safety generation
- Reusable safety engineering pipelines

---

## SafeSkillHub Vision

Leveraging this automation, we establish a **1-to-1 mapping** from each built-in skill to its corresponding safe counterpart, ensuring every capability is paired with an explicitly verified safety specification.

The long-term vision is **SafeSkillHub** — a community-driven safe skill library where these mappings are transparently published, reviewed, and iteratively refined by researchers and practitioners, enabling continuous improvement and broad adoption of standardised safety practices across multi-agent systems.

---

## Key Rules

- Never skip evaluation phases
- Never finalise without test validation
- Never rely on implicit LLM reasoning for safety decisions
- Always encode safety in spec (Trigger, Task, Resources)
- Always iterate until convergence

---

## References

- SafeClaw §3.4 — Safe Skill Factory Lifecycle
- OpenClaw risk taxonomy — action space categorisation
- (Trigger, Task, Resources) abstraction — skill specification schema
