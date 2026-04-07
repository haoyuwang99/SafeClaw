# Risk Notes for safe-1password

## Threat Model Summary

The original `1password` skill provides access to the 1Password CLI (`op`) for managing vaults, items, and secrets. Its common operations are:
- checking CLI version and account status
- signing in to one or more accounts
- listing vaults and items (metadata)
- reading specific fields from specific items
- injecting secrets into commands via `op inject` or `op run`
- troubleshooting desktop app integration and tmux setup

The skill requires access to credentials stored in 1Password vaults and executes authenticated CLI commands that can retrieve, expose, or indirectly transmit secret material.

## Main Risk Categories

### 1. Credential exposure (secrets, tokens, API keys)
Risk:
- `op read`, `op item get`, and similar commands emit raw secret values to stdout.
- If the agent captures, echoes, or returns that output in a response, secrets are exposed in conversation history, logs, or tmux pane buffers.
- Shell history may record secret values if they appear as command arguments.

Mitigation:
- Never return raw secret values in any response.
- Treat all field reads as confirm-level operations.
- Prohibit `tmux capture-pane` after any command that may emit a secret.
- Prefer `op run` / `op inject` so secrets are passed directly to the target process and never materialized in the agent's context.

### 2. Irreversibility (wrong-vault or wrong-account operations)
Risk:
- 1Password supports multiple accounts and vaults. A mis-scoped `op item delete`, `op document delete`, or vault modification targets the wrong data store.
- Deleted items may be recoverable from the trash for a limited time, but automated bulk operations can exceed that window.
- `op item edit` or `op document edit` overwrites existing values without a diff preview.

Mitigation:
- Require explicit account, vault, and item identification before any destructive or mutating operation.
- Treat all write/delete operations as confirm-level with a full scope summary.
- Refuse operations where account or vault is ambiguous or unspecified.

### 3. Scope explosion (bulk vault enumeration)
Risk:
- `op item list --vault <vault>` or `op vault list` across all vaults can reveal the full inventory of stored secrets, including item titles and metadata that may themselves be sensitive (e.g., "AWS prod root key").
- Bulk export via `op export` materializes the entire vault to disk in plaintext or encrypted-but-portable form.
- Iterating over all items to find a target is functionally equivalent to a full vault dump.

Mitigation:
- Block bulk export and unscoped item enumeration.
- Require the user to specify a narrow target (exact item title, UUID, or field) before listing.
- Limit `op item list` to a single named vault with a clear stated purpose.

### 4. External interaction (exfiltration via APIs or remote services)
Risk:
- `op run --env-file` or `op inject` followed by a curl/webhook call can silently transmit secrets to external endpoints.
- A maliciously crafted template or `.env` reference could route secrets to a remote host under the guise of a legitimate workflow.
- Clipboard sync tools integrated with the shell may capture pane output containing secrets.

Mitigation:
- Require an explicit command preview before executing `op run` or `op inject`.
- Refuse any workflow where the downstream command contacts an external URL that the user has not explicitly reviewed.
- Block pane captures and clipboard-adjacent workflows after secret-bearing commands.
- Prohibit piping `op read` output into curl, nc, ssh, or other network tools.

### 5. Privilege escalation (cross-account access)
Risk:
- When multiple 1Password accounts are configured, an ambiguous `op` command may default to a higher-privileged account (e.g., a business account instead of a personal one).
- A stale tmux session authenticated to a different account may be reused without the user's awareness.
- `OP_ACCOUNT` or `--account` flags, if omitted, allow the CLI to choose an account automatically.

Mitigation:
- Always surface the resolved account identity (`op whoami`) before any secret-bearing operation.
- Require explicit `--account` scoping when more than one account is configured.
- Refuse to reuse existing tmux sessions for new sign-in flows; always require a fresh session.
- Block operations that rely on ambient account selection when multiple accounts are present.

## Safe / Confirm / Block Examples

### Safe (ALLOW)
- `op --version` — check CLI availability
- `op whoami` — confirm currently authenticated account identity
- `op account list` — list configured accounts (no secret values)
- `op vault list` — list vault names and IDs (metadata only, single account)
- `op item list --vault Personal` — list item titles in a named vault (no field values)
- Troubleshooting desktop app integration or tmux session setup

### Confirm (CONFIRM)
- `op signin` inside a fresh dedicated tmux session for a specified account
- `op item get "GitHub Token" --vault Work --fields username` — read a specific non-password field from a named item
- `op inject -i template.env -o /dev/null` followed by a user-reviewed local command — secret injection with explicit command preview
- `op run -- <user-reviewed command>` — run a local command with secrets injected via environment
- `op item edit` or `op item delete` with explicit account, vault, and item confirmation

### Block (BLOCK)
- Returning any raw password, token, API key, private key, recovery code, or session token in a response
- `tmux capture-pane` after any command that may emit secret values
- Writing secrets to disk: `.env` files, shell rc files, temp files, plaintext configs
- `op export` or any bulk vault dump
- Piping `op read` into `curl`, `nc`, `ssh`, or any network-facing tool
- `op item list` without a named vault or with intent to iterate all items
- Any operation where account or vault identity is ambiguous and cannot be resolved before execution
- Reusing an existing tmux session of unknown authentication state for a new secret-bearing flow
