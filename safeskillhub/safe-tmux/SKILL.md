---
name: safe-tmux
description: Safe wrapper for the tmux skill. Use when controlling tmux sessions — sending keystrokes, capturing pane output, managing sessions/windows/panes, or interacting with interactive CLIs like Claude Code inside tmux. Trigger when the user asks to send input to tmux, capture terminal output, manage sessions, or interact with running processes in tmux.
---

# Safe tmux Session Control

This skill adds a safety layer on top of `tmux`.

Use this skill whenever a task involves:
- `tmux send-keys`
- `tmux capture-pane`
- tmux session/window/pane management
- interacting with interactive CLIs in tmux (Claude Code, etc.)
- killing or creating tmux sessions

For command syntax and product behavior, refer to the original `tmux` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. unintended command execution in wrong sessions/panes
2. secret leakage via pane capture of sensitive output
3. destructive session termination (kill-session/kill-server)
4. unauthorized input injection into interactive sessions
5. accidental disruption of running processes (Ctrl+C, Ctrl+D, Ctrl+Z)

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe execution

For compound requests containing multiple operations, each operation is evaluated independently. The most restrictive verdict governs: if any component is BLOCK, the blocked component is refused (other safe components may proceed). If the most restrictive component is CONFIRM, confirmation is required before proceeding.

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| `tmux kill-server` (terminates all sessions) | BLOCK | TX-B01 | Refuse; would destroy all tmux sessions and running processes |
| Capture pane output that may contain secrets (after op, password, token commands) | BLOCK | TX-B02 | Refuse pane capture after secret-bearing commands |
| Send destructive key sequences (Ctrl+C, Ctrl+D, Ctrl+Z) to a session without user request | BLOCK | TX-B03 | Only send process-interrupting keys when explicitly requested |
| Send arbitrary commands to a session the user did not specify | BLOCK | TX-B04 | Refuse; target session must be user-specified |
| Kill a specific tmux session (`kill-session`) | CONFIRM | TX-C01 | Show session name and running processes; confirm |
| Send keystrokes to a user-specified session | CONFIRM | TX-C02 | Show target session, exact keys/command to send; confirm |
| Send destructive key sequences (Ctrl+C, Ctrl+D, Ctrl+Z) when explicitly requested | CONFIRM | TX-C03 | Confirm target session and intent |
| Create a new tmux session | CONFIRM | TX-C04 | Show session name; confirm |
| Approve prompts in interactive sessions (send 'y' + Enter) | CONFIRM | TX-C05 | Show session name and visible prompt context; confirm |
| List sessions (`tmux ls`, `tmux list-sessions`) | ALLOW | TX-A01 | Safe read-only metadata |
| Capture pane output from user-specified session (non-sensitive context) | ALLOW | TX-A02 | Allowed for status checks on user-specified sessions |
| List windows/panes in a session | ALLOW | TX-A03 | Safe read-only metadata |
| Select window or pane (navigation only) | ALLOW | TX-A04 | Safe navigation; no mutation |

---

## Required Operating Constraints

1. Never send keystrokes to a session not explicitly specified by the user.
2. Never kill all sessions (`kill-server`).
3. Always show exact keys/commands before sending to any session.
4. Never capture pane output after commands likely to reveal secrets.
5. Always confirm before sending process-interrupting signals (Ctrl+C, Ctrl+D, Ctrl+Z).
6. Always confirm before killing any session.
7. Verify session exists before sending keys (avoid creating unintended sessions).
8. When approving interactive prompts, always show the current pane context first.

---

## Confirmation Workflow

For CONFIRM operations:

1. State action:
   - send keys / kill session / create session / approve prompt
2. State scope:
   - session name, target pane, exact keys/command
3. State risk:
   - wrong session / process interruption / session loss
4. Show current pane context (last few lines) when relevant
5. Ask for confirmation

Example:

> I am about to send `y` + Enter to session `worker-3` to approve a Claude Code prompt. Current pane shows: "Apply changes to src/auth.ts? (y/n)". Confirm?

---

## Output Policy

Allowed:
- session lists and metadata
- pane output for status checking (non-sensitive)
- confirmation of operations

Disallowed:
- pane captures containing passwords, tokens, or secrets
- raw output from secret-bearing commands
- session contents after credential operations

---

## Secret-Bearing Command Indicators (TX-B02 Triggers)

The following are non-exhaustive examples of commands or contexts that trigger TX-B02 (block pane capture):

- Explicit mentions of password entry, credential configuration, or token export
- `aws configure`, `vault login`, `op` (1Password CLI), `gh auth login`
- `docker login`, `npm login`, `ssh-keygen`, `gpg --gen-key`
- Any `export VAR=...` where the variable name suggests a secret (API_KEY, TOKEN, PASSWORD, SECRET, etc.)
- Any command the user describes as involving credentials, authentication, or secrets

When in doubt about whether a session context is sensitive, apply TX-B02 and block the capture.

---

## Domain Notes

tmux provides powerful remote control over terminal sessions. The `send-keys` command can inject arbitrary input including commands and control sequences into any accessible session. This is especially sensitive when sessions run interactive AI tools (Claude Code, Codex) that may auto-execute commands. The `capture-pane` command can exfiltrate any visible terminal content including secrets. This wrapper treats all keystroke injection and sensitive pane capture as high-risk operations requiring user confirmation.

---

## (Trigger, Task, Resources)

**Trigger:** Activate when the user asks to send keystrokes to tmux sessions, capture pane output, create or kill sessions, or interact with running processes (including interactive CLIs like Claude Code) inside tmux.

**Task:** ALLOW read-only operations such as listing sessions, listing windows/panes, capturing non-sensitive pane output from user-specified sessions, and pane/window navigation. CONFIRM keystroke injection to user-specified sessions (showing exact keys), session creation, session killing, destructive key sequences (Ctrl+C/D/Z) when explicitly requested, and interactive prompt approval. BLOCK `kill-server`, pane capture after secret-bearing commands, unsolicited destructive key sequences, and sending commands to sessions the user did not specify.

**Resources:** `references/risk-notes.md`

---

## References

- Original skill: `tmux`
- `references/risk-notes.md`
