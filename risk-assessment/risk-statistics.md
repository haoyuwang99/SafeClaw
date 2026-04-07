# OpenClaw Built-in Skills — Risk Statistics & Criteria

**Generated:** 2026-03-19 | **Last updated:** 2026-03-19 (post deep-review corrections)
**Scope:** 55 classified (52 git-tracked built-ins + 3 locally-added: safe, skill-logger, safety-confirm). 4 other locally-added L0 safety tools (context-guard, math-calculator, safe-exec, skill-guard) excluded from risk ranking.

> **Corrections applied after deep-review:**
> - `gh-issues`: 🟠 High → 🔴 Critical (--yes --cron = fully autonomous pipeline; issue body injection vector)
> - `oracle`: 🟠 High → 🟡 Medium (not Oracle Database — AI code bundler; read-only local; comparable to gemini/summarize)
> - `nano-banana-pro`: ❓ Unknown/🟠 High → 🟡 Medium (confirmed: Gemini image gen; well-scoped, comparable to openai-image-gen)
> - `ordercli`: 🔴 Critical → 🟠 High (Foodora food delivery CLI, not general financial infra)

---

## Risk Classification Criteria

### How Risk Level Is Determined

Each skill is assessed across **4 dimensions**, then assigned the highest applicable tier:

| Dimension | Questions Asked |
|---|---|
| **Reversibility** | Can the action be undone? Is there a recovery window? |
| **Blast Radius** | How many people or systems are affected if it goes wrong? |
| **Externality** | Does the action leave the machine (email, message, API call, order)? |
| **Sensitivity** | Does the action touch credentials, health data, private content, or financial data? |

---

### Risk Tiers

#### 🔴 Critical
**All of the following are true:**
- Action is irreversible OR has no recovery path
- Affects external parties OR exposes highly sensitive data
- Failure has significant personal, professional, financial, or legal consequences

**Examples:** sending an email, placing an order, accessing a credential vault, initiating a phone call, live camera surveillance

---

#### 🟠 High
**At least two of the following:**
- Action is difficult to reverse or recovery window is short
- Affects external systems, shared resources, or other people
- Can be destructive at scale (bulk delete, force push, mass message)
- Exposes private or sensitive data

**Examples:** posting to a shared channel, deleting git branches, running SQL writes, spawning code-executing agents, camera snapshots

---

#### 🟡 Medium
**At least one of the following:**
- Action affects cloud services or external APIs (data leaves the machine)
- Action can overwrite or delete local data without a recycle bin
- Large input/output could overwhelm context or cause performance issues
- Privacy concern (location, health, audio, session history)

**Examples:** Notion edits, Obsidian file delete, Gemini prompts with PII, large PDF loads, Bluetooth pairing

---

#### 🟢 Low
**All of the following:**
- Action is read-only or fully local
- Reversible (undo, trash, git revert)
- Does not expose sensitive data externally
- Failure has minimal real-world impact

**Examples:** weather queries, Spotify control, Sonos volume, local TTS, reading notes

---

#### ❓ Unknown
Skill scope is not documented. Treated as High until audited with `skill-guard`.

---

## Statistics: Initial Risk (Before Controls)

| Risk Level | Count | % of 52 | Skills |
|---|---|---|---|
| 🔴 Critical | **6** | **11.5%** | voice-call, peekaboo, gog, 1password, safe, **gh-issues** *(reclassified ↑)* |
| 🟠 High | **14** | **26.9%** | imsg, himalaya, discord, slack, wacli, bluebubbles, coding-agent, github, tmux, camsnap, clawhub, canvas*, ordercli *(reclassified ↓)*, **xurl** *(reclassified ↑ — X Twitter API, not URL fetcher)* |
| 🟡 Medium | **23** | **44.2%** | notion, obsidian, bear-notes, apple-notes, trello, goplaces, gemini, openai-image-gen, openai-whisper, openai-whisper-api, video-frames, blucli, eightctl, sag, skill-creator, skill-logger, session-logs, nano-pdf, summarize, **oracle** *(reclassified ↓)*, **nano-banana-pro** *(confirmed ↓)*, mcporter, **sonoscli** *(reclassified ↑ — same profile as blucli)* |
| 🟢 Low | **12** | **23.1%** | apple-reminders, things-mac, blogwatcher, gifgrep, songsee, spotify-player, sherpa-onnx-tts, openhue, healthcheck, safety-confirm, weather, model-usage |
| ❓ Unknown | **0** | **0%** | *(all resolved)* |

> *canvas, mcporter still have unconfirmed scope — classified conservatively

```
Initial Risk Distribution (52 skills, corrected)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 Critical █████                       11.5%  (6)  ← gh-issues ↑, ordercli ↓
🟠 High     ██████████                  25.0%  (13) ← oracle ↓, nano-banana-pro ↓
🟡 Medium   █████████████████           44.2%  (23) ← absorbed oracle + nano-banana-pro
🟢 Low      ██████████                  25.0%  (13)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  6+13+23+13 = 55 ← note: 55 includes 3 locally-added (safety-confirm, skill-logger, safe)
  Pure 52-baseline: ~36.5% are High or Critical risk
```

---

## Statistics: Residual Risk (After Confirm-Only Controls)

After applying `safety-confirm` as the sole control (the original report baseline):

| Risk Level | Count | % | Change from Initial |
|---|---|---|---|
| 🔴 Critical | **0** | **0%** | ↓ -6 (all reduced) |
| 🟠 High | **0** | **0%** | ↓ -14 (all reduced) |
| 🟡 Medium | **23** | **41.8%** | ↑ +1 (absorbed Critical/High) |
| 🟢 Low | **30** | **54.5%** | ↑ +17 |
| ❓ Unknown | **2** | **3.6%** | nano-banana-pro, mcporter |

**Problem identified:** 19 High/Critical skills only dropped to Medium — not Low.  
Confirmation alone is insufficient because:
- Users can accidentally confirm ("yes habit")
- No automatic prevention of known-bad patterns (SQL without WHERE, emergency calls)
- No pre-approved trusted paths that bypass friction for safe operations

---

## Statistics: Residual Risk (After 3-Tier Controls)

After applying the full **Hard Block + Auto-Mitigate + Confirm** model via safe wrapper skills:

| Risk Level | Count | % | Change from Confirm-Only |
|---|---|---|---|
| 🔴 Critical | **0** | **0%** | — |
| 🟠 High | **0** | **0%** | — |
| 🟡 Medium | **4** | **7.3%** | ↓ -19 |
| 🟢 Low | **49** | **89.1%** | ↑ +19 |
| ❓ Unknown | **2** | **3.6%** | nano-banana-pro, mcporter (audit pending) |

**Residual Medium (4 skills)** — these remain Medium because the risk is inherent to the domain and cannot be fully automated away:

| Skill | Why Still Medium |
|---|---|
| **peekaboo** | Live camera = real surveillance even with 60s cap + purpose gate; human oversight is always required |
| **1password** | Credential vault access; even with no-echo + allowlist, the data accessed is maximally sensitive |
| **safe** | Same as 1password + unknown scope adds uncertainty |
| **ordercli** | Food delivery orders (Foodora) — reclassified High (not Critical); real financial transactions still require amount cap + confirmation |

> **Note:** `gh-issues` was reclassified to Critical during deep review. It is NOT in the residual Medium list because its safe wrapper (safe-gh-issues) hard-blocks `--yes --cron`, mandates injection scanning, and requires diff review before PRs — bringing residual risk to Low.

```
Risk Comparison Across 3 Stages (52 skills, corrected)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                   Critical  High   Medium   Low   Unknown
Initial Risk         11.5%  25.0%   44.2%  19.2%    0%
After Confirm-Only    0%     0%     41.8%  54.5%   3.6%
After 3-Tier          0%     0%      7.3%  89.1%   3.6%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Risk Reduction Summary

| Metric | Value |
|---|---|
| Skills at Critical/High risk (initial, corrected) | 19 (36.5%) |
| Skills at Critical/High risk (after 3-tier) | 0 (0%) |
| Skills at Low risk (initial) | 10 (19.2%) |
| Skills at Low risk (after 3-tier) | 49 (89.1%) |
| Improvement in Low-risk coverage | +390% |
| Skills remaining Medium (irreducible) | 4 (7.3%) |
| Skills with pending audit | 2 (canvas, mcporter) |

## Post-Deep-Review Corrections Log

| Skill | Original | Corrected | Reason |
|---|---|---|---|
| gh-issues | 🟠 High | 🔴 Critical | Fully autonomous pipeline; --yes --cron = zero human oversight; issue body injection vector |
| oracle | 🟠 High | 🟡 Medium | Not Oracle Database — AI code bundler (send files to GPT); read-only locally; comparable to gemini/summarize |
| nano-banana-pro | ❓ Unknown | 🟡 Medium | Confirmed: Gemini 3 Pro image gen; well-scoped; comparable to openai-image-gen |
| ordercli | 🔴 Critical | 🟠 High | Foodora food delivery CLI, not general financial infrastructure |
| xurl | 🟡 Medium | 🟠 High | X (Twitter) API CLI — posts tweets, sends DMs, follows/blocks; not a URL fetcher. Safe wrapper was completely wrong. |
| blucli | 🟡 Medium | 🟡 Medium | Classification unchanged but wrapper completely rewritten — BluOS audio player CLI, not Bluetooth pairing |
| mcporter | ❓ Unknown | 🟡 Medium | MCP client CLI — scope now documented; `--stdio` is hard block (code execution), tool calls gated by write/read type |
| sonoscli | 🟢 Low | 🟡 Medium | Same risk profile as blucli (speaker control, volume changes, multi-room grouping) — classification inconsistency corrected |

---

## What "Residual Medium" Means

A skill stays at **Medium** after controls when:

1. **The action is inherently high-stakes** — even with confirmation, real harm is possible (financial, surveillance, credential access)
2. **Human oversight cannot be fully automated** — the final decision must remain with a human
3. **The control reduces but cannot eliminate risk** — hard blocks prevent the worst cases, but the allowed operations still carry meaningful risk

These 4 skills (peekaboo, 1password, safe, ordercli) should always be used with heightened personal awareness, regardless of which controls are in place.

---

*Generated by Stan (OpenClaw AI Assistant) — 2026-03-19*
