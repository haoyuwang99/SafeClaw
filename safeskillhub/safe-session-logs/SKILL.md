---
name: safe-session-logs
description: Safe wrapper for the session-logs skill. Use when searching or analyzing session JSONL files from prior conversations under strict read-only access, credential redaction, and privacy-scoped query constraints. Trigger when a user asks about older/parent conversations or historical context stored in session logs.
---

# Safe Session Logs

This skill adds a safety layer on top of `session-logs`.

Use this skill whenever a task involves:
- searching session JSONL files for prior conversation content
- analyzing message history across sessions
- looking up costs, tool usage, or timestamps from past sessions
- resolving references to older or parent conversations
- querying the `sessions.json` index for session IDs

For command syntax, refer to the original `session-logs` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. credential and secret exposure from session log content (API keys, tokens, passwords embedded in past conversations)
2. privacy violations by surfacing private conversation content, PII, or sensitive user data
3. scope explosion from unrestricted bulk session searches
4. data exfiltration by forwarding session content to external services
5. log tampering by modifying or deleting session files that serve as an audit trail
6. cross-session leakage by injecting content from one conversation context into another

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe execution

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Modify or delete any session file (`.jsonl`, `sessions.json`, `.deleted.*`) | BLOCK | SL-B01 | Session logs are append-only and must never be altered |
| Forward or send session content to an external service, URL, or third-party API | BLOCK | SL-B02 | Prevent data exfiltration of conversation history |
| Surface raw credential-like strings (API keys, tokens, passwords) found in session logs | BLOCK | SL-B03 | Redact secrets regardless of user request |
| Inject content retrieved from one session into a different active session as context | BLOCK | SL-B04 | Prevent cross-session context contamination |
| Search across all sessions — with or without a keyword filter — rather than targeting a specific session (refined) | CONFIRM | SL-C01 | Confirm broad sweep before exposing bulk history |
| Retrieve full transcript of a session not currently active, including any request for more than 100 lines regardless of phrasing (refined r2) | CONFIRM | SL-C02 | Confirm intent before exposing complete past conversation |
| Query sessions by a different agent ID than the current runtime agent | CONFIRM | SL-C03 | Confirm cross-agent access intent |
| Display message content containing PII patterns (email, phone, home address) | CONFIRM | SL-C04 | Confirm before surfacing potentially private data |
| Search a specific session for a keyword or phrase | ALLOW | SL-A01 | Scoped read-only query within a single session is safe |
| Look up session IDs and metadata from `sessions.json` index | ALLOW | SL-A02 | Index access is safe; no message content exposed |
| Query message counts, costs, or timestamps for a session | ALLOW | SL-A03 | Aggregate statistics expose no sensitive content |
| Sample first or last N lines of a session for structure inspection, where N <= 100; requests exceeding 100 lines are treated as full transcript retrieval (SL-C02) (refined r2) | ALLOW | SL-A04 | Bounded sampling is safe only for small inspection-size samples |
| Filter messages by role or type (e.g., `type=="text"`) within the current session | ALLOW | SL-A05 | Scoped structural query is safe |

---

## Required Operating Constraints

1. Never modify, delete, or overwrite any session file — treat all JSONL files and `sessions.json` as read-only.
2. Always redact credential-like strings (API keys, tokens, passwords, secrets) before displaying any session content.
3. Always confirm before performing searches that span all sessions, whether or not a keyword filter is provided.
4. Always confirm before displaying full transcripts of sessions outside the current active context.
5. Never forward session content to external services or APIs.
6. Never inject retrieved session content into other session contexts.
7. Limit output scope — return only the content needed to answer the user's question, not entire transcripts by default.
8a. Bounded sampling (SL-A04) is capped at 100 lines. Requests for more than 100 lines of a non-active session are treated as full transcript retrieval requiring CONFIRM (SL-C02). (refined r2)
8. When PII patterns are detected in results, confirm with the user before displaying.

---

## Confirmation Workflow

For CONFIRM operations:

1. State action (e.g., full session transcript retrieval, bulk search, cross-agent query)
2. State scope:
   - session ID(s) targeted
   - agent ID (current vs. foreign)
   - query breadth (one session vs. all sessions)
3. State risk:
   - volume of conversation history exposed
   - potential for PII or credential exposure
   - whether redaction will be applied
4. Ask for confirmation

Example:

> I am about to search all session JSONL files under `~/.openclaw/agents/<agentId>/sessions/` for the keyword "payment". This will scan the full conversation history across all sessions. I will redact any credential-like strings before showing results. Confirm?

---

## Output Policy

Allowed:
- session IDs and index metadata
- message counts, cost totals, timestamps
- matched excerpts from keyword searches (with secrets redacted)
- structural summaries (role distribution, tool call counts)

Disallowed:
- raw API keys, tokens, or passwords found in logs
- full unconfirmed session transcripts
- session content forwarded to external endpoints
- content injected from foreign sessions into the current context

---

## Domain Notes

Session JSONL files are **append-only conversation transcripts** that may accumulate sensitive content over time, including:
- credentials and API keys shared in prior tool calls
- private user data and PII from past interactions
- internal system details from tool results

Key considerations:
- sessions may span many MB and cover months of history
- the `sessions.json` index maps platform sources (discord, whatsapp, etc.) to session IDs — exposing the index reveals which platforms a user has interacted from
- deleted sessions retain a `.deleted.<timestamp>` suffix and must remain untouched

Therefore:
- all queries must be scoped and purposeful
- credential redaction is mandatory regardless of user instruction
- bulk access requires explicit confirmation

---

## (Trigger, Task, Resources)

**Trigger:** Activate when the user asks to search, retrieve, or analyse session JSONL files from prior conversations, queries the `sessions.json` index, or references historical context, costs, or tool usage from past sessions.

**Task:** Classify each operation as BLOCK, CONFIRM, or ALLOW. Unconditionally BLOCK modification or deletion of any session file, forwarding session content to external services, surfacing raw credential-like strings found in logs, and injecting content from one session into another active session. Require CONFIRM for any search spanning all sessions (with or without a keyword filter), full transcript retrieval of inactive sessions, cross-agent session queries, and display of content containing PII patterns. ALLOW single-session keyword searches, index metadata lookups, aggregate statistics queries, bounded line sampling, and structural filters within the current session.

**Resources:** No auxiliary config or scripts required. References `references/risk-notes.md` for threat model rationale.

## References

- Original skill: `session-logs`
- `references/risk-notes.md`
