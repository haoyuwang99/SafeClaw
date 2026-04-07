---
name: safe-things-mac
description: Safe wrapper for the things-mac skill. Use when managing Things 3 tasks via the things CLI on macOS — adding, updating, searching, or listing todos, projects, and areas. Trigger when the user asks to add a task, list inbox/today, search Things, update or complete a todo, or inspect projects/areas/tags.
---

# Safe Things 3 CLI

This skill adds a safety layer on top of `things-mac`.

Use this skill whenever a task involves:
- `things` CLI
- Things 3 task management
- adding, updating, or completing todos
- listing inbox, today, upcoming, projects, areas, tags
- searching tasks
- Things auth tokens

For command syntax and product behavior, refer to the original `things-mac` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. accidental bulk modification or completion of tasks
2. auth token leakage (THINGS_AUTH_TOKEN)
3. unintended task deletion or cancellation
4. modification of wrong tasks (ID mismatch)
5. unsolicited task creation flooding

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe execution

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Print, log, or return THINGS_AUTH_TOKEN or auth token values — including token metadata (length, prefix, format, hash) and embedding token values in task metadata (titles, notes, tags) | BLOCK | TH-B01 | Never expose auth tokens in output, metadata, or task data (refined r2) |
| Bulk complete, cancel, or modify multiple tasks in one operation (including iterative or automated loops over a large set of tasks) | BLOCK | TH-B02 | Refuse bulk destructive mutations; require one-at-a-time with confirmation |
| Complete or cancel a task (`--completed`, `--canceled`) | CONFIRM | TH-C01 | Show task title and ID; confirm before marking complete/canceled |
| Update an existing task (title, notes, tags, list, heading) | CONFIRM | TH-C02 | Show current task details and proposed changes; confirm |
| Add a new task | CONFIRM | TH-C03 | Show task details (title, notes, list, tags) and confirm before creation |
| Add multiple tasks in rapid succession (>3 per user turn or request) | CONFIRM | TH-C04 | Pause and show summary of all proposed tasks before continuing |
| Use `--dry-run` for any write operation | ALLOW | TH-A01 | Safe preview; does not modify Things |
| List inbox, today, upcoming | ALLOW | TH-A02 | Safe read-only query |
| Search tasks | ALLOW | TH-A03 | Safe read-only query |
| List projects, areas, tags | ALLOW | TH-A04 | Safe read-only query |

---

## Required Operating Constraints

1. Never expose THINGS_AUTH_TOKEN in output — this includes token metadata (length, prefix, format) and embedding token values in task fields. (refined r2)
2. Always prefer `--dry-run` first for write operations to preview before executing.
3. Always confirm before completing or canceling tasks.
4. Always verify task ID matches intended task before update operations.
5. Never bulk-modify tasks without individual confirmation.
6. Show task title alongside ID in all confirmation prompts.
7. Limit task creation to user-requested items only.
8. When a request combines operations with different verdicts, apply the most restrictive: BLOCK > CONFIRM > ALLOW. Refuse the blocked portion and explain; safe portions may proceed if separable. (refined r2)

---

## Confirmation Workflow

For CONFIRM operations:

1. State action:
   - add task / update task / complete task / cancel task
2. State scope:
   - task title, ID, list/project, proposed changes
3. State risk:
   - wrong task modified / irreversible completion / task flood
4. Show `--dry-run` preview when available
5. Ask for confirmation

Example:

> I am about to mark task "Buy milk" (ID: ABC123) as completed. This will move it out of your active lists. Confirm?

---

## Output Policy

Allowed:
- task lists and search results
- task metadata (title, notes, tags, project, area)
- dry-run URL previews
- confirmation of successful operations

Disallowed:
- THINGS_AUTH_TOKEN values
- raw auth tokens passed on command line in output

---

## Domain Notes

Things 3 uses a URL scheme for write operations, making mutations visible in the Things app. The `--completed` and `--canceled` flags are soft-delete operations (no true delete exists in the CLI). However, completing or canceling the wrong task is still disruptive, so all mutations require confirmation. The `--dry-run` flag is a valuable safety tool that previews the URL without executing.

---

## (Trigger, Task, Resources)

**Trigger:** Activate when the user asks to manage Things 3 tasks via the `things` CLI — adding, updating, completing, canceling, listing, or searching todos, projects, areas, or tags.

**Task:** ALLOW read-only operations such as listing inbox/today/upcoming, searching tasks, listing projects/areas/tags, and dry-run previews. CONFIRM individual write operations including adding, updating, completing, or canceling tasks — showing task title, ID, and proposed changes before proceeding. BLOCK bulk destructive mutations (mass complete/cancel/modify) and any exposure of THINGS_AUTH_TOKEN values.

**Resources:** `references/risk-notes.md`

---

## References

- Original skill: `things-mac`
- `references/risk-notes.md`
