# Risk Notes for safe-tmux

## Threat Model Summary

tmux remote-controls terminal sessions by sending keystrokes and capturing pane output. It is used to manage interactive CLIs including Claude Code sessions. It can inject arbitrary input and read arbitrary output from any accessible session.

## Action Space

- **read**: capture pane output, list sessions/windows/panes
- **write**: send keystrokes, create sessions, rename sessions
- **destructive**: kill sessions (`kill-session`), kill server (`kill-server`), send Ctrl+C/Ctrl+D/Ctrl+Z
- **external**: interacts with processes running inside tmux sessions
- **credential**: can capture pane output containing secrets; can send credentials as keystrokes

## Key Risks

### 1. Command Injection via send-keys
`tmux send-keys` can inject arbitrary commands into any session, potentially executing destructive operations in the wrong context.

Mitigation:
- always confirm target session and exact keys
- never send to unspecified sessions

---

### 2. Secret Exfiltration via capture-pane
`tmux capture-pane` reads all visible terminal content, which may include passwords, tokens, or API keys displayed by running processes.

Mitigation:
- block capture after secret-bearing commands
- never return raw pane content from sensitive contexts

---

### 3. Session Destruction
`kill-session` terminates a session and all its processes. `kill-server` destroys all sessions.

Mitigation:
- block `kill-server` entirely
- confirm before any `kill-session`

---

### 4. Process Interruption
Sending Ctrl+C, Ctrl+D, or Ctrl+Z can terminate, EOF, or suspend running processes unexpectedly.

Mitigation:
- only send interrupt signals when explicitly requested
- confirm target session and intent

---

### 5. Wrong-Session Targeting
Sending input to the wrong session could disrupt unrelated work or running processes.

Mitigation:
- require explicit session specification
- verify session exists before operations

---

## Safe vs Unsafe

Safe:
- list sessions/windows/panes
- capture pane output (non-sensitive, user-specified session)
- select window/pane (navigation)

Confirm:
- send keystrokes to session
- kill session
- create session
- send interrupt signals
- approve interactive prompts

Block:
- kill-server
- capture after secret-bearing commands
- unsolicited interrupt signals
- input to unspecified sessions
