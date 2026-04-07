---
name: safe-healthcheck
description: Safe wrapper for the healthcheck skill. Use when performing host security audits, hardening, firewall/SSH configuration, or OpenClaw security checks under strict state-change control, credential protection, and rollback-first safeguards.
---

# Safe Healthcheck

This skill adds a safety layer on top of `healthcheck`.

Use this skill whenever a task involves:
- healthcheck
- host security auditing
- firewall or SSH configuration
- OpenClaw security audit or hardening
- system hardening or risk posture assessment
- scheduling periodic security checks

For command syntax, refer to the original `healthcheck` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. unintended system lockout (firewall, SSH, access misconfiguration)
2. credential and token leakage
3. irreversible system state changes without rollback plan
4. unauthorized privilege escalation
5. silent persistence (cron jobs, startup tasks) without explicit approval
6. exposure of sensitive host details in logs or memory

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe execution

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Display or log tokens, credentials, or sensitive config contents | BLOCK | HC-B01 | Never expose secrets |
| Modify remote access (SSH/RDP) without confirming user's access method | BLOCK | HC-B02 | Prevent lockout |
| Run `--fix` or remediation without showing plan first | BLOCK | HC-B03 | Require plan-before-action |
| Disable firewall entirely | BLOCK | HC-B04 | Prevent full exposure |
| Remove or downgrade security packages | BLOCK | HC-B05 | Prevent security regression |
| Execute remediation commands with `sudo` or elevated privileges | BLOCK | HC-B06 | Block unless user explicitly grants privilege escalation per-command |
| Schedule cron jobs containing remote code execution patterns (`curl\|bash`, `wget\|sh`), data exfiltration, or known dangerous command patterns | BLOCK | HC-B07 | Block dangerous cron payloads regardless of privilege level (refined) |
| Firewall rule changes (open/close ports, modify rules) | CONFIRM | HC-C01 | Show exact command, impact, and rollback |
| SSH/RDP configuration changes | CONFIRM | HC-C02 | Confirm access preservation |
| Install or remove packages | CONFIRM | HC-C03 | Confirm system modification |
| Enable or disable services | CONFIRM | HC-C04 | Confirm service impact |
| User or group modifications | CONFIRM | HC-C05 | Confirm permission changes |
| Schedule cron jobs (`openclaw cron add`) with safe command content | CONFIRM | HC-C06 | Confirm persistence and cadence; escalates to BLOCK via HC-B07 if command contains dangerous patterns (refined) |
| Apply OpenClaw safe defaults (`openclaw security audit --fix`) | CONFIRM | HC-C07 | Confirm scope of fix |
| Update policy changes (auto-update enable/disable) | CONFIRM | HC-C08 | Confirm update behaviour |
| Access sensitive files or directories | CONFIRM | HC-C09 | Confirm data access scope |
| Read-only system checks (`uname`, `sw_vers`, `lsof`, `ss`) | ALLOW | HC-A01 | Safe observation |
| Firewall status check (read-only) | ALLOW | HC-A02 | Safe observation |
| `openclaw security audit` (without `--fix`) | ALLOW | HC-A03 | Safe read-only audit |
| `openclaw security audit --deep` | ALLOW | HC-A04 | Safe read-only deep audit |
| `openclaw security audit --json` | ALLOW | HC-A05 | Safe structured output |
| `openclaw update status` | ALLOW | HC-A06 | Safe version check |
| `openclaw status` / `openclaw health --json` | ALLOW | HC-A07 | Safe status check |
| `openclaw cron list` / `openclaw cron runs` | ALLOW | HC-A08 | Safe read-only listing |
| Backup status check (`tmutil status`) | ALLOW | HC-A09 | Safe observation |

---

## Required Operating Constraints

1. Never expose tokens, credentials, or sensitive config file contents.
2. Never modify remote access settings without confirming user's connection method.
3. Always show remediation plan with exact commands before any state change.
4. Always include rollback instructions for every state-changing operation.
5. Never disable firewall entirely.
6. Never create cron jobs or scheduled tasks without explicit approval.
7. Block privilege escalation unless user approves each specific command.
8. Redact sensitive host details (usernames, hostnames, IPs, tokens) in all output and logs.
9. Prefer staged, reversible changes over batch operations.
10. Stop and ask for guidance on unexpected output during remediation.

---

## Remediation Workflow

Before any state change:

1. Show the exact command to be executed
2. Explain the impact in plain language
3. Provide the rollback command
4. Confirm that access will be preserved
5. Wait for explicit user approval

Example:

> I am about to run `ufw allow 22/tcp` to open SSH port. This allows inbound SSH connections. Rollback: `ufw delete allow 22/tcp`. Your current SSH access will be preserved. Confirm?

---

## Scheduling Safeguards

Before creating any cron job:

1. Show the exact `openclaw cron add` command
2. State cadence (daily/weekly), time window, and output location
3. Confirm no secrets will appear in cron output or logs
4. Check for existing jobs (`openclaw cron list`) to avoid duplicates
5. Use stable job names (`healthcheck:security-audit`, `healthcheck:update-status`)

---

## Confirmation Workflow

For CONFIRM operations:

1. State action (firewall change / SSH config / install package / schedule cron)
2. State target system and scope
3. State risk:
   - lockout potential
   - irreversibility
   - persistence
4. Show exact command and rollback
5. Ask for confirmation

---

## Output Policy

Allowed:
- system status summaries
- audit results and findings
- remediation plans with commands
- posture reports

Disallowed:
- tokens, credentials, API keys
- full config file contents containing secrets
- unredacted hostnames, IPs, or usernames in stored output
- sensitive serial numbers or hardware identifiers

---

## Domain Notes

This skill performs **host-level security auditing and system modification**.

Key considerations:
- incorrect firewall or SSH changes can permanently lock out the user
- system-level changes are difficult to reverse
- scheduled tasks persist beyond the current session
- credential and host detail exposure enables further attacks

Therefore:
- every state change requires explicit approval with rollback plan
- all operations must preserve existing access
- output must be redacted before storage

---

## (Trigger, Task, Resources)

**Trigger:** Activates whenever a task involves host security auditing, system hardening, firewall or SSH configuration, package management, service control, scheduled security checks, or OpenClaw security operations — any operation that could modify system state, expose credentials, cause lockout, or create persistent scheduled tasks.

**Task:** If the operation would expose tokens/credentials, modify remote access without confirming the user's connection method, run remediation without showing a plan first, disable the firewall entirely, remove security packages, or execute commands with `sudo` without per-command approval → BLOCK. If the operation changes firewall rules, SSH/RDP config, installs/removes packages, enables/disables services, modifies users/groups, schedules cron jobs, applies security fixes, changes update policies, or accesses sensitive files → CONFIRM with exact command, plain-language impact, rollback instructions, and access preservation confirmation. Otherwise (read-only system checks, firewall status, security audits without `--fix`, version/status checks, cron listings, backup status) → ALLOW.

**Resources:** `references/risk-notes.md` — threat model and risk rationale. No auxiliary config or scripts required.

---

## References

- Original skill: `healthcheck`
- `references/risk-notes.md`
