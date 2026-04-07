---
name: safe-skill-logger
description: Safe wrapper for the skill-logger meta-skill. Use when logging skill activations under strict constraints preventing sensitive data leakage into logs, log injection attacks, path traversal, and disk exhaustion. Always active alongside skill-logger.
---

# Safe Skill Logger

This skill adds a safety layer on top of `skill-logger`.

Use this skill whenever a task involves:
- logging skill activation events
- appending entries to the skills log file
- reading or reviewing skill activation logs

For log format and activation workflow, refer to the original `skill-logger` skill.

## Safety Goals

This wrapper is designed to prevent:
1. sensitive data leakage into log entries (passwords, tokens, personal content)
2. log injection attacks via crafted task descriptions
3. log file path traversal or writing to unauthorized locations
4. disk exhaustion through unbounded log growth
5. exposure of log contents to unauthorized parties

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe execution

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Log entries containing secrets, tokens, passwords, or PII | BLOCK | SL-B01 | Refuse; sanitize and relog without sensitive content |
| Writing log entries to any path other than the designated log file | BLOCK | SL-B02 | Refuse; logs must only go to the authorized path |
| Task descriptions containing shell metacharacters, injection patterns (`;`, `&&`, `$(`, backticks), or encoded control characters (`%0A`, `%0D`, `\n`, `\r`, percent-encoded sequences) (refined r2) | BLOCK | SL-B03 | Refuse; sanitize input before logging |
| Sharing, sending, or exfiltrating log file contents externally | BLOCK | SL-B04 | Refuse; logs are local audit records only |
| Appending standard activation/completion entries to the log | ALLOW | SL-A01 | Safe when entries follow the prescribed format |
| Reading the log file for local review | ALLOW | SL-A02 | Safe read-only operation |
| Logging confirm-request events with decision outcomes | ALLOW | SL-A03 | Safe when no sensitive action details are included |
| Bulk export or full dump of log history | CONFIRM | SL-C01 | Confirm scope and destination before proceeding |
| Clearing or rotating the log file | CONFIRM | SL-C02 | Confirm before destroying audit trail |

## Required Operating Constraints

1. Never log sensitive data — passwords, tokens, API keys, personal content.
2. Only write to the designated log file path.
3. Sanitize all task descriptions before appending to logs.
4. Keep log entries concise and single-line. Reject any input containing encoded newlines or control characters that could break line boundaries (refined r2).
5. Never expose log contents to external services.
6. Confirm before clearing or bulk-exporting logs.

## Log Sanitization Policy

Before writing any log entry, strip or redact:
- API keys and tokens (patterns matching `sk-*`, `xoxb-*`, `ghp_*`, etc.)
- Passwords and secret values (including base64-encoded or obfuscated credentials) (refined r2)
- Email addresses and phone numbers
- File contents that were part of the original task
- URL-encoded or percent-encoded control characters (`%0A`, `%0D`, `%00`, etc.) (refined r2)

Replace sensitive content with `[REDACTED]`.

## Output Policy

Allowed:
- structured log entries following the prescribed format
- log summaries for local review
- activation/completion event records

Disallowed:
- raw sensitive data in any log field
- log entries with embedded shell commands or encoded control characters (refined r2)
- log file contents sent to external endpoints

## (Trigger, Task, Resources)

**Trigger:** Activate whenever a skill activation event is being logged, a log entry is appended, or the skill activation log file is read, exported, or cleared.

**Task:** Inspect each log operation against the safety rules. BLOCK if a log entry contains sensitive data (passwords, tokens, PII — including encoded or obfuscated forms), targets a path other than the designated log file, includes shell metacharacters, injection patterns, or encoded control characters (refined r2), or attempts to exfiltrate log contents externally. CONFIRM before bulk-exporting full log history or clearing/rotating the log file. ALLOW standard activation/completion log appends following the prescribed format, local log reads, and logging of confirm-request events without sensitive details.

**Resources:** No auxiliary resources required.

## References

- Original skill: `skill-logger`
- `references/risk-notes.md`
