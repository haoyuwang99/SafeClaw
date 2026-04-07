# Risk Notes for safe-blucli

## Threat Model Summary

blucli (`blu`) controls BluOS/NAD audio players over the local network. It supports device discovery, playback control, volume adjustment, speaker grouping, and TuneIn/Spotify streaming.

## Action Space

- **read**: `blu status`, `blu devices`, `blu volume` (query current state)
- **write**: `blu play/pause/stop`, `blu volume set`, `blu group add/remove`
- **destructive**: `blu raw` (arbitrary low-level endpoint access)
- **external**: TuneIn/Spotify streaming (fetches external audio content)
- **credential**: None (no authentication required by default)

## Key Risks

### 1. Wrong Device Targeting
- **Risk**: Controlling an unintended speaker in the wrong room.
- **Category**: Scope explosion
- **Trigger**: Missing `--device` flag when multiple players exist on network.
- **Mitigation**: Block any control action without an explicit device target.

### 2. Audio Disruption
- **Risk**: Sudden loud playback or extreme volume changes.
- **Category**: Irreversibility (physical environment impact)
- **Trigger**: `volume set 100` or `play` without user awareness.
- **Mitigation**: Confirm all playback and volume changes; block volume above 80%.

### 3. Multi-room Interference
- **Risk**: Grouping operations affect multiple rooms simultaneously.
- **Category**: Scope explosion
- **Trigger**: `group add` implicitly linking speakers.
- **Mitigation**: Confirm grouping; list all affected devices before execution.

### 4. Network Scanning
- **Risk**: Repeated device discovery scans local network.
- **Category**: External interaction
- **Trigger**: Automated loops calling `blu devices`.
- **Mitigation**: Allow single discovery; confirm repeated scans.

### 5. External Stream Risk
- **Risk**: Playing arbitrary URLs on a local device.
- **Category**: External interaction
- **Trigger**: `blu play <url>` with untrusted source.
- **Mitigation**: Confirm stream source before playback.

### 6. Raw Command Access
- **Risk**: `blu raw` allows arbitrary low-level BluOS API calls.
- **Category**: Privilege escalation
- **Trigger**: Direct `blu raw` invocation.
- **Mitigation**: Block unconditionally.

## Safe vs Unsafe

Safe:
- `blu status`
- `blu devices` (first call)
- `blu volume` (query only)

Confirm:
- `blu play/pause/stop`
- `blu volume set <level≤80>`
- `blu group add/remove`
- TuneIn/Spotify playback

Block:
- `blu raw`
- any command without explicit device target
- `blu volume set` with level > 80
