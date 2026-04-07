# Risk Notes for safe-eightctl

## Threat Model Summary

eightctl is a CLI for controlling Eight Sleep devices via unofficial API.
It requires credentials and can change real-world device behavior.

## Action Space

```
Skill: eightctl
Actions:
  - read: status, base info, alarm list, schedule list, audio state
  - write: set temperature, create alarms, create/update schedules, set base angle
  - destructive: dismiss alarms, power off device
  - external: unofficial Eight Sleep API (rate-limited)
  - credential: email/password in ~/.config/eightctl/config.yaml or env vars
```

## Key Risks

### 1. Credential Exposure
Email/password stored in config or env.

Mitigation:
- never expose or log credentials

---

### 2. Physical Environment Manipulation
Temperature and device state directly affect user comfort.

Mitigation:
- require confirmation for all changes
- block extreme temperature values

---

### 3. Persistent Behavior Changes
Schedules and alarms persist beyond execution.

Mitigation:
- require explicit confirmation
- show full schedule details before applying

---

### 4. Sleep Disruption
Audio, alarms, and temperature may disrupt sleep.

Mitigation:
- treat as high-impact action
- confirm intent

---

### 5. API Abuse
Unofficial API is rate-limited.

Mitigation:
- avoid repeated logins
- avoid loops

---

## Safe vs Unsafe

Safe:
- status
- device info
- alarm list
- schedule list

Confirm:
- temperature
- power on/off
- alarms (create/dismiss)
- schedules (create/update)
- audio control
- base angle

Block:
- credential exposure
- repeated login abuse
- extreme temperatures
