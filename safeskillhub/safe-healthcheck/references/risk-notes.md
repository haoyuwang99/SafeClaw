# Risk Notes for safe-healthcheck

## Threat Model Summary

```
Skill: healthcheck
Actions:
  - read: OS info, listening ports, firewall status, backup status, OpenClaw audit, version check, disk encryption status
  - write: apply OpenClaw safe defaults (--fix), create cron jobs, write memory/audit logs
  - destructive: firewall rule changes, SSH/RDP config changes, enable/disable services, user/group modifications, update policy changes
  - external: none directly (all operations are local/host-level)
  - credential: access to OpenClaw credentials, system config files, tokens, SSH keys
Risks:
  - Irreversibility: firewall misconfiguration causing lockout; SSH config changes severing remote access
  - Scope explosion: batch remediation applying many changes at once; overly aggressive hardening
  - Credential exposure: OpenClaw tokens, SSH keys, system credentials visible during audit
  - Privilege escalation: sudo/root required for most hardening; agent could elevate beyond intent
  - Persistence: cron jobs and startup tasks persist silently beyond session
```

## Key Risks

### 1. System Lockout
Modifying firewall rules or SSH configuration can permanently lock out the user, especially on remote/headless systems. This is the highest-severity risk.

Mitigation:
- block SSH/RDP changes without confirming user's access method
- always confirm access preservation before firewall changes
- require rollback instructions for every change
- block disabling firewall entirely

---

### 2. Irreversible System Changes
Package removal, service disabling, and user/group modifications can be difficult or impossible to reverse cleanly.

Mitigation:
- confirm each individual change
- prefer staged changes over batch operations
- show exact rollback commands

---

### 3. Credential Exposure
Security audits access sensitive config files containing tokens, SSH keys, and credentials. These can leak through output, logs, or memory files.

Mitigation:
- block display of credentials and token contents
- redact sensitive details in all stored output
- never log tokens in cron output

---

### 4. Privilege Escalation
Most hardening operations require root/sudo. An unguarded agent could escalate privileges beyond what the user intends.

Mitigation:
- block blanket sudo usage; require per-command approval
- never assume root access; verify privilege level first

---

### 5. Silent Persistence
Cron jobs and scheduled tasks persist beyond the session. If created without awareness, they run unmonitored.

Mitigation:
- confirm before creating any scheduled task
- check for existing jobs to avoid duplicates
- use stable, predictable job names
- ensure no secrets in cron output

---

### 6. Overly Aggressive Hardening
Applying a strict security profile without understanding the user's workflow can break legitimate services.

Mitigation:
- determine risk profile after establishing system context
- show full remediation plan before any changes
- stop on unexpected output and ask for guidance

---

## Safe vs Unsafe

Safe:
- read-only system checks (OS, ports, firewall status)
- OpenClaw audit (without --fix)
- version/update status
- cron listing
- backup status

Confirm:
- firewall changes
- SSH/RDP config
- package install/remove
- service enable/disable
- cron job creation
- OpenClaw --fix
- update policy changes

Block:
- credential exposure
- SSH changes without access method confirmation
- remediation without showing plan
- disable firewall entirely
- security package removal
- unscoped privilege escalation
