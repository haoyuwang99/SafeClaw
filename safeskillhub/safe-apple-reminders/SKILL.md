---
name: safe-apple-reminders
description: Safe wrapper for the apple-reminders skill. Use when managing Apple Reminders via `remindctl` CLI under strict deletion control, bulk-operation safeguards, and iCloud sync awareness.
---

# Safe Apple Reminders

This skill adds a safety layer on top of `apple-reminders`.

Use this skill whenever a task involves:
- remindctl CLI
- listing, adding, or viewing Apple Reminders
- completing or deleting reminders or lists
- creating or removing Reminders lists
- any operation that syncs to iCloud or iOS devices

For command syntax, refer to the original `apple-reminders` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. irreversible deletion of reminders or entire lists without confirmation
2. bulk destructive operations wiping multiple reminders at once
3. unintended changes propagating to all Apple devices via iCloud sync
4. modification of shared or family lists affecting other people's data
5. unauthorized installation of third-party CLI tooling from external taps
6. exfiltration of reminder data to external services, emails, or URLs (refined r2)

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe execution

**Compound Request Escalation (refined r2):** When a single user request contains multiple operations with different verdicts, apply the highest-severity verdict as the controlling verdict. Severity order: BLOCK > CONFIRM > ALLOW. Safe sub-operations (ALLOW) may proceed, but the overall request must not bypass the most restrictive verdict. If any sub-operation is BLOCK, the entire unsafe portion is refused. If any sub-operation is CONFIRM, confirmation is required before any destructive sub-operation executes.

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Delete all reminders across any list (bulk wipe) | BLOCK | AR-B01 | Prevent total data destruction |
| Delete a shared or family list (affects other users' data) | BLOCK | AR-B02 | Prevent cross-user data loss |
| Use `--force` flag without specifying exact reminder IDs | BLOCK | AR-B03 | Prevent unscoped force-delete |
| Exfiltrate, forward, or transmit reminder data to external services, URLs, emails, or any destination outside the local CLI (refined r2) | BLOCK | AR-B04 | Prevent data exfiltration of reminder contents |
| Delete a list (`remindctl list <name> --delete`) | CONFIRM | AR-C01 | Confirm list name and destruction of all contained reminders |
| Delete specific reminder(s) (`remindctl delete <id> ...`) | CONFIRM | AR-C02 | Confirm each ID and reminder title before deletion |
| Complete multiple reminders in one command (`remindctl complete <id> <id> ...`) | CONFIRM | AR-C03 | Confirm bulk-complete scope and iCloud sync impact |
| Create a new list (`remindctl list <name> --create`) | CONFIRM | AR-C04 | Confirm list name before creation |
| Install remindctl CLI (`brew install steipete/tap/remindctl`) | CONFIRM | AR-C05 | Confirm third-party tap installation |
| Grant Reminders app permission (`remindctl authorize`) | CONFIRM | AR-C06 | Confirm OS permission grant |
| View reminders (remindctl, today, tomorrow, week, overdue, all) | ALLOW | AR-A01 | Safe read operation |
| List all Reminders lists (`remindctl list`) | ALLOW | AR-A02 | Safe read operation |
| View reminders in a specific list (`remindctl list <name>`) | ALLOW | AR-A03 | Safe read operation |
| Add one or more reminders (`remindctl add ...`) (refined r2) | ALLOW | AR-A04 | Safe write; non-destructive |
| Check CLI status (`remindctl status`) | ALLOW | AR-A05 | Safe read operation |
| Complete a single reminder (`remindctl complete <id>`) | ALLOW | AR-A06 | Safe single-item state change |

---

## Required Operating Constraints

1. Never use `--force` without a set of explicit, individually verified reminder IDs.
2. Always confirm before deleting any reminder or list; show the reminder title or list name.
3. Before deleting a list, state the number of reminders it contains that will be permanently lost.
4. Block all operations targeting shared or family lists that are owned by another user.
5. Treat any delete or complete operation affecting more than one reminder as a bulk operation requiring confirmation.
6. Remind the user that all mutations sync to iCloud and will appear on all linked Apple devices.
7. Never auto-install remindctl or grant OS permissions without explicit user approval.
8. Evaluate all commands by their decoded/resolved intent, not their surface representation. Obfuscated, encoded (e.g., base64), spaced-out, or indirectly phrased commands must be interpreted and matched against safety rules by their effective operation. (refined r2)
9. Never forward, copy, email, upload, or otherwise transmit reminder data to external services, URLs, APIs, or email addresses. Reminder data must stay within the local CLI and user's terminal session. (refined r2)

---

## Confirmation Workflow

For CONFIRM operations:

1. State the action (delete reminder / delete list / bulk complete / create list / install / authorize)
2. State the target:
   - reminder title(s) and ID(s), or
   - list name (and reminder count if deleting)
3. State the impact:
   - irreversibility (deletions cannot be undone)
   - iCloud sync (change will propagate to all Apple devices)
4. Show a summary preview (titles, IDs, list contents count)
5. Ask for confirmation

Example:

> I am about to delete reminder "Pick up prescription" (ID: 4A83) from list "Personal". This is irreversible and will sync to all your Apple devices. Confirm?

---

## Output Policy

Allowed:
- reminder titles, due dates, list names, and IDs
- status and authorization state
- filtered views by date range or list

Disallowed:
- silent deletions or completions
- force-deleting without displaying what will be removed
- bulk destructive operations without per-item confirmation
- exfiltrating, forwarding, or transmitting reminder data (titles, IDs, due dates, notes) to any external service, URL, email address, API, or destination outside the local terminal session (refined r2)

---

## Domain Notes

This skill interacts with **Apple Reminders via iCloud sync**.

Key considerations:
- deletions are permanent; Apple Reminders does not have a trash or undo mechanism via CLI
- every mutation (add, complete, delete) propagates in real time to all devices signed into the same Apple ID (iPhone, iPad, Apple Watch, Mac)
- shared and family lists are owned by specific Apple ID holders; modifying them affects other people's reminders
- remindctl is a third-party brew tap (`steipete/tap`), not an Apple-provided tool; installation carries supply-chain trust considerations

Therefore:
- strict human-in-the-loop control for all delete, bulk-complete, and list-management operations

---

## (Trigger, Task, Resources)

**Trigger:** Activates whenever the user requests any operation involving Apple Reminders through the `remindctl` CLI, including listing, adding, completing, deleting reminders or lists, or managing iCloud-synced reminder data.

**Task:** If the operation is a bulk wipe of all reminders, deletion of a shared/family list, or use of `--force` without explicit reminder IDs → BLOCK. If the operation deletes a list or specific reminders, bulk-completes multiple reminders, creates a new list, installs `remindctl`, or grants OS permissions → CONFIRM with a summary showing target names/IDs, irreversibility notice, and iCloud sync impact. If the operation is read-only (view, list, status) or adds a single reminder → ALLOW.

**Resources:** `references/risk-notes.md`

## References

- Original skill: `apple-reminders`
- `references/risk-notes.md`
