---
name: safe-model-usage
description: Safe wrapper for the model-usage skill. Use when summarizing per-model usage and cost data via CodexBar CLI, parsing cost JSON, or displaying cost breakdowns. Trigger when the user asks about model costs, usage summaries, codexbar cost, or cost breakdowns by model.
---

# Safe Model Usage

This skill adds a safety layer on top of `model-usage`.

Use this skill whenever a task involves:
- `codexbar cost`
- Model usage or cost summaries
- Parsing cost JSON data
- Per-model cost breakdowns
- Reading cost data from files or stdin

For command syntax and product behavior, refer to the original `model-usage` skill and CodexBar documentation.

## Safety Goals

This wrapper is designed to prevent:
1. Arbitrary file reads beyond cost data files
2. Exposure of sensitive business spending information to unintended destinations
3. Manipulation of the Python parsing script to execute arbitrary code
4. Unbounded or recursive file system traversal via the --input flag
5. Unintended disclosure of usage patterns that reveal organizational activity

## Enforcement Model

Actions are classified into three levels:

- `BLOCK`   — refuse outright
- `CONFIRM` — require explicit user approval with a risk summary
- `ALLOW`   — permitted under standard operating constraints

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| `codexbar cost --format json` for the current model | ALLOW | MU-A01 | Permitted; standard read-only cost query |
| `codexbar cost --format json --all` for all models | ALLOW | MU-A02 | Permitted; read-only cost query across models |
| Parse cost JSON from stdout and display text summary | ALLOW | MU-A03 | Permitted; local data transformation only |
| Parse cost JSON from stdout and output as JSON | ALLOW | MU-A04 | Permitted; local data transformation only |
| Read cost JSON from a file via --input with a path under the current working directory | ALLOW | MU-A05 | Permitted if path is under cwd and has .json extension |
| Read cost JSON from stdin | ALLOW | MU-A06 | Permitted; no file system access involved |
| Read from a file via --input with a path outside the current working directory | CONFIRM | MU-C01 | Show the absolute resolved path and ask for confirmation before reading |
| Read from a file via --input targeting sensitive paths (~/.config, ~/.ssh, ~/.aws, /etc, ~/.env*) | BLOCK | MU-B01 | Refuse; the --input flag must not be used to read sensitive configuration or credential files |
| Read from a file via --input using path traversal (../) to escape intended directory | BLOCK | MU-B02 | Refuse; resolve the path and reject if it escapes the working directory without explicit confirmation via MU-C01 |
| Pipe or redirect cost output to an external URL, API endpoint, or network destination | BLOCK | MU-B03 | Refuse; cost data must remain local |
| Modify, overwrite, or replace the Python parsing script | BLOCK | MU-B04 | Refuse; the parsing script must not be altered during operation |
| Execute arbitrary commands through the --input flag or script arguments | BLOCK | MU-B05 | Refuse; only valid file paths and recognized flags are permitted |
| Glob or wildcard expansion in --input to read multiple files at once | CONFIRM | MU-C02 | Show the expanded file list and ask for confirmation before processing |
| Display cost data that includes account identifiers or billing IDs | CONFIRM | MU-C03 | Warn that output may contain identifiable billing information; ask for confirmation |
| Read from --input with a non-.json file extension under cwd (e.g., .csv, .jsonl, .txt) | CONFIRM | MU-C04 | MU-A05 only auto-allows .json; show the file path and extension and ask for confirmation before reading (refined r2) |
| Write cost output to a file outside the current working directory (non-sensitive path) | CONFIRM | MU-C05 | Show the resolved output path and ask for confirmation; sensitive paths are blocked by MU-B07 (refined r2) |
| Pass unrecognized or unknown flags to the codexbar CLI | BLOCK | MU-B06 | Refuse; only recognized flags (--format json, --all, --input) are permitted per Operating Constraint 2 (refined r2) |
| Write, append, or redirect output to sensitive system paths (~/.config, ~/.ssh, ~/.aws, /etc, ~/.env*, /var/log) | BLOCK | MU-B07 | Refuse; sensitive paths must not be written to, mirroring the read protection of MU-B01 (refined r2) |
| Perform destructive file operations (delete, rename, move) on any files | BLOCK | MU-B08 | Refuse; this skill only covers reading and displaying cost data; destructive file operations are outside scope (refined r2) |

## Required Operating Constraints

1. Only invoke `codexbar cost` with `--format json` and optionally `--all`.
2. Only pass recognized flags (`--format json`, `--all`, `--input`) to the codexbar CLI; reject unknown flags with a BLOCK verdict per MU-B06. (refined r2)
3. Resolve all --input file paths to absolute paths before access; reject paths that resolve to sensitive directories.
4. Never modify the Python parsing script at runtime.
5. Never send cost output to external services, URLs, or network destinations.
6. Prefer summarized output over raw JSON when presenting to the user.
7. If the user requests output to a file, write only to the current working directory. Writing to paths outside cwd requires CONFIRM (MU-C05); writing to sensitive paths is blocked (MU-B07). (refined r2)
8. Never perform destructive file operations (delete, rename, move) on any files; these are outside skill scope per MU-B08. (refined r2)
9. For --input files under cwd, only .json extension is auto-allowed (MU-A05); other extensions require confirmation per MU-C04. (refined r2)

## Confirmation Workflow

For any `CONFIRM` operation, follow this exact flow:

1. State the intended operation in one sentence.
2. State the exact scope:
   - file path (resolved absolute path)
   - models included (current or all)
   - output format (text or JSON)
3. State the main risk:
   - reading outside working directory
   - exposing billing identifiers
   - processing multiple files
4. Ask for explicit confirmation.

Example confirmation text:

> I am about to read cost data from `/Users/alice/other-project/costs.json`, which is outside the current working directory. The file will be parsed for model cost breakdowns and displayed as a text summary. Confirm?

## Output Policy

When responding to the user:
- Summarize cost data in tabular or bullet form by default
- Do not include raw account IDs or billing identifiers unless the user explicitly requests them
- If outputting JSON, ensure it contains only cost/model fields, not metadata with account details
- Redact or omit any fields that appear to contain API keys, tokens, or credentials

Allowed examples:
- "Model gpt-4 cost $12.34 over 1,200 requests this period."
- "Total spend across all models: $45.67."
- JSON with model name, request count, and cost fields only.

Disallowed examples:
- Raw account IDs or billing identifiers without user request
- API keys or tokens found in cost data
- Cost data piped to an external service

## (Trigger, Task, Resources)

**Trigger:** Activates whenever the user requests model usage or cost data via the `codexbar cost` CLI, including querying per-model costs, parsing cost JSON from files or stdin, or displaying cost breakdowns.

**Task:** If the `--input` flag targets sensitive paths (~/.config, ~/.ssh, ~/.aws, /etc, ~/.env*), uses path traversal to escape the working directory, if cost data would be piped to an external network destination, if the parsing script would be modified, if arbitrary commands are injected through flags, if unrecognized CLI flags are used (MU-B06), if output is written/appended to sensitive system paths (MU-B07), or if destructive file operations (delete, rename, move) are requested (MU-B08) → BLOCK. If `--input` references a file outside the current working directory, uses glob/wildcard expansion, if output contains account/billing identifiers, if --input targets a non-.json file under cwd (MU-C04), or if cost output is written to a non-sensitive path outside cwd (MU-C05) → CONFIRM with resolved path and risk disclosure. If the operation is a standard `codexbar cost` query with recognized flags, parses cost JSON from stdout or a local .json file under cwd, or reads from stdin → ALLOW.

**Resources:** `references/risk-notes.md` — threat model and risk rationale from Phase 1 analysis. No auxiliary config or scripts required.

## References

- Original skill: `model-usage`
- `references/risk-notes.md`
