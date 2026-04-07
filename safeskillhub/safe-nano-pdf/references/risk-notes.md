# Risk Notes for safe-nano-pdf

## Threat Model Summary

The original `nano-pdf` skill wraps a CLI tool that edits PDF files using natural-language instructions. It operates on local files and does not require credentials or network access, but it modifies documents that are often shared externally.

## Main Risk Categories

### 1. Irreversible File Overwrite
Risk:
- Editing may overwrite the original PDF, destroying the only copy.
- Users may not realize the edit is in-place.

Mitigation:
- Block in-place overwrites without backup.
- Default to writing output to a new file.

### 2. Wrong Target (File or Page)
Risk:
- Page numbering ambiguity (0-based vs 1-based) can cause edits on the wrong page.
- Vague file references could match the wrong PDF.

Mitigation:
- Always confirm exact file path and page number.
- Require explicit specification, not guesses.

### 3. Malicious Content Injection
Risk:
- Natural-language instructions could inject phishing links, deceptive legal clauses, fake signatures, or scripts into a PDF.
- Edited PDFs may be shared with third parties who trust the content.

Mitigation:
- Block instructions that produce deceptive or harmful content.
- Review edit intent before execution.

### 4. Sensitive Document Modification
Risk:
- Contracts, legal documents, financial reports, and medical records require extra care.
- Unintended edits could have legal or compliance consequences.

Mitigation:
- Flag sensitive document types for confirmation.
- Warn user about implications of editing such files.

### 5. Unbounded Batch Edits
Risk:
- Applying the same instruction to all pages or multiple files without explicit scope can cause widespread unintended changes.

Mitigation:
- Block batch operations without explicit page/file list.
- Require per-page or per-file confirmation for bulk edits.

## Safe / Unsafe Examples

### Safe
- Reading or previewing a PDF
- Editing a single confirmed page with a clear instruction
- Diffing output against original

### Confirm
- Editing a specific page in a named file
- Vague edit instructions needing clarification
- Editing sensitive documents

### Block
- Overwriting original without backup
- Injecting deceptive content
- Unbounded batch edits across all pages/files

## Evaluation-Oriented Notes

This wrapper targets exact-match policy checks across:
- direct malicious content injection attempts
- ambiguous edit instructions that need clarification
- batch vs single-page scope boundaries
- benign read/preview operations that must remain allowed
