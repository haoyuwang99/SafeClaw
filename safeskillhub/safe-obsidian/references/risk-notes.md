# Risk Notes for safe-obsidian

## Threat Model Summary

The original `obsidian` skill works with Obsidian vaults (plain Markdown folders on disk) and the `obsidian-cli` tool. It supports creating, searching, moving, deleting, and editing notes. Vaults are local and personal, but operations are file-system-level and can be destructive.

## Main Risk Categories

### 1. Accidental Note Deletion
Risk:
- `obsidian-cli delete` permanently removes a note file from disk.
- No built-in trash or undo mechanism at the CLI level.
- Bulk deletion could wipe significant portions of a knowledge base.

Mitigation:
- Block bulk deletions.
- Require single-target confirmation for each delete.

### 2. Multi-Vault Confusion
Risk:
- Users commonly have multiple vaults (work, personal, iCloud, local).
- Operating on the wrong vault can create, edit, or delete notes in unintended locations.
- Hardcoded paths bypass vault resolution and compound this risk.

Mitigation:
- Always resolve vault from config before operating.
- Block hardcoded vault paths.
- Explicitly confirm target vault when multiple exist.

### 3. Configuration Corruption
Risk:
- `.obsidian/` contains workspace state, plugin configs, themes, and hotkeys.
- Direct modification can break Obsidian startup, plugin behavior, or workspace layout.
- These files are meant to be managed by the Obsidian application, not scripts.

Mitigation:
- Block direct modification of `.obsidian/` directory contents.

### 4. Wikilink Breakage
Risk:
- Moving or renaming notes with raw `mv` instead of `obsidian-cli move` breaks `[[wikilinks]]` across the vault.
- Broken links degrade knowledge base navigability.

Mitigation:
- Prefer `obsidian-cli move` which auto-updates links.
- Confirm move operations and warn about link integrity.

### 5. Unbounded Bulk Operations
Risk:
- Batch create, move, or edit operations without explicit scope can affect many notes.
- Combined with wrong-vault risk, this amplifies potential damage.

Mitigation:
- Require explicit note-by-note scope for destructive operations.
- Confirm each operation individually.

## Safe / Unsafe Examples

### Safe
- Searching notes by name or content
- Printing default vault path
- Reading vault config

### Confirm
- Creating a new note
- Editing note content
- Moving or renaming a note
- Deleting a single named note
- Switching default vault

### Block
- Bulk deletions
- Modifying `.obsidian/` config
- Using hardcoded vault paths

## Evaluation-Oriented Notes

This wrapper targets exact-match policy checks across:
- delete scope (single vs bulk)
- vault resolution method (config-based vs hardcoded)
- config directory protection
- move method (obsidian-cli vs raw mv)
- benign search/read operations that must remain allowed
