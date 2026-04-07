# Risk Notes for safe-apple-notes

## Threat Model Summary

The `apple-notes` skill uses the `memo` CLI (installed via Homebrew from `antoniorodr/memo`) to manage Apple Notes on macOS. The CLI communicates with Notes.app via macOS Automation (AppleScript/JXA). Commands include: listing notes (`memo notes`), searching notes (`memo notes -s`), creating notes (`memo notes -a`), editing notes (`memo notes -e`), deleting notes (`memo notes -d`), moving notes between folders (`memo notes -m`), and exporting notes to HTML or Markdown (`memo notes -ex`). Because Automation access is granted at the application level, the CLI can read and modify all notes across all folders, including private notes, iCloud-synced notes, and notes in shared or collaborative folders. There is no built-in undo for any write or destructive operation performed through the CLI.

## Main Risk Categories

### 1. Irreversibility
Risk:
- Deleting a note via `memo notes -d` is permanent; the macOS Notes trash may or may not capture CLI-initiated deletions, and the `memo` CLI provides no undo command.
- Editing a note via `memo notes -e` opens an interactive editor; saving overwrites the existing content with no versioning or rollback available through the CLI.

Mitigation:
- Require explicit CONFIRM for every single-note delete and every edit where the note was not explicitly identified by the user before the operation began.
- Display note title, folder, and a permanence warning in the pre-flight summary for all delete operations.
- Block any attempt to delete or overwrite multiple notes in a single agent turn.

### 2. Scope Explosion
Risk:
- Bulk operations (delete all, move all, export all) can affect hundreds of notes across the entire Notes library in a single command or scripted loop.
- An agent acting on an ambiguous instruction (e.g., "clean up my notes") could interpret it as a mass delete without scoping guardrails.
- Exporting all notes without a folder/note filter can write large volumes of data to disk, potentially including sensitive content.

Mitigation:
- Block any delete or move operation that targets more than one note in a single invocation.
- Block any export that lacks an explicit folder or note scope.
- Require explicit CONFIRM with destination details before any scoped export proceeds.
- Never infer a broad scope from an ambiguous user instruction; ask for clarification instead.

### 3. External Interaction (Automation Access)
Risk:
- Granting Automation access to Notes.app allows the `memo` CLI to read and write all notes, including private notes the user may not intend to expose.
- A compromised or misconfigured CLI could silently exfiltrate note content during a read operation.
- Interactive prompts from `memo` may require terminal access and can behave unpredictably in non-interactive agent environments.

Mitigation:
- Surface note content only for the specific note the user explicitly requested to view; do not log or retain content beyond the current task.
- Validate that the `memo` binary originates from the sanctioned Homebrew tap before any command is run.
- Warn users before the first use that Automation access is broad and applies to all notes in Notes.app.

### 4. Privilege Escalation (Shared/Collaborative Folders)
Risk:
- Notes.app supports shared folders where multiple iCloud users collaborate. CLI edits, moves, or deletes in a shared folder propagate to all collaborators immediately.
- An agent unaware of folder sharing status could modify or delete content that other users depend on.
- There is no CLI-level indicator of whether a folder is shared; the agent cannot detect this automatically without inspecting folder metadata.

Mitigation:
- Flag any operation targeting a folder that is known or suspected to be shared with a CONFIRM verdict and an explicit warning that changes will affect other collaborators.
- Instruct the user to verify sharing status in Notes.app before authorizing write or destructive operations on any folder.
- Never move notes into a shared folder without explicit user confirmation that this is intended.

### 5. Supply-Chain (Third-Party CLI Installation)
Risk:
- The `memo` CLI is a third-party tool published by an individual maintainer (`antoniorodr`). Installing from an unofficial source (pip, curl, unsigned binary) could introduce a malicious binary with full Automation access to Notes.app.
- Brew formula updates could introduce breaking changes or malicious code if the tap is compromised.
- Users may already have a binary named `memo` on their PATH from an unrelated tool.

Mitigation:
- Block any installation command that does not use the exact sanctioned Homebrew tap: `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`.
- Before the first command execution, verify that the `memo` binary on PATH matches the expected Homebrew Cellar path (e.g., output of `which memo` should resolve to a Homebrew-managed path).
- Advise users to review the Homebrew formula and recent tap commits before installation on sensitive machines.

## Safe / Unsafe Examples

### Safe
- `memo notes` — list all notes, read-only, no side effects.
- `memo notes -f "Personal"` — list notes in a specific folder, read-only.
- `memo notes -s "project plan"` — search notes by keyword, read-only.
- `memo notes -a "Meeting Agenda"` — create a new note with an explicit title, additive and low-risk.
- Viewing a single explicitly requested note — read-only, no state change.

### Confirm
- `memo notes -d` targeting a single explicitly named note — irreversible; requires pre-flight summary and "yes" confirmation.
- `memo notes -e` on a note explicitly identified by the user — overwrites content; requires pre-flight summary showing note title and folder.
- `memo notes -m` moving a single note to an explicitly named destination folder — requires pre-flight summary showing source and destination.
- `memo notes -ex` scoped to a single explicitly named folder — exports data to disk; requires pre-flight summary showing scope and format.
- Any operation targeting a folder suspected to be shared — requires warning and explicit acknowledgment from the user.

### Block
- Any install of `memo` from a source other than `brew install antoniorodr/memo/memo`.
- Deleting multiple notes in a single agent turn (loop or bulk flag).
- Moving multiple notes in a single agent turn.
- `memo notes -ex` with no folder or note scope (export everything).
- Editing a note that contains images or attachments (unsupported by `memo`; risk of data corruption).
- Any command that would write to or delete from more than one note without separate per-note confirmations.

## Evaluation-Oriented Notes

The safety wrapper checks for the following before any command is executed:
- **Installation provenance**: Is the `memo` binary on PATH installed from the sanctioned Homebrew tap? Reject if not.
- **Operation cardinality**: Does the operation target exactly one note and/or one folder? Block if multiple targets are detected.
- **Export scope**: Is the export scoped to a specific folder or note, not the entire library? Block if unscoped.
- **Shared folder indicator**: Has the user mentioned or does context suggest the target folder is shared? Escalate to CONFIRM with a collaborator-impact warning.
- **Attachment presence**: Is the target note known to contain images or attachments? Block edit attempts on such notes.
- **Confirmation token**: For CONFIRM-verdict operations, did the user respond with an unambiguous "yes" to the pre-flight summary? Do not proceed until this is satisfied.
- **Content leakage**: Is the output limited to what the user explicitly requested, without surfacing unrelated note content from search results or folder listings?
