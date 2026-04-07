# Risk Notes for safe-camsnap

## Threat Model Summary

camsnap connects to RTSP/ONVIF cameras over the local network to capture snapshots, video clips, and motion events. It stores camera credentials locally in `~/.config/camsnap/config.yaml` and can trigger automated shell commands via `watch --action`.

## Action Space

- **read**: `camsnap discover`, `camsnap doctor`, list configured cameras
- **write**: `camsnap snap` (capture image), `camsnap clip` (capture video), `camsnap add` (add camera config)
- **destructive**: `camsnap watch --action` (execute arbitrary shell commands on motion events)
- **external**: Camera discovery scans local network; captured media could be sent externally
- **credential**: Camera usernames and passwords stored in `config.yaml`

## Key Risks

### 1. Credential Exposure
- **Risk**: Camera credentials in config.yaml leaked via display, logging, or command output.
- **Category**: Credential exposure
- **Trigger**: Reading config file, showing `--user`/`--pass` flags, or dumping camera details.
- **Mitigation**: Never display or log credentials.

### 2. Visual Privacy Leakage
- **Risk**: Snapshots and clips may capture home interiors, personal activity, or sensitive environments.
- **Category**: External interaction, Irreversibility
- **Trigger**: Any `snap` or `clip` command; outputting media into chat.
- **Mitigation**: Confirm all captures; never output raw media; never send externally.

### 3. Surveillance Abuse
- **Risk**: Continuous monitoring without clear user intent constitutes unauthorized surveillance.
- **Category**: Scope explosion
- **Trigger**: `camsnap watch` without bounded duration or explicit purpose.
- **Mitigation**: Require confirmation with justification and duration for monitoring.

### 4. Arbitrary Command Execution
- **Risk**: `watch --action` executes arbitrary shell commands when motion is detected.
- **Category**: Privilege escalation
- **Trigger**: `camsnap watch kitchen --action 'rm -rf /'` or any shell payload.
- **Mitigation**: Block all `watch --action` commands unconditionally.

### 5. Network Probing
- **Risk**: Camera discovery scans local network, potentially revealing topology.
- **Category**: External interaction
- **Trigger**: `camsnap discover` used for network reconnaissance.
- **Mitigation**: Allow discovery (metadata only) but restrict to explicit user request.

## Safe vs Unsafe

Safe:
- `camsnap doctor` (health check)
- `camsnap discover` (metadata enumeration)
- listing configured cameras (names only, no credentials)

Confirm:
- `camsnap snap` (capture snapshot)
- `camsnap clip` (capture video clip)
- `camsnap watch` (monitoring without action)
- `camsnap add` (adding new camera)

Block:
- displaying credentials
- `camsnap watch --action` (arbitrary command execution)
- sending captured media externally
- outputting raw image/video into chat
