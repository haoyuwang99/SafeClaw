# Risk Notes for safe-skill-logger

## Threat Model Summary

The skill-logger meta-skill appends audit entries to a log file whenever any skill activates. Because it processes arbitrary task descriptions and runs alongside all other skills, it is a vector for sensitive data leakage, log injection, and path traversal attacks.

## Key Risks

### 1. Sensitive Data Leakage
Task descriptions may contain passwords, tokens, or personal information that would be persisted to disk in plaintext logs.

Mitigation:
- sanitize all task descriptions before logging
- block entries containing detected secrets or PII patterns

---

### 2. Log Injection
Crafted task descriptions containing shell metacharacters or newlines could inject false log entries or execute commands via the echo-based logging mechanism.

Mitigation:
- block shell metacharacters in task fields
- validate single-line format before appending

---

### 3. Path Traversal
A modified log path could redirect log writes to sensitive system files.

Mitigation:
- hardcode the authorized log file path
- block writes to any other location

---

### 4. Disk Exhaustion
Unbounded logging in high-activity environments could fill disk space.

Mitigation:
- keep entries concise
- confirm before bulk operations
- recommend log rotation

---

### 5. Log Exfiltration
Log files contain an audit trail of all skill usage that could be valuable to attackers.

Mitigation:
- block sharing log contents externally
- treat logs as local-only audit records

---

## Safe vs Unsafe

Safe:
- appending standard activation/completion entries
- reading logs for local review
- logging confirm-request events

Confirm:
- bulk export of log history
- clearing or rotating the log file

Block:
- logging entries containing secrets or PII
- writing to unauthorized file paths
- task descriptions with shell injection patterns
- exfiltrating log contents externally
