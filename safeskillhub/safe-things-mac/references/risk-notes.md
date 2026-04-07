# Risk Notes for safe-things-mac

## Threat Model Summary

things-mac manages Things 3 tasks via the `things` CLI on macOS. It reads from a local SQLite database and writes via the Things URL scheme. Update operations require an auth token.

## Action Space

- **read**: list inbox/today/upcoming, search tasks, list projects/areas/tags
- **write**: add new tasks, update task fields (title, notes, tags, list, heading, dates)
- **destructive**: complete tasks (`--completed`), cancel tasks (`--canceled`) — soft-delete equivalents
- **external**: Things URL scheme (local inter-app communication)
- **credential**: THINGS_AUTH_TOKEN required for update operations

## Key Risks

### 1. Auth Token Leakage
THINGS_AUTH_TOKEN could be exposed in command output or conversation.

Mitigation:
- never print token values
- redact from command previews

---

### 2. Accidental Task Completion/Cancellation
Completing or canceling the wrong task removes it from active views with no easy undo.

Mitigation:
- confirm with task title and ID before any completion/cancellation
- prefer `--dry-run` first

---

### 3. Wrong Task Modification
UUID-based updates could target the wrong task if ID is mismatched.

Mitigation:
- always show task title alongside ID
- confirm changes before execution

---

### 4. Task Creation Flooding
Unsolicited bulk task creation could clutter the user's task management system.

Mitigation:
- confirm each task creation
- pause after 3+ rapid additions

---

### 5. Bulk Destructive Operations
Mass completion or cancellation could wipe active task lists.

Mitigation:
- block bulk mutations
- require individual confirmation

---

## Safe vs Unsafe

Safe:
- list inbox/today/upcoming
- search tasks
- list projects/areas/tags
- dry-run previews

Confirm:
- add task
- update task
- complete/cancel task
- batch task creation

Block:
- auth token exposure
- bulk complete/cancel
