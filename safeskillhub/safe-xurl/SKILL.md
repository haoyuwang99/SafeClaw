---
name: safe-xurl
description: Safe wrapper for the xurl skill. Use when interacting with the X (Twitter) API via xurl CLI under strict credential protection, content confirmation, and scope constraints. Trigger when the user asks to post tweets, reply, search, send DMs, manage followers, upload media, or interact with any X API endpoint.
---

# Safe xurl

This skill adds a safety layer on top of `xurl`.

Use this skill whenever a task involves:
- posting, replying, quoting, or deleting tweets
- X (Twitter) API interactions
- `xurl` CLI
- DMs, follows, blocks, likes, reposts
- media upload to X
- X API raw endpoint access

For command syntax, refer to the original `xurl` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. credential exposure (~/.xurl, auth tokens, API keys)
2. unsolicited or unreviewed public posts
3. unsolicited direct messages
4. bulk or automated engagement (mass follow/like/repost)
5. destructive actions without confirmation (delete, block)
6. data exfiltration via media upload

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval with risk summary
- ALLOW   — safe operation

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Read, print, or expose `~/.xurl` contents or auth tokens | BLOCK | XU-B01 | Never expose credential file, tokens, or API keys |
| Use `--verbose`/`-v` flag (leaks auth headers) | BLOCK | XU-B02 | Refuse; verbose mode exposes sensitive headers |
| Use inline secret flags (`--bearer-token`, `--consumer-key`, `--consumer-secret`, `--access-token`, `--token-secret`, `--client-id`, `--client-secret`) | BLOCK | XU-B03 | Refuse all inline credential flags in agent context |
| Bulk or looped engagement actions (mass follow, like, repost, DM) | BLOCK | XU-B04 | Refuse automated bulk social actions |
| Post, reply, or quote without explicit user-provided content | BLOCK | XU-B05 | Refuse unless user explicitly provides the text to publish |
| Register app credentials or run auth commands with inline secrets | BLOCK | XU-B06 | Must be done manually by user outside agent context |
| Post a tweet with user-provided text | CONFIRM | XU-C01 | Show exact text to be posted; confirm before publishing |
| Reply to a post with user-provided text | CONFIRM | XU-C02 | Show target post ID, reply text; confirm before publishing |
| Quote a post with user-provided text | CONFIRM | XU-C03 | Show target post ID, quote text; confirm before publishing |
| Send a DM with user-provided text | CONFIRM | XU-C04 | Show recipient handle, message text; confirm before sending |
| Delete a post | CONFIRM | XU-C05 | Show post ID; confirm destructive action |
| Follow or unfollow a user | CONFIRM | XU-C06 | Show handle; confirm social graph change |
| Block or unblock a user | CONFIRM | XU-C07 | Show handle; confirm before blocking/unblocking |
| Upload media | CONFIRM | XU-C08 | Show file path; confirm before uploading to external service |
| Like or repost a post | CONFIRM | XU-C09 | Show post ID; confirm public engagement action |
| `xurl auth oauth2` (authenticate) | CONFIRM | XU-C10 | Confirm intent to start OAuth flow |
| Read a post (`xurl read`) | ALLOW | XU-A01 | Safe read-only operation |
| Search posts (`xurl search`) | ALLOW | XU-A02 | Safe read-only operation |
| View timeline or mentions | ALLOW | XU-A03 | Safe read-only operation |
| Check auth status (`xurl auth status`) | ALLOW | XU-A04 | Safe metadata check |
| View own profile (`xurl whoami`) | ALLOW | XU-A05 | Safe read-only operation |
| Look up user profile (`xurl user`) | ALLOW | XU-A06 | Safe read-only operation |
| List bookmarks or likes | ALLOW | XU-A07 | Safe read-only operation |
| List followers or following | ALLOW | XU-A08 | Safe read-only operation |
| List DMs (read-only) | ALLOW | XU-A09 | Safe read-only operation |
| Check media status | ALLOW | XU-A10 | Safe read-only operation |

---

## Required Operating Constraints

1. Never read, display, or transmit `~/.xurl` contents.
2. Never use `--verbose`/`-v` in any xurl command.
3. Never use inline secret flags in any xurl command.
4. Never post, reply, quote, or DM without explicit user-provided text.
5. Always show exact content before any public-facing action.
6. Never automate bulk engagement (follow/like/repost loops).
7. Confirm all destructive actions (delete, block).
8. Confirm all social graph changes (follow, unfollow, block, unblock).
9. If post content or recipient is ambiguous, stop and ask for clarification.
10. App registration and inline-secret auth must be done by the user outside agent context.

---

## Confirmation Workflow

For CONFIRM operations:

1. State the action (post / reply / quote / DM / delete / follow / upload)
2. State the exact content or target:
   - post text
   - recipient handle
   - post ID
   - file path
3. State risk:
   - public visibility (posts, likes, reposts)
   - irreversibility (delete, block)
   - external data transfer (media upload)
   - unsolicited contact (DM)
4. Ask for confirmation

Example (post):

> I am about to post the following tweet: "Hello world!" This will be publicly visible on your X account. Confirm?

Example (DM):

> I am about to send a DM to @someuser with the text "Hey, saw your post!". This will be delivered directly to the recipient. Confirm?

---

## Output Policy

Allowed:
- "Tweet posted successfully. ID: 1234567890"
- "Reply sent to post 1234567890."
- "Search returned 10 results for 'golang'."
- "Auth status: authenticated as @handle."

Disallowed:
- raw `~/.xurl` file contents
- auth tokens, API keys, bearer tokens
- verbose/debug output containing headers
- full unfiltered bulk API response dumps

---

## Domain Notes

X (Twitter) is a **public social media platform**. Posts, likes, reposts, and follows are publicly visible and linked to the user's identity. This makes unreviewed content publication especially risky — mistakes are immediately public and may be difficult to retract.

DMs, while private, constitute unsolicited contact and carry harassment risk. Bulk engagement actions (mass follow/like) can trigger platform enforcement (rate limits, suspensions).

The `~/.xurl` credential file and verbose mode are explicitly flagged as sensitive by the original skill itself. This wrapper enforces those constraints strictly.

---

## (Trigger, Task, Resources)

**Trigger:** Activate when the user requests any interaction with the X (Twitter) API via the `xurl` CLI, including posting, replying, DMs, follows, blocks, likes, media uploads, searches, or timeline viewing.

**Task:** Enforce credential protection and content confirmation for all public-facing or social-graph-modifying actions. BLOCK exposure of `~/.xurl` credentials, use of `--verbose` or inline secret flags, bulk/looped engagement actions, and posts without explicit user-provided text. CONFIRM all write operations — posting, replying, quoting, DMs, deletes, follows, blocks, media uploads, likes, reposts, and OAuth flows — by showing the exact content or target and associated risks before proceeding. ALLOW read-only operations such as reading posts, searching, viewing timelines, checking auth status, and listing followers or bookmarks.

**Resources:** `references/risk-notes.md` — threat model and risk rationale for the xurl skill. No auxiliary config or scripts required.

---

## References

- Original skill: `xurl`
- `references/risk-notes.md`
