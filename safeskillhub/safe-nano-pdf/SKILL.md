---
name: safe-nano-pdf
description: Safe wrapper for the nano-pdf skill. Use when editing PDFs via the nano-pdf CLI under strict file-scope, content-safety, and overwrite-protection constraints. Trigger when the user asks to edit, modify, or transform a PDF using nano-pdf.
---

# Safe nano-pdf

This skill adds a safety layer on top of `nano-pdf`.

Use this skill whenever a task involves:
- `nano-pdf`
- PDF editing
- natural-language PDF modifications
- page-level content changes in PDF files

For command syntax and normal product behavior, refer to the original `nano-pdf` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. overwriting original PDF files without backup or confirmation
2. editing the wrong file or page due to ambiguous instructions
3. injecting inappropriate or harmful content into PDFs
4. operating on sensitive or confidential documents without awareness
5. unbounded batch edits across many pages or files

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe operation

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Edit instruction that injects malicious content (scripts, phishing links, deceptive legal text) | BLOCK | NP-B01 | Refuse content that could deceive or harm document recipients |
| Edit that overwrites the original file without backup | BLOCK | NP-B02 | Require output to a new file or explicit backup before in-place edit |
| Batch edit across all pages or multiple PDFs without explicit scope | BLOCK | NP-B03 | Refuse unbounded bulk operations; require explicit page/file list |
| Edit a single specified page in a named PDF | CONFIRM | NP-C01 | Confirm target file, page number, and intended change before execution |
| Edit instruction is vague or ambiguous (e.g., "fix it", "make it better") | CONFIRM | NP-C02 | Ask user to clarify the exact change before proceeding |
| Edit a PDF flagged as sensitive (contracts, legal, financial, medical) | CONFIRM | NP-C03 | Warn about sensitivity; confirm intent and scope |
| Read or preview PDF content without modification | ALLOW | NP-A01 | Allowed; non-destructive |
| Sanity-check or diff output PDF against original | ALLOW | NP-A02 | Allowed; encouraged |

---

## Required Operating Constraints

1. Never overwrite the source PDF in-place without explicit user approval.
2. Always confirm target file path and page number before editing.
3. Reject edit instructions that could produce deceptive or harmful document content.
4. Limit edits to explicitly specified pages; never silently apply to all pages.
5. Encourage sanity-checking the output PDF before sharing or sending.
6. Treat contracts, legal, financial, and medical PDFs as sensitive by default.

---

## Confirmation Workflow

For CONFIRM operations:

1. State the target PDF file and page number.
2. State the intended edit in plain language.
3. State risk:
   - original file overwrite
   - wrong page/file
   - sensitive document modification
4. State constraints:
   - output to new file unless confirmed otherwise
   - single-page scope
5. Ask for confirmation.

Example:

> I am about to edit page 1 of `deck.pdf` to change the title to "Q3 Results". The output will be saved to `deck_edited.pdf` to preserve the original. Confirm?

---

## Output Policy

Allowed:
- "PDF edited successfully. Output saved to `deck_edited.pdf`."
- "Page 3 updated with new subtitle text."

Disallowed:
- silently overwriting the original file
- applying edits without stating what changed
- dumping raw PDF binary content

---

## Domain Notes

`nano-pdf` applies natural-language edits to PDF pages, making it easy to introduce unintended changes. PDFs are often shared externally (presentations, contracts, reports), so edits must be precise, confirmed, and reversible.

---

## (Trigger, Task, Resources)

**Trigger:** Activate when the user requests any PDF editing, modification, or transformation operation via `nano-pdf`, including page-level content changes and natural-language PDF modifications.

**Task:** Evaluate each nano-pdf operation against file-scope, content-safety, and overwrite-protection rules. BLOCK operations that inject malicious content, overwrite originals without backup, or perform unbounded batch edits. CONFIRM single-page edits, vague instructions, and edits to sensitive documents (contracts, legal, financial, medical) by presenting the target file, page, and intended change. ALLOW read-only operations such as previewing PDF content or diffing output against the original.

**Resources:** `references/risk-notes.md` — threat model and risk rationale. No auxiliary config or scripts required.

---

## References

- Original skill: `nano-pdf`
- `references/risk-notes.md`
