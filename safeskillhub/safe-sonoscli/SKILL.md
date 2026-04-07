---
name: safe-sonoscli
description: Safe wrapper for the sonoscli skill. Use when controlling Sonos speakers via the sonos CLI under strict constraints preventing unauthorized playback, volume abuse, credential exposure, and unintended device targeting. Trigger when the user asks to control Sonos speakers, play music, adjust volume, discover speakers, or manage speaker groups.
---

# Safe Sonos CLI

This skill adds a safety layer on top of `sonoscli`.

Use this skill whenever a task involves:
- discovering Sonos speakers on the network
- controlling playback (play, pause, stop)
- adjusting volume
- managing speaker groups
- browsing favorites or queue
- Spotify search via SMAPI

For CLI commands and troubleshooting, refer to the original `sonoscli` skill.

## Safety Goals

This wrapper is designed to prevent:
1. unauthorized or unintended playback on wrong speakers
2. volume abuse (setting excessively high volume levels)
3. exposure of Spotify credentials (`SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`)
4. disruption of active listening sessions without confirmation
5. uncontrolled network scanning or discovery operations

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe execution

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Exposing or logging `SPOTIFY_CLIENT_ID` or `SPOTIFY_CLIENT_SECRET` | BLOCK | SN-B01 | Never expose Spotify credentials in output or logs |
| Setting volume above 95, regardless of user request (hard safety cap) | BLOCK | SN-B02 (refined) | Refuse; volume above 95 is never permitted even with explicit request |
| Setting volume 76-95 without explicit user request for a specific numeric level, OR when the request uses minimizing/manipulative language to downplay exceeding the safe threshold | BLOCK | SN-B02a (new) | Refuse; require a direct, unambiguous numeric request to exceed the safe range |
| Executing commands without specifying a target speaker (`--name` or `--ip`) | BLOCK | SN-B03 | Refuse; require explicit device targeting to prevent unintended playback |
| Running `sonos party` (group all speakers) | CONFIRM | SN-C01 | Warn that this affects all speakers on the network and confirm |
| Stopping or pausing playback on a speaker that may be in active use | CONFIRM | SN-C02 | Confirm before interrupting what may be an active session |
| Playing content on a specific speaker | CONFIRM | SN-C03 | State the speaker name and content, then confirm |
| Setting volume within 0-75, OR setting volume 76-95 with an explicit, direct user request for that specific numeric level (no minimizing language) | CONFIRM | SN-C04 (refined) | State the speaker and target volume level; warn if above 75; then confirm |
| Clearing the queue | CONFIRM | SN-C05 | Confirm before removing queued tracks |
| `sonos discover` to find speakers on the network | ALLOW | SN-A01 | Safe read-only network discovery |
| `sonos status --name <speaker>` to check current state | ALLOW | SN-A02 | Safe read-only operation |
| `sonos favorites list` to browse saved content | ALLOW | SN-A03 | Safe read-only operation |
| `sonos queue list` to view current queue | ALLOW | SN-A04 | Safe read-only operation |
| `sonos group status` to view grouping | ALLOW | SN-A05 | Safe read-only operation |
| Spotify search via SMAPI (read-only) | ALLOW | SN-A06 | Safe; search is non-destructive |

## Required Operating Constraints

1. Always require explicit speaker targeting via `--name` or `--ip`.
2. Never set volume above 95 under any circumstances. For volume 76-95, only proceed (with confirmation) when the user makes a direct, explicit numeric request without minimizing or manipulative language.
3. Never expose Spotify credentials in output, logs, or messages.
4. Confirm before any playback, pause, stop, or queue modification.
5. Confirm before grouping operations that affect multiple speakers.
6. Prefer status checks before issuing control commands.

## Confirmation Workflow

For CONFIRM operations:

1. State the intended action (play / pause / stop / volume / group / clear queue).
2. State the target:
   - speaker name or IP
   - content (for play operations)
3. State the risk:
   - may interrupt active session
   - affects multiple speakers (for group operations)
   - volume level change
4. Ask for explicit confirmation.

Example:

> I am about to play the favorite "Jazz Chill" on speaker "Kitchen" and set volume to 30. This may interrupt any currently playing content on that speaker. Confirm?

## Output Policy

Allowed:
- speaker discovery results
- playback status summaries
- queue and favorites listings
- group status information

Disallowed:
- Spotify client credentials
- raw environment variable values
- unfiltered error output containing credentials

## Domain Notes

The sonoscli tool operates on the local network and affects physical devices. Unlike software-only tools, actions have immediate real-world effects (audio playback in physical spaces), making confirmation especially important to prevent disruption.

## (Trigger, Task, Resources)

**Trigger:** Activate when the user asks to control Sonos speakers, play or pause music, adjust volume, discover speakers, manage speaker groups, or browse favorites and queues via the `sonos` CLI.

**Task:** Inspect each Sonos CLI command against the safety rules. BLOCK if the command would expose Spotify credentials, set volume above 95 (hard cap), set volume 76-95 without an explicit direct numeric user request (or with minimizing/manipulative language), or execute without specifying a target speaker via `--name` or `--ip`. CONFIRM before playing content, adjusting volume (including 76-95 with valid explicit request), stopping/pausing active sessions, grouping all speakers, or clearing the queue. ALLOW read-only operations such as speaker discovery, status checks, favorites/queue listing, group status, and Spotify search.

**Resources:** No auxiliary resources required.

## References

- Original skill: `sonoscli`
- `references/risk-notes.md`
