---
name: safe-apple-notes
description: Safe wrapper for the apple-notes skill. Use when managing Apple Notes via the `memo` CLI under controlled installation, scope validation, and bounded state changes. Trigger when the user asks to create, view, edit, delete, search, move, or export notes using the memo CLI.
---

# Safe Apple Notes

This skill adds a safety layer on top of `apple-notes`.

Use this skill whenever a task involves:
- `memo notes` or the `memo` CLI
- creating or editing Apple Notes
- listing, searching, or viewing notes
- deleting notes or note folders
- moving notes between folders
- exporting notes to HTML or Markdown

For command syntax and normal product behavior, refer to the original `apple-notes` skill.

## Safety Goals

1. Prevent irreversible deletion of notes without explicit user confirmation, since the `memo` CLI provides no undo mechanism.
2. Prevent bulk destructive operations (mass delete, mass move, mass export) that could affect large portions of a user's note library in a single unreviewed action.
3. Restrict access to notes in shared or collaborative folders to avoid inadvertently modifying data visible to other users.
4. Verify that the `memo` CLI is installed from the sanctioned Homebrew tap (`antoniorodr/memo`) before any command is executed.
5. Ensure all write and destructive operations are scoped to a single, explicitly identified note or folder at a time, with output summarized to the user before side effects occur.

## Enforcement Model
- `BLOCK`   — refuse outright
- `CONFIRM` — require explicit user approval
- `ALLOW`   — permitted under scope and output constraints

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---|---|---|
| Install `memo` from any source other than `brew install antoniorodr/memo/memo` | BLOCK | AN-B01 | Reject the request; provide the sanctioned install command |
| Delete a single explicitly named note (`memo notes -d`) | CONFIRM | AN-C01 | Display note title and folder; require user to type "yes" before proceeding |
| Delete multiple notes in a single invocation or loop | BLOCK | AN-B02 | Refuse; instruct user to delete one note at a time |
| Edit a note that the user has not explicitly identified by title | CONFIRM | AN-C02 | Display the selected note title and current content summary; require approval before opening editor |
| Edit a note containing images or attachments | BLOCK | AN-B03 | Refuse; surface the `memo` limitation that image/attachment notes cannot be safely edited via CLI |
| Move a single explicitly named note to an explicitly named folder | CONFIRM | AN-C03 | Display source note, source folder, and destination folder; require user approval |
| Move multiple notes in a single invocation or loop | BLOCK | AN-B04 | Refuse; instruct user to move one note at a time |
| Export all notes (`memo notes -ex` with no folder/note filter) | BLOCK | AN-B05 | Refuse; require user to scope export to a specific folder or note |
| Forward, transmit, or exfiltrate note content to any destination outside Notes.app / memo CLI (e.g., email, HTTP endpoint, clipboard for another tool) | BLOCK | AN-B06 | Refuse; note content must remain within the Notes.app / memo CLI scope. Read operations are permitted but results must not be forwarded externally (refined r2) |
| Create, delete, move, or edit multiple notes in a single agent turn via loop, script, or batch operation (including bulk creation) | BLOCK | AN-B07 | Refuse; all write operations (additive and destructive) must target a single note per agent turn (refined r2) |
| Export notes from a single explicitly scoped folder or note | CONFIRM | AN-C04 | Display scope and destination format; require user approval before writing files |
| Access or modify notes in a shared or collaborative folder | CONFIRM | AN-C05 | Warn that changes may affect other collaborators; require explicit user acknowledgment |
| Copy or duplicate note body content from one note into another note | CONFIRM | AN-C06 | Display source note, destination note, and content summary; require user approval before duplicating content (refined r2) |
| Search notes (`memo notes -s "query"`) | ALLOW | AN-A01 | Permitted; results displayed read-only with no side effects |
| List notes (`memo notes`, `memo notes -f "Folder Name"`) | ALLOW | AN-A02 | Permitted; read-only operation with no side effects |
| View a single note | ALLOW | AN-A03 | Permitted; read-only operation with no side effects |
| Create a new note with an explicit title (`memo notes -a "Title"`) | ALLOW | AN-A04 | Permitted; low-risk additive operation |
| Create a new note interactively (`memo notes -a`) | ALLOW | AN-A05 | Permitted; user drives the interactive prompt directly |

## Required Operating Constraints

1. The `memo` CLI must be installed exclusively from the sanctioned Homebrew tap: `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`. Any other source (pip, curl, manual binary) is disallowed.
2. All write operations (create, delete, edit, move) must target a single, explicitly named note per agent turn. Wildcard, glob, or loop-based bulk operations -- whether destructive or additive -- are not permitted in a single agent turn. (refined r2)
3. All write operations (create, edit, move) must be scoped to a folder and note explicitly provided or confirmed by the user; the agent must not infer or guess target folders from context.
4. Before any CONFIRM-verdict operation executes, the agent must display a plain-language summary of the exact change that will occur and wait for the user to respond with an unambiguous approval ("yes").
5. Automation access to Notes.app grants broad read access to all notes including private content; the agent must not surface note content beyond what is directly relevant to the user's stated task.
6. Note content retrieved via read operations (search, view, list) must not be forwarded, transmitted, or exfiltrated to any destination outside the Notes.app / memo CLI boundary, including email, HTTP requests, clipboard injection for other tools, or file writes outside the memo export workflow. (refined r2)

## Confirmation Workflow

1. The agent identifies the operation and looks up its verdict in the Safety Rules table.
2. If verdict is `BLOCK`, the agent refuses with a plain-language explanation and, where applicable, suggests a safer alternative.
3. If verdict is `CONFIRM`, the agent presents a pre-flight summary:
   - Operation type (delete / edit / move / export)
   - Target note title and folder
   - Destination folder (for move/export) or change description (for edit)
   - A warning if the operation is irreversible
4. The agent asks: "Do you want to proceed? Type 'yes' to confirm or 'no' to cancel."
5. The agent proceeds only if the user responds with an unambiguous "yes"; any other response results in cancellation with a status message.

**Example — delete confirmation:**
> You have requested: DELETE note "Q4 Budget Draft" from folder "Work".
> This action is permanent and cannot be undone via the memo CLI.
> Do you want to proceed? Type 'yes' to confirm or 'no' to cancel.

## Output Policy

Allowed:
- Displaying note titles and folder names returned by list or search operations
- Showing a pre-flight summary of a pending write or destructive operation
- Reporting success or failure of a completed operation (e.g., "Note 'Meeting Notes' deleted from 'Work'.")
- Displaying the path and format of exported files after a confirmed export

Disallowed:
- Printing full note body content unless the user explicitly requested to view that specific note
- Logging or retaining note content between turns beyond what is needed to complete the current task
- Surfacing content from notes not targeted by the user's request (e.g., revealing other notes discovered during a search)

## Domain Notes

The `memo` CLI interacts with Apple Notes via macOS Automation (AppleScript/JXA), which grants it broad access to all notes across all folders, including private notes and notes in iCloud-synced shared or collaborative folders. Because there is no native undo for CLI-initiated deletions and edits, irreversibility is the primary risk. The safety wrapper enforces single-note scoping on all write and destructive operations, mandatory confirmation before any state change, and a hard block on bulk destructive patterns. Installation must be validated against the sanctioned Homebrew tap to reduce supply-chain risk from unofficial `memo` binaries.

## (Trigger, Task, Resources)

**Trigger:** Activates whenever the user requests any operation involving Apple Notes through the `memo` CLI, including creating, editing, deleting, moving, searching, listing, or exporting notes.

**Task:** If the operation is a bulk destructive action (mass delete, mass move, unscoped export), an install from an unsanctioned source, or an edit of a note containing images/attachments → BLOCK. If the operation is a single-note delete, edit, move, scoped export, or access to a shared/collaborative folder → CONFIRM with a pre-flight summary showing the target note, folder, and irreversibility warning. If the operation is read-only (search, list, view) or a simple note creation with an explicit title → ALLOW.

**Resources:** `references/risk-notes.md`

## References
- Original skill: `apple-notes`
- `references/risk-notes.md`
- `config/allowlist.yaml`
- `scripts/check.py`
