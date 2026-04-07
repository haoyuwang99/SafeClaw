# Risk Notes for safe-sonoscli

## Threat Model Summary

The sonoscli skill controls Sonos speakers on the local network — playback, volume, grouping, and content selection. Because actions affect physical devices with immediate real-world effects, the risk profile includes unauthorized playback disruption, volume abuse, credential exposure (Spotify), and unintended device targeting.

## Key Risks

### 1. Unauthorized Playback
The agent could start, stop, or change playback on speakers without user intent, disrupting active listening sessions.

Mitigation:
- confirm before any playback control operation
- require explicit speaker targeting

---

### 2. Volume Abuse
Setting volume to very high levels could cause physical discomfort or speaker damage.

Mitigation:
- block volume above 75 unless explicitly requested
- confirm all volume changes

---

### 3. Credential Exposure
Spotify integration requires `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` environment variables that must remain secret.

Mitigation:
- never expose credentials in output or logs
- block any operation that would reveal env var values

---

### 4. Unintended Device Targeting
Without explicit `--name` or `--ip` flags, commands may target the wrong speaker or all speakers.

Mitigation:
- block commands without explicit device targeting
- require `--name` or `--ip` for all control operations

---

### 5. Multi-Speaker Disruption
Operations like `sonos party` affect all speakers on the network simultaneously, with broad blast radius.

Mitigation:
- confirm before any group-wide operations
- warn about the scope of impact

---

### 6. Queue Destruction
Clearing the queue removes all queued tracks irreversibly.

Mitigation:
- confirm before queue clear operations

---

## Safe vs Unsafe

Safe:
- discovering speakers
- checking playback status
- listing favorites, queue, groups
- searching Spotify (read-only)

Confirm:
- playing, pausing, or stopping content
- adjusting volume
- grouping speakers (party/join)
- clearing the queue

Block:
- exposing Spotify credentials
- setting volume above 75 without explicit request
- commands without explicit speaker targeting
