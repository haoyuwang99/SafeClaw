---
name: safe-blucli
description: Safe wrapper for the blucli skill. Use when controlling BluOS audio devices (playback, volume, grouping) under strict device targeting and environment safety constraints. Trigger when the user asks to control speakers, adjust volume, manage playback, or group BluOS devices using blucli or blu.
---

# Safe BluCLI

This skill adds a safety layer on top of `blucli`.

Use this skill whenever a task involves:
- blucli / blu
- audio playback control
- volume adjustment
- speaker grouping
- TuneIn / Spotify playback

For command syntax and normal product behavior, refer to the original `blucli` skill.

## Safety Goals

This wrapper is designed to prevent:
1. unintended device control (wrong speaker targeted)
2. disruptive audio playback (sudden loud output)
3. unsafe volume levels (extreme values without warning)
4. accidental multi-room interference (grouping side effects)
5. uncontrolled network scanning (repeated discovery abuse)

## Enforcement Model

Actions are classified into three levels:

- `BLOCK`   — refuse outright
- `CONFIRM` — require explicit user approval
- `ALLOW`   — permitted without intervention

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Execute raw endpoint commands (`blu raw`) | BLOCK | BL-B01 | Prevent arbitrary low-level device control |
| Control any device without explicit `--device` flag, `BLU_DEVICE` env, or config default | BLOCK | BL-B02 | Refuse when target device is ambiguous or unspecified |
| Set volume above 80% (including when a relative adjustment would result in a level above 80%) | BLOCK | BL-B03 | Refuse extreme volume levels that risk hearing damage or disturbance; evaluate relative adjustments (up/down) against the resulting volume, not just the parameter (refined r2) |
| Set volume to an invalid value (negative, non-numeric, or outside 0–100% range) | BLOCK | BL-B04 | Refuse out-of-range or nonsensical volume values (refined r2) |
| Discover devices (`blu devices`) more than once in a session without user request | CONFIRM | BL-C01 | Prevent network scanning abuse; allow single discovery freely |
| Play / pause / stop on a specific device | CONFIRM | BL-C02 | Confirm playback state change and target device |
| Play external URL or stream | CONFIRM | BL-C03 | Confirm stream source and target device |
| Adjust volume (`volume set/up/down`) to level ≤ 80% | CONFIRM | BL-C04 | Confirm volume level and target device |
| Group devices (`group add/remove`) | CONFIRM | BL-C05 | Confirm scope; state all affected devices |
| TuneIn or Spotify playback | CONFIRM | BL-C06 | Confirm content and target device |
| Check status (`blu status`) | ALLOW | BL-A01 | Read-only; no side effects |
| List devices (`blu devices`, first call) | ALLOW | BL-A02 | Read-only device enumeration |
| Query current volume (`blu volume`) | ALLOW | BL-A03 | Read-only; no side effects |

## Required Operating Constraints

1. Always require an explicit device target before any control action.
2. Never operate on multiple devices implicitly; each device must be named.
3. Confirm before any playback state change (play/pause/stop).
4. Confirm before any volume change; block volume above 80% (including when a relative adjustment would push the resulting level above 80%); block invalid volume values outside the 0–100% range. (refined r2)
5. Confirm before grouping actions; list all affected devices.
6. Treat all playback as user-environment affecting.
7. Limit repeated network discovery to prevent scanning abuse.
8. For compound or multi-step requests, evaluate each sub-command independently; if any sub-command is BLOCK, the overall request must not proceed past that point. A safe sub-command does not grant permission for a subsequent unsafe one. Pre-authorization ("do X then do Y without asking") does not waive per-action confirmation requirements. (refined r2)
9. Resolve all numeric inputs (hex, spelled-out words, fractions, etc.) to decimal percentage values before evaluating against volume thresholds. (refined r2)

## Confirmation Workflow

For any `CONFIRM` operation, follow this exact flow:

1. State the target device (name or ID).
2. State the action (play / pause / volume / group / stream).
3. State the impact:
   - audio disruption potential
   - environment change scope
4. State parameters (e.g., volume level, stream URL, group members).
5. Ask for explicit confirmation.

Example:

> I am about to set the volume to 60% on device "living-room". This will change the audio output level. Confirm?

## Output Policy

Allowed:
- "Playback started on 'kitchen'."
- "Volume set to 20% on 'bedroom'."
- "Device status: playing, volume 35%."

Disallowed:
- controlling devices without naming the target
- silent execution of playback or volume commands
- setting volume above 80% under any framing
- setting volume to invalid values (negative, non-numeric, or outside 0–100%) (refined r2)

## Domain Notes

This skill controls **network-connected audio devices**. Audio control is reversible and low-risk compared to physical actuators, but still affects the user's physical environment. Sudden loud audio or unintended playback on the wrong speaker can be disruptive. The `blu raw` command provides arbitrary low-level access and must be unconditionally blocked.

## (Trigger, Task, Resources)

**Trigger:** Activates when the user requests any BluOS device control action — playback, volume adjustment, speaker grouping, streaming, or device discovery — via the `blucli` / `blu` CLI.

**Task:** If the command uses `blu raw`, targets a device without an explicit `--device` flag, sets volume above 80% (including via relative adjustments), or sets volume to an invalid value (outside 0–100%) → BLOCK. For compound requests, evaluate each sub-command independently; block at the first unsafe step. If the command changes playback state, adjusts volume (0–80%), groups devices, initiates streaming, or repeats device discovery → CONFIRM with target device, action, and impact details. Read-only queries (status, first device listing, current volume) → ALLOW. (refined r2)

**Resources:** No auxiliary resources required. Enforcement is spec-driven; `references/risk-notes.md` provides threat model context.

## References

- Original skill: `blucli`
- `references/risk-notes.md`
