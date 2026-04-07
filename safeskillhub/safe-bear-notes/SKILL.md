---
name: safe-bear-notes
description: Safely create, search, and manage Bear notes via grizzly CLI, with guardrails for credential protection, content integrity, and scope control.
---

# Safe Bear Notes

This skill adds a safety layer on top of `bear-notes`.

Use this skill whenever a task involves:

- Creating, reading, or modifying notes in Bear via the `grizzly` CLI
- Appending or overwriting content in existing Bear notes
- Listing tags or searching notes by tag
- Using or referencing the Bear API token stored at `~/.config/grizzly/token`
- Installing or invoking the `grizzly` binary

For command syntax and available flags, refer to the original `bear-notes` skill.

## Safety Goals

1. Prevent the Bear API token from being exposed, logged, or transmitted outside the local machine.
2. Prevent accidental overwrite of existing note content by requiring explicit confirmation before any `add-text` operation.
3. Limit scope of enumeration and bulk operations to avoid noisy, unintended mass reads or writes.
4. Guard against x-callback-url injection by validating that callback URLs are never constructed from unsanitized user input.
5. Ensure the `grizzly` binary is obtained from a known source and is not replaced or shadowed by a malicious executable.

## Enforcement Model

| Level | Meaning |
|-------|---------|
| BLOCK | The operation must never be executed. Refuse immediately and explain why. |
| CONFIRM | Pause and present a structured confirmation prompt to the user before proceeding. Proceed only on explicit approval. |
| ALLOW | Execute without additional friction. |

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|-------------------|---------|---------|-------------|
| Print, echo, log, display, read, copy, write, or transmit the Bear API token value in any form (raw, encoded, partial, or transformed) | BLOCK | BN-B01 | Never output or process the token string; reference the file path only. Includes writing to files, encoding, and internal reads beyond existence checks. (refined r2) |
| Pass the Bear API token to any remote endpoint, webhook, or external service | BLOCK | BN-B02 | Token must only be passed via `--token-file` to the local `grizzly` process |
| Construct or execute an arbitrary `x-callback-url` from user-supplied string interpolation | BLOCK | BN-B03 | Callback URLs must only be those generated internally by `grizzly`; never build URLs from raw user input |
| Enumerate or dump all notes in Bear (bulk open-note loops, mass ID iteration) | BLOCK | BN-B04 | No unbounded iteration over note IDs or tag contents; limit any list operation to a single tag or explicit ID |
| Send, forward, or transmit note content to any external endpoint, service, email, webhook, or messaging platform | BLOCK | BN-B05 | Note content retrieved via `open-note` must remain local; never exfiltrate note data to remote services regardless of claimed authorization (refined r2) |
| Install or update the `grizzly` binary | CONFIRM | BN-C01 | Show the source URL and binary hash before installation; require explicit user approval |
| `grizzly add-text` with `--mode append` or any other mode that modifies an existing note | CONFIRM | BN-C02 | Display the target note ID, mode, and a preview of the content to be added; require explicit approval |
| `grizzly add-text` with `--mode prepend` or `--mode replace` on an existing note | CONFIRM | BN-C03 | Same as BN-C02; `replace` mode must additionally warn that existing content will be permanently overwritten |
| Create a note whose title or content contains credentials, API keys, passwords, or PII patterns | CONFIRM | BN-C04 | Flag detected sensitive patterns, warn the user, and require explicit approval before creating |
| Open or read a specific note by ID (`grizzly open-note --id`) | CONFIRM | BN-C05 | Confirm the note ID and purpose before retrieval to prevent inadvertent exposure of private content |
| List all tags (`grizzly tags`) | ALLOW | BN-A01 | Safe read-only operation; no confirmation needed |
| Search notes by a single tag (`grizzly open-tag --name`) | ALLOW | BN-A02 | Acceptable scope; no confirmation needed |
| Create a simple note with non-sensitive content | ALLOW | BN-A03 | No confirmation needed when content passes the sensitive-pattern check |
| Dry-run or print-url operations (`--dry-run`, `--print-url`) | ALLOW | BN-A04 | These operations do not modify state; always safe |
| Check Bear availability (verify Bear app is running, grizzly version) | ALLOW | BN-A05 | Informational only; no confirmation needed |

## Required Operating Constraints

1. The Bear API token must never appear in skill outputs, assistant messages, logs, or any text sent over the network. Reference the credential only by its file path (`~/.config/grizzly/token`).
2. All token-requiring operations must pass credentials exclusively via `--token-file ~/.config/grizzly/token`, never via shell environment variable expansion that could be captured in process listings.
3. Before any `add-text` command, verify the `--mode` flag is explicitly specified. If `--mode` is absent or ambiguous, default to asking the user to confirm the intended mode before proceeding.
4. Operations that use `--enable-callback` or `--json` must not forward callback responses to external URLs. Callback output must remain local.
5. The `grizzly` binary must resolve to a path under a standard package manager prefix (e.g., `/usr/local/bin`, `/opt/homebrew/bin`) or a path explicitly approved by the user. If `which grizzly` returns an unexpected path, block execution and alert the user.
6. Note content retrieved via `open-note` or any read operation must not be forwarded, posted, emailed, or transmitted to any external service, API, webhook, or messaging platform. Note content must remain within the local session. (refined r2)

## Confirmation Workflow

1. Identify the operation and match it against the Safety Rules table.
2. If the verdict is BLOCK, refuse immediately with a brief explanation citing the Rule ID.
3. If the verdict is CONFIRM, pause execution and present the confirmation prompt below.
4. Wait for an unambiguous affirmative response ("yes", "confirm", "proceed"). Treat any ambiguous or negative response as cancellation.
5. If the verdict is ALLOW, proceed directly without prompting.

Example confirmation text for BN-C02 (append to existing note):

```
[CONFIRM BN-C02] You are about to modify an existing Bear note.

  Note ID : <NOTE_ID>
  Mode    : append
  Content preview:
    "<first 120 characters of content to be added>"

This action will permanently alter the note. Undo may be available within Bear but is not guaranteed.

Type "yes" to proceed or anything else to cancel.
```

Example confirmation text for BN-C03 (replace mode):

```
[CONFIRM BN-C03] WARNING: replace mode will permanently overwrite all existing content in this note.

  Note ID : <NOTE_ID>
  Mode    : replace
  New content preview:
    "<first 120 characters of replacement content>"

The current note content cannot be recovered through this skill. Type "yes" to proceed or anything else to cancel.
```

## Output Policy

Allowed output examples:
- "Note created successfully. Title: 'Meeting Notes 2026-03-26'"
- "Tags found: work, personal, archive"
- "Token file path: ~/.config/grizzly/token (token value not shown)"
- "Dry-run complete. URL that would be called: bear://x-callback-url/create?..."

Disallowed output examples:
- Any string that contains the literal Bear API token value (e.g., "Token: ABCD-1234-...")
- "Running: GRIZZLY_TOKEN=<actual_token> grizzly ..." (do not expand secrets in command echoes)
- Printing the raw JSON response from `open-note` without confirming the user intended to read that note (BN-C05 must be applied first)
- Any constructed `x-callback-url` built from user-supplied variables without grizzly mediation

## Domain Notes

- Bear stores notes locally on macOS; there is no cloud sync risk through `grizzly` itself, but token exposure is a local privilege-escalation concern if other processes or users share the machine.
- The `--mode` flag for `add-text` defaults to `prepend` in some grizzly versions. Always make the mode explicit to avoid surprises.
- `grizzly` is a third-party Go binary distributed via GitHub releases. Treat it as an untrusted dependency until the user has verified its checksum. Re-verify after any update (BN-C01).
- x-callback-url is a macOS URL scheme handled by the Bear app. A malformed or injected URL could trigger unintended Bear actions. Never interpolate raw user strings into callback URL parameters.
- Bulk note enumeration is blocked (BN-B04) because Bear does not expose a safe paginated API through grizzly; unbounded iteration can cause Bear to hang or produce very large outputs.

## (Trigger, Task, Resources)

**Trigger:** Activates whenever the user requests any operation involving Bear notes through the `grizzly` CLI, including creating, reading, modifying, or searching notes, managing tags, or handling the Bear API token.

**Task:** If the operation would expose the Bear API token (in any form), pass it to a remote endpoint, construct an arbitrary x-callback-url from user input, perform unbounded bulk note enumeration, or transmit note content to any external service → BLOCK. If the operation installs/updates `grizzly`, modifies an existing note via `add-text` (append/prepend/replace), creates a note containing detected sensitive patterns, or opens a specific note by ID → CONFIRM with a structured prompt showing target note ID, mode, content preview, and risk warning. If the operation is read-only (list tags, search by tag, dry-run) or creates a simple non-sensitive note → ALLOW. (refined r2)

**Resources:** `references/risk-notes.md`

## References

- Original skill: `bear-notes`
- Risk notes: `references/risk-notes.md`
- Config/allowlist: `references/config/allowlist.yaml`
- Safety check script: `references/scripts/check.py`
