---
name: safe-gifgrep
description: Safe wrapper for the gifgrep skill. Use when searching GIF providers (Tenor/Giphy), downloading GIFs, extracting stills/sheets, or browsing GIF results under strict API key protection, download control, and content safety constraints.
---

# Safe GifGrep

This skill adds a safety layer on top of `gifgrep`.

Use this skill whenever a task involves:
- gifgrep
- searching GIFs on Tenor or Giphy
- downloading GIF files
- extracting stills or contact sheets from GIFs
- browsing GIF results in TUI

For command syntax, refer to the original `gifgrep` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. API key leakage (GIPHY_API_KEY, TENOR_API_KEY)
2. uncontrolled bulk downloads consuming disk space
3. downloading inappropriate or unexpected content at scale
4. exposure of API credentials in command output or logs
5. excessive API requests incurring rate limits or costs

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe execution

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Display, log, or partially reveal API keys (`GIPHY_API_KEY`, `TENOR_API_KEY`) — including substrings, encoded forms, or obfuscated references | BLOCK | GG-B01 | Never expose credentials in any form (refined r2) |
| Download more than 10 GIFs in a single command (`--download --max >10`) or cumulatively across batched commands in a session | BLOCK | GG-B02 | Prevent uncontrolled bulk download (refined) |
| Pipe GIF URLs to external commands or services — including multi-step exfiltration via intermediate files, webhooks, or encoded destinations | BLOCK | GG-B03 | Prevent data exfiltration, including indirect/staged methods (refined r2) |
| Batched download commands whose cumulative total exceeds 10 GIFs in a single session | BLOCK | GG-B05 | Prevent cap circumvention via splitting (refined) |
| Download GIFs (`--download`) with max ≤ 10 | CONFIRM | GG-C01 | Confirm disk write and count |
| Bulk search with `--max` > 20 | CONFIRM | GG-C02 | Confirm scope and API usage |
| Use `--reveal` to open Finder | CONFIRM | GG-C03 | Confirm system interaction |
| Extract still or sheet from local file (`gifgrep still`, `gifgrep sheet`) | CONFIRM | GG-C04 | Confirm output path and overwrite |
| Basic search returning URLs or metadata (`gifgrep <query>`, `--format url`, `--json`) | ALLOW | GG-A01 | Safe read-only query |
| TUI browsing (`gifgrep tui`) | ALLOW | GG-A02 | Safe interactive preview |
| Search with `--max` ≤ 20 (no download) | ALLOW | GG-A03 | Safe bounded query |
| Preview with `--thumbs` | ALLOW | GG-A04 | Safe local rendering |

---

## Compound Request Resolution (refined r2)

When a request contains multiple operations, evaluate each sub-operation independently and apply the **most restrictive** verdict: BLOCK > CONFIRM > ALLOW. A safe sub-operation does not neutralize an unsafe one.

---

## Required Operating Constraints

1. Never expose API keys — fully or partially — in output, logs, or command echoes.
2. Always confirm before writing files to disk (downloads, stills, sheets).
3. Cap bulk downloads at 10 per invocation; block requests exceeding this.
4. Confirm large search result sets (>20) to prevent excessive API usage.
5. Never pipe GIF URLs or content to external services without explicit approval.
6. Verify output path before overwriting existing files during still/sheet extraction.

---

## Confirmation Workflow

For CONFIRM operations:

1. State action (download / extract / bulk search)
2. State scope:
   - number of results or files
   - output directory or path
3. State risk:
   - disk space usage
   - API quota consumption
   - file overwrite
4. Ask for confirmation

Example:

> I am about to download 5 GIFs matching "cats" to ~/Downloads. This will write files to disk. Confirm?

---

## Output Policy

Allowed:
- search result metadata (titles, URLs, tags)
- thumbnail previews
- summary counts

Disallowed:
- API keys or tokens
- bulk URL dumps piped to external tools
- unconfirmed file writes

---

## Domain Notes

gifgrep is a **GIF search and download tool** that interacts with external APIs (Tenor, Giphy).

Key considerations:
- every search request hits an external API
- downloads write to local disk
- API keys may be present in environment variables

Therefore:
- credential protection and download control are primary concerns

---

## (Trigger, Task, Resources)

**Trigger:** Activates whenever a task involves searching GIF providers (Tenor/Giphy), downloading GIF files, extracting stills or contact sheets, or browsing GIF results via `gifgrep` — any operation that could expose API credentials, write files to disk, or send data to external services.

**Task:** If the operation would expose API keys (`GIPHY_API_KEY`, `TENOR_API_KEY`) or pipe GIF URLs to external commands or download more than 10 GIFs in a single command → BLOCK. If the operation writes files to disk (downloads with ≤10, still/sheet extraction), performs bulk searches with `--max` > 20, or opens Finder via `--reveal` → CONFIRM with a preview of the action scope, file count, and output path. Otherwise (read-only searches with ≤20 results, TUI browsing, thumbnail previews) → ALLOW.

**Resources:** `references/risk-notes.md` — threat model and risk rationale. No auxiliary config or scripts required.

---

## References

- Original skill: `gifgrep`
- `references/risk-notes.md`
