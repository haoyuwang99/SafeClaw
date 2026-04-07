# Risk Notes for safe-apple-reminders

## Threat Model Summary

```
Skill: apple-reminders
Actions:
  - read: list reminders/lists, view by date filter (today/tomorrow/week/overdue/all), check status
  - write: add reminders, create lists
  - destructive: delete reminders (--force), delete lists, complete reminders
  - external: all mutations sync to iCloud and propagate to all linked Apple devices
  - credential: macOS Reminders permission grant via remindctl authorize
Risks:
  - Irreversibility: deleted reminders cannot be recovered via CLI; no undo or trash mechanism
  - Scope explosion: completing/deleting multiple IDs in one command; deleting a list destroys all its reminders
  - External interaction: iCloud sync means every change appears on iPhone, iPad, Apple Watch in real time
  - Privilege escalation: shared/family lists are owned by other Apple ID holders; mutations affect other users
  - Supply-chain: remindctl is a third-party CLI from a personal brew tap, not Apple-provided
```

## Key Risks

### 1. Irreversible Deletion

`remindctl delete <id> --force` permanently removes reminders. Unlike most file systems or databases, Apple Reminders (via CLI) provides no recycle bin or undo pathway. Deleting an entire list with `remindctl list <name> --delete` destroys every reminder inside it simultaneously.

Mitigation:
- confirm every delete operation with reminder title and ID displayed
- block `--force` when no explicit ID list is provided
- state item count before deleting a list

---

### 2. Bulk Destructive Operations

`remindctl complete 1 2 3` and `remindctl delete 4A83 5B12 6C99` accept multiple targets in one invocation. A mistyped or AI-generated list of IDs can wipe or finalize reminders the user did not intend.

Mitigation:
- treat any multi-ID complete or delete as a bulk operation requiring confirmation
- display each target title before executing
- block unscoped force-delete (no explicit IDs)

---

### 3. iCloud Sync Propagation

Apple Reminders is backed by iCloud. Every mutation — add, complete, delete — syncs within seconds to all devices on the same Apple ID. An inadvertent deletion that goes unnoticed on the Mac will already be gone from the user's iPhone before they can intervene.

Mitigation:
- include iCloud sync impact statement in every CONFIRM prompt
- never perform silent mutations

---

### 4. Shared and Family List Exposure

Reminders supports shared lists where multiple Apple ID holders collaborate. Deleting or bulk-completing items on a shared list affects all participants. Family Sharing lists may be owned by another household member.

Mitigation:
- block deletion of shared or family lists outright
- surface list ownership information when available before any write operation

---

### 5. Third-Party CLI Supply-Chain

remindctl is distributed via `steipete/tap`, a personal Homebrew tap. It is not an Apple-provided utility. Installation pulls from an external author's repository, and future tap updates could introduce changes without Apple's validation.

Mitigation:
- confirm before running `brew install steipete/tap/remindctl`
- confirm before running `remindctl authorize` (grants OS-level Reminders permission)

---

## Safe vs Unsafe

Safe:
- view reminders by date (today, tomorrow, week, overdue, all)
- list all Reminders lists
- view reminders in a specific list
- add a single reminder
- check remindctl status
- complete a single reminder

Confirm:
- delete specific reminder(s)
- delete a list
- complete multiple reminders at once
- create a new list
- install remindctl
- authorize Reminders permission

Block:
- bulk delete all reminders across any list
- delete shared or family lists
- force-delete without specifying exact IDs
