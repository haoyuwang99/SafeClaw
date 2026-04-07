---
name: safe-obsidian
description: Safe wrapper for the obsidian skill. Use when working with Obsidian vaults and the obsidian-cli under strict vault-scope, deletion-protection, and configuration-safety constraints. Trigger when the user asks to create, edit, move, delete, or search notes in an Obsidian vault.
---

# Safe Obsidian

This skill adds a safety layer on top of `obsidian`.

Use this skill whenever a task involves:
- Obsidian vaults
- `obsidian-cli`
- creating, editing, moving, or deleting Markdown notes
- searching vault content
- vault configuration or plugin settings

For command syntax and normal product behavior, refer to the original `obsidian` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. accidental deletion of notes or vault data
2. modification of the wrong vault (multi-vault confusion)
3. corruption of `.obsidian/` configuration directory
4. bulk destructive operations without confirmation
5. operating on hardcoded vault paths instead of reading config

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe operation

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Delete multiple notes or bulk-delete operations | BLOCK | OB-B01 | Refuse bulk deletion; require single-target deletion with confirmation |
| Modify `.obsidian/` directory or plugin configuration files | BLOCK | OB-B02 | Refuse direct config modification; changes must be made through Obsidian UI |
| Use hardcoded vault paths instead of reading config or `print-default` | BLOCK | OB-B03 | Refuse hardcoded paths; require dynamic vault resolution |
| Delete a single named note (`obsidian-cli delete`) | CONFIRM | OB-C01 | Confirm note path and vault before deletion |
| Create a new note (`obsidian-cli create`) | CONFIRM | OB-C02 | Confirm vault, path, and content summary before creation |
| Move or rename a note (`obsidian-cli move`) | CONFIRM | OB-C03 | Confirm source, destination, and that wikilinks will be updated |
| Edit note content directly (open and modify `.md` file) | CONFIRM | OB-C04 | Confirm vault, note path, and nature of change |
| Switch default vault (`obsidian-cli set-default`) | CONFIRM | OB-C05 | Confirm new default vault name; warn about scope change |
| Search notes by name (`obsidian-cli search`) | ALLOW | OB-A01 | Allowed; read-only |
| Search note content (`obsidian-cli search-content`) | ALLOW | OB-A02 | Allowed; read-only |
| Print default vault (`obsidian-cli print-default`) | ALLOW | OB-A03 | Allowed; read-only |
| Read vault config to resolve vault path | ALLOW | OB-A04 | Allowed; non-destructive |

---

## Required Operating Constraints

1. Always resolve the active vault from config before operating; never hardcode paths.
2. Never modify `.obsidian/` directory contents directly.
3. Require confirmation for all write, move, and delete operations.
4. Refuse bulk deletions outright; limit deletions to single named notes with confirmation.
5. When multiple vaults exist, explicitly confirm which vault is the target.
6. Prefer `obsidian-cli move` over raw `mv` to preserve wikilink integrity.
7. Treat vault data as personal knowledge base — sensitive by default.

---

## Vault Resolution Policy

Before any operation:
1. Check default vault: `obsidian-cli print-default --path-only`
2. If no default, read `~/Library/Application Support/obsidian/obsidian.json`
3. Use the vault with `"open": true`
4. Never assume a vault path without verification

---

## Confirmation Workflow

For CONFIRM operations:

1. State the target vault name and resolved path.
2. State the operation (create / edit / move / delete).
3. State the exact note path.
4. State risk:
   - data loss (for delete/move)
   - wrong vault (for multi-vault setups)
   - wikilink breakage (for raw moves)
5. Ask for confirmation.

Example:

> I am about to delete the note "Projects/old-draft" from vault "Personal" at `~/Documents/Obsidian/Personal/`. This will permanently remove the note. Confirm?

---

## Output Policy

Allowed:
- "Note created at Projects/new-note.md"
- "Found 5 notes matching 'meeting'."
- "Note moved from old/path to new/path; wikilinks updated."

Disallowed:
- silently deleting notes
- modifying config files
- operating on assumed vault paths without verification

---

## Domain Notes

Obsidian vaults are **personal knowledge bases** stored as plain Markdown files on disk. Users often have multiple vaults (work, personal, research) and rely on wikilinks for cross-referencing. Operating on the wrong vault or breaking link integrity can cause significant knowledge loss.

---

## (Trigger, Task, Resources)

**Trigger:** Activate when the user requests any operation on an Obsidian vault via `obsidian-cli`, including creating, editing, moving, deleting, or searching notes, or changing vault configuration.

**Task:** Evaluate each vault operation against vault-scope, deletion-protection, and configuration-safety rules. BLOCK bulk deletions, direct modification of `.obsidian/` config directory, and use of hardcoded vault paths. CONFIRM single-note deletions, creations, moves, edits, and default-vault changes by presenting the resolved vault, note path, and operation details. ALLOW read-only operations such as searching notes, printing the default vault, and reading vault config for path resolution.

**Resources:** `references/risk-notes.md` — threat model and risk rationale. No auxiliary config or scripts required.

---

## References

- Original skill: `obsidian`
- `references/risk-notes.md`
