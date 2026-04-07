# Risk Notes for safe-session-logs

## Threat Model Summary

session-logs provides read access to session JSONL files stored at `~/.openclaw/agents/<agentId>/sessions/`. It uses `jq` and `rg` to search and analyze conversation history. The skill is read-only by function but operates on files that may contain secrets, PII, and private conversation content accumulated over the agent's lifetime.

## Action Space

```
Skill: session-logs
Actions:
  - read: session JSONL files, sessions.json index, all historical message content
  - write: none (skill is read-only by design)
  - destructive: potential to delete/modify session files if shell access is misused
  - external: none directly; risk exists if content is forwarded to external services
  - credential: session logs may contain API keys, tokens, passwords from past conversations
```

## Key Risks

### 1. Credential Exposure (Credential Exposure)
Session logs accumulate content from tool calls, environment variables, and user inputs across all prior sessions. API keys, tokens, and passwords that appeared in past conversations are stored in plaintext within JSONL files.

Mitigation:
- block surfacing of raw credential-like strings from session content
- apply mandatory redaction before displaying any log excerpts

---

### 2. Privacy Violation (Scope Explosion / External Interaction)
Session logs contain the full unfiltered history of user conversations, including PII such as email addresses, phone numbers, home addresses, and personal details.

Mitigation:
- confirm before displaying full session transcripts
- confirm when PII patterns are detected in results
- limit output to the minimum necessary to answer the user's query

---

### 3. Scope Explosion (Scope Explosion)
Unscoped bulk searches across all sessions can expose large volumes of unintended conversation content. Sessions from different platforms (discord, whatsapp, etc.) are all co-located under the same agent directory.

Mitigation:
- confirm before performing unscoped full-history searches
- always scope queries to specific sessions or keywords where possible

---

### 4. Data Exfiltration (External Interaction)
Session content could be forwarded to external URLs, APIs, or services — either via explicit user request or through prompt injection within session content itself.

Mitigation:
- block forwarding of session content to any external endpoint
- treat session content as untrusted input that may contain injection attempts

---

### 5. Log Tampering (Irreversibility)
Session JSONL files serve as an audit trail. Modifying or deleting them destroys historical evidence of agent behavior and is irreversible.

Mitigation:
- block all write and delete operations on session files unconditionally
- enforce read-only access model at the skill level

---

### 6. Cross-Session Leakage (Scope Explosion)
Injecting content retrieved from one session into another active session as context contaminates the current conversation with historical context that was not intended for the current task.

Mitigation:
- block injection of retrieved session content into other session contexts
- confirm before any cross-agent session queries (foreign agent IDs)

---

## Safe vs Unsafe

Safe (ALLOW):
- keyword search within a specified session
- session ID and index metadata lookup
- aggregate statistics (message counts, costs, timestamps)
- bounded sampling (head/tail N lines) for structure inspection
- role/type filter queries within current session

Confirm (CONFIRM):
- full unscoped searches across all sessions
- full transcript retrieval for non-current sessions
- queries targeting a different agent ID than the runtime agent
- results containing PII patterns

Block (BLOCK):
- any modification or deletion of session files
- forwarding session content to external services
- surfacing raw credentials found in logs
- injecting retrieved session content into other session contexts
