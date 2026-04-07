---
name: safe-1password
description: Safe wrapper for the 1password skill. Use when checking 1Password CLI availability, verifying account status, listing non-sensitive metadata, or performing carefully controlled secret operations through op with confirmation and redaction. Trigger when the user asks to use 1Password, op CLI, vault items, secrets, inject, signin, or tmux-based 1Password workflows.
---

# Safe 1Password CLI

This skill adds a safety layer on top of `1password`.

Use this skill whenever a task involves:
- `op`
- 1Password CLI
- vaults / items / secrets
- `op signin`, `op whoami`, `op vault list`
- `op read`, `op inject`, `op run`
- tmux-based 1Password workflows

For command syntax and product behavior, refer to the original `1password` skill and official 1Password documentation.

## Safety Goals

This wrapper is designed to prevent:
1. secret leakage into chat, logs, files, or pane captures
2. over-broad access to vault contents
3. unsafe secret materialization to disk or shell history
4. hidden exfiltration through captured terminal output
5. accidental execution against the wrong account or vault

## Enforcement Model

Actions are classified into three levels:

- `BLOCK`   — refuse outright
- `CONFIRM` — require explicit user approval with a risk summary
- `ALLOW`   — permitted under redaction and scope constraints

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Print, paste, or return raw secret values into chat/logs/code | BLOCK | OP-B01 | Refuse and explain that secrets must never be exposed in conversation output |
| Use `tmux capture-pane` or similar output capture after commands likely to reveal secret values | BLOCK | OP-B02 | Refuse unless command is metadata-only and redaction-safe |
| Write secret values to disk, temp files, dotenv files, shell rc files, or plaintext configs | BLOCK | OP-B03 | Refuse; recommend `op run` or `op inject` without materializing values |
| Send secrets to external URLs, APIs, email, clipboard sync, or remote shells | BLOCK | OP-B04 | Refuse as explicit exfiltration risk |
| Bulk export / enumerate vault items or documents without narrow user-specified scope | BLOCK | OP-B05 | Refuse broad retrieval and ask for a narrower target |
| Use unknown account, unknown vault, or untrusted tmux socket path | BLOCK | OP-B06 | Refuse until path/account/vault is clarified or allowlisted |
| `op whoami`, `op account list`, `op vault list` (metadata only) | ALLOW | OP-A01 | Allowed if output is non-sensitive and summarized safely |
| `op signin` or re-auth inside dedicated tmux session | CONFIRM | OP-C01 | Show account + session scope + no-secret-output policy before proceeding |
| Read a specific field (sensitive or non-sensitive) from a specific item | CONFIRM | OP-C02 | Require exact item/field/vault and redact returned value by default. For sensitive fields, only derived metadata (e.g., existence, length, last-modified) may be returned — never the raw value (refined r2) |
| `op inject` / `op run` for a user-requested local task | CONFIRM | OP-C03 | Require explicit command preview and prohibit returning secret-expanded output |
| Metadata inspection of a specific item (title, vault, tags, URLs) | ALLOW | OP-A02 | Allowed if secret-bearing fields are excluded |
| List items within a single user-specified vault (titles/metadata only, no secret fields) | ALLOW | OP-A04 | Allowed when the user specifies a single vault and output contains only non-secret metadata (titles, categories, tags). Distinct from OP-B05 which blocks unscoped cross-vault enumeration (refined r2) |
| Create, edit, delete, archive, or move a specific vault item | CONFIRM | OP-C04 | Require explicit confirmation with item name, vault, and operation type. Destructive operations (delete, archive) must state data-loss risk (refined r2) |
| Troubleshooting signin / app integration / tmux setup | ALLOW | OP-A03 | Allowed if no secrets are printed or persisted |

## Compound Request Policy (refined r2)

When a user request contains multiple sub-operations, decompose them and evaluate each independently. The overall verdict is the **strictest** among all sub-operations: BLOCK > CONFIRM > ALLOW. If any sub-operation is BLOCK, the entire compound request is BLOCK. Safe sub-operations before the blocked one should not be executed if they serve no purpose without the blocked step.

## Required Operating Constraints

1. Always use a fresh dedicated tmux session for interactive `op signin`.
2. Never reuse stale tmux sessions for secret-bearing flows.
3. Never capture pane output after any command that may reveal secret material.
4. Never quote raw secret values in the final response.
5. Prefer metadata summaries over raw command output.
6. Prefer `op run` / `op inject` over writing secrets to disk.
7. Limit operations to the user-requested account, vault, item, and field only.
8. If scope is ambiguous, stop and ask for narrowing details.

## Confirmation Workflow

For any `CONFIRM` operation, follow this exact flow:

1. State the intended operation in one sentence.
2. State the exact scope:
   - account
   - vault
   - item
   - field / command
3. State the main risk:
   - secret exposure
   - wrong-vault access
   - unsafe output capture
4. State the safety controls that will be applied:
   - dedicated tmux only
   - no pane capture of secret-bearing commands
   - redacted output only
   - no disk writes
5. Ask for explicit confirmation.

Example confirmation text:

> I am about to sign in to 1Password using `op signin` inside a fresh dedicated tmux session for account `<account>`. I will not capture or return any secret-bearing terminal output, and I will only verify authentication status unless you request a narrower follow-up action. Confirm?

## Output Policy

When responding to the user:
- Never include raw secret values
- Never include full captured terminal output from secret-bearing commands
- Summarize safe metadata only
- If a requested value is sensitive, report success/failure or masked form only

Allowed examples:
- "Sign-in succeeded for account X."
- "Vault Y is accessible."
- "The requested field exists and was injected into the local command without being exposed."

Disallowed examples:
- actual password
- token
- API key
- recovery code
- private key
- session token
- full secret-bearing pane capture

## Domain Notes

The original `1password` skill requires tmux and includes `capture-pane` in its sample workflow. That pattern is acceptable for metadata-only commands but unsafe for commands that may emit secrets. This wrapper therefore treats uncontrolled pane capture as high risk and defaults to redacted summaries only.

## (Trigger, Task, Resources)

**Trigger:** Activates whenever the user requests any operation involving the 1Password CLI (`op`), including vault/item access, secret retrieval, `op inject`/`op run`, sign-in, or tmux-based 1Password workflows.

**Task:** If the operation would expose raw secret values in chat, logs, files, or external channels, or involves bulk vault enumeration, uncontrolled pane capture after secret-bearing commands, or an unknown account/vault/socket path → BLOCK. If the operation is a sign-in, a read of a specific item field, an `op inject`/`op run` invocation, or a vault write/destructive operation (create, edit, delete, archive, move) → CONFIRM with a structured risk summary including account, vault, item scope, and applied safety controls. If the operation is metadata-only (`op whoami`, `op vault list`, single-vault item listing, troubleshooting) with no secret exposure → ALLOW. For compound requests containing multiple sub-operations, decompose and apply the strictest verdict (refined r2).

**Resources:** `references/risk-notes.md`

## References

- Original skill: `1password`
- `references/risk-notes.md`
- `config/allowlist.yaml`
- `scripts/check.py`
