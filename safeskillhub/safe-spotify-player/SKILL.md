---
name: safe-spotify-player
description: Safe wrapper for the spotify-player skill. Use when controlling Spotify playback, searching tracks, managing devices, or importing authentication cookies via spogo or spotify_player CLI. Trigger when the user asks to play music, search Spotify, control playback, list devices, or configure Spotify CLI tools.
---

# Safe Spotify Player

This skill adds a safety layer on top of `spotify-player`.

Use this skill whenever a task involves:
- `spogo` or `spotify_player` CLI
- Spotify playback control (play, pause, next, prev)
- Spotify search
- Device listing or switching
- Cookie/credential import for Spotify authentication
- Spotify configuration files

For command syntax and product behavior, refer to the original `spotify-player` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. credential leakage (Spotify cookies, session tokens, client IDs)
2. unauthorized browser cookie extraction
3. unintended configuration changes to Spotify settings
4. excessive API usage or account abuse
5. exposure of listening history or account metadata

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe execution

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Print, log, or return raw Spotify cookies, session tokens, OAuth secrets, `client_id`, or `client_secret` values (refined r2) | BLOCK | SP-B01 | Refuse; credentials and config-derived identifiers must never appear in conversation output |
| Extract browser cookies without explicit user request (`spogo auth import`) | BLOCK | SP-B02 | Cookie import must be user-initiated with browser explicitly named |
| Modify `~/.config/spotify-player/app.toml` or other config files without user request | BLOCK | SP-B03 | Refuse unsolicited config changes |
| Send Spotify credentials or tokens to external URLs or services | BLOCK | SP-B04 | Refuse as exfiltration risk |
| Import cookies from a specific browser with explicit user request | CONFIRM | SP-C01 | Show browser name and confirm before running `spogo auth import` |
| Set or change `client_id` in Spotify config | CONFIRM | SP-C02 | Show the config change and confirm before writing |
| Switch playback device to a named device | CONFIRM | SP-C03 | Show target device name and confirm |
| Modify any Spotify config file (e.g. `app.toml`) at explicit user request, for settings other than `client_id` | CONFIRM | SP-C04 | Show the specific setting and new value, confirm before writing |
| Search tracks, albums, artists | ALLOW | SP-A01 | Safe read-only operation |
| Check playback status (`spogo status`) | ALLOW | SP-A02 | Safe read-only operation |
| Basic playback control (play, pause, next, prev) | ALLOW | SP-A03 | Safe user-initiated playback |
| List available devices (`spogo device list`) | ALLOW | SP-A04 | Safe metadata query |

---

## Required Operating Constraints

1. Never expose Spotify cookies, tokens, session credentials, `client_id`, or `client_secret` in output (refined r2).
2. Never import browser cookies without explicit user consent and browser specification.
3. Never modify Spotify config files without user confirmation.
4. Prefer `spogo` over `spotify_player` as the primary CLI.
5. Limit device switching to user-specified targets only.
6. Never bulk-export listening history or account data.

---

## Confirmation Workflow

For CONFIRM operations:

1. State action:
   - import cookies / change config / switch device
2. State scope:
   - browser name / config key / device name
3. State risk:
   - credential extraction / config modification / wrong device
4. Ask for confirmation

Example:

> I am about to import Spotify cookies from Chrome using `spogo auth import --browser chrome`. This will extract browser session data. Confirm?

---

## Output Policy

Allowed:
- track/album/artist search results
- playback status summaries
- device list names
- confirmation of successful operations

Disallowed:
- raw cookies or session tokens
- OAuth client secrets or `client_id` values (refined r2)
- full config file contents containing credentials
- browser session data

---

## Domain Notes

The original skill involves browser cookie extraction for authentication, which is inherently sensitive. The `spogo auth import` command accesses browser cookie stores directly. This wrapper treats all cookie/credential operations as high-risk and requires explicit user consent.

---

## (Trigger, Task, Resources)

**Trigger:** Activate when the user requests Spotify playback control, track/device search, cookie or credential import via `spogo`/`spotify_player` CLI, or modification of Spotify configuration files.

**Task:** ALLOW read-only operations such as search, playback status, and device listing. CONFIRM operations that involve credential extraction (browser cookie import), configuration changes (client_id, app.toml), or device switching — showing the target and scope before proceeding. BLOCK any attempt to expose raw cookies, session tokens, or OAuth secrets in output, or to send credentials to external services.

**Resources:** `references/risk-notes.md`

---

## References

- Original skill: `spotify-player`
- `references/risk-notes.md`
