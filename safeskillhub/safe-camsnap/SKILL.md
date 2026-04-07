---
name: safe-camsnap
description: Safe wrapper for the camsnap skill. Use when interacting with RTSP/ONVIF cameras for snapshots, clips, or diagnostics under strict privacy, credential, and execution constraints. Trigger when the user asks to access cameras, capture images/videos, or monitor motion using camsnap.
---

# Safe CamSnap

This skill adds a safety layer on top of `camsnap`.

Use this skill whenever a task involves:
- cameras / RTSP / ONVIF
- `camsnap`
- snapshots or clips
- motion detection
- camera monitoring

For command syntax and normal product behavior, refer to the original `camsnap` skill.

## Safety Goals

This wrapper is designed to prevent:
1. exposure of camera credentials (usernames, passwords)
2. leakage of sensitive visual data (images, video)
3. unauthorized surveillance or continuous monitoring
4. unsafe automation via `watch --action` shell execution
5. unintended local network probing via camera discovery

## Enforcement Model

Actions are classified into three levels:

- `BLOCK`   — refuse outright
- `CONFIRM` — require explicit user approval
- `ALLOW`   — permitted without intervention

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Display or export camera credentials (`--user`, `--pass`, raw config.yaml contents, RTSP/connection URLs with embedded credentials) | BLOCK | CS-B01 | Never expose credentials in output or logs; includes connection strings and URLs containing embedded auth (refined r2) |
| Send snapshots/clips to external services, chat, email, or network endpoints (including disguised network paths like `/dev/tcp/`, named pipes, or non-local redirections) | BLOCK | CS-B02 | Prevent visual data exfiltration; validate output paths are genuine local filesystem locations (refined r2) |
| Use `watch --action` with any shell command | BLOCK | CS-B03 | Prevent uncontrolled arbitrary command execution |
| Output raw image or video data (base64, binary) into chat | BLOCK | CS-B04 | Prevent visual data leakage in conversation |
| Add camera with unknown or untrusted host | CONFIRM | CS-C01 | Require explicit host address and stated purpose |
| Capture snapshot (`camsnap snap`) | CONFIRM | CS-C02 | Confirm camera name, intent, and that output stays local |
| Capture clip (`camsnap clip`) | CONFIRM | CS-C03 | Confirm camera, duration, output path, and that clip stays local |
| Continuous monitoring (`camsnap watch`) without `--action` | CONFIRM | CS-C04 | Require explicit justification and bounded duration |
| Camera discovery (`camsnap discover`) | ALLOW | CS-A01 | Non-sensitive metadata enumeration |
| Health check (`camsnap doctor`) | ALLOW | CS-A02 | Diagnostic only; no data capture |
| List configured cameras (names and status only) | ALLOW | CS-A03 | No credentials shown; metadata only |

## Compound Request Resolution (refined r2)

When a single user request contains multiple sub-operations:
1. Evaluate each sub-operation independently against the safety rules.
2. If **any** sub-operation triggers BLOCK, that portion must be refused and the user informed.
3. Remaining sub-operations that are ALLOW or CONFIRM may proceed under their normal workflow.
4. Never allow a BLOCK-classified sub-operation to execute as a side-effect of completing an ALLOW or CONFIRM operation.

## Required Operating Constraints

1. Never output raw images, video, or base64-encoded media into chat.
2. Never expose credentials from config file or command-line flags.
3. Only operate on explicitly named cameras.
4. Require confirmation for any data capture (snapshot, clip, monitoring).
5. Block all `watch --action` commands unconditionally.
6. Treat all camera data as sensitive personal data.
7. Keep captured data local; never transmit to external endpoints.

## Confirmation Workflow

For any `CONFIRM` operation, follow this exact flow:

1. State the camera name and host address.
2. State the action (snapshot / clip / monitoring / add camera).
3. State the risk:
   - privacy exposure from visual data
   - sensitive environment capture
4. State the constraints:
   - output stays local only
   - no credential exposure
   - no external sharing
5. Ask for explicit confirmation.

Example:

> I am about to capture a snapshot from camera "kitchen" at 192.168.0.10. This may capture sensitive visual data. The image will be saved locally and will not be shared externally. Confirm?

## Output Policy

Allowed:
- "Snapshot saved to shot.jpg."
- "Camera 'kitchen' is reachable and streaming."
- "3 cameras configured: kitchen, garage, front-door."

Disallowed:
- raw image or video content in chat
- base64-encoded media
- camera credentials (usernames, passwords)
- full config file dumps

## Domain Notes

Unlike typical CLI tools, camsnap interacts with **physical-world sensors**. Camera data is inherently sensitive — it may capture home interiors, personal activity, or private spaces. All visual data must be treated as private user data. The `watch --action` feature poses a command injection risk and must be unconditionally blocked.

## (Trigger, Task, Resources)

**Trigger:** Activates when the user requests any camera interaction via `camsnap` — capturing snapshots or clips, monitoring motion, adding cameras, or running diagnostics on RTSP/ONVIF devices.

**Task:** If the action exposes credentials, sends visual data externally, outputs raw image/video into chat, or uses `watch --action` with shell commands → BLOCK. If the action captures a snapshot, clip, or starts monitoring, or adds an untrusted camera host → CONFIRM with camera identity, intent, and local-only storage constraint. Read-only operations (discover, doctor, list camera names) → ALLOW.

**Resources:** No auxiliary resources required. Enforcement is spec-driven; `references/risk-notes.md` provides threat model context.

## References

- Original skill: `camsnap`
- `references/risk-notes.md`
