# Risk Notes for safe-spotify-player

## Threat Model Summary

spotify-player controls Spotify playback and search via `spogo` or `spotify_player` CLI tools. It involves browser cookie extraction for authentication and local config file management.

## Action Space

- **read**: search tracks, check status, list devices, read config
- **write**: modify config files (`app.toml`), set `client_id`
- **destructive**: none directly (no delete operations)
- **external**: Spotify API calls, browser cookie extraction
- **credential**: Spotify cookies, OAuth tokens, `client_id`

## Key Risks

### 1. Credential Leakage
Spotify session cookies and OAuth tokens could be exposed in conversation output or logs.

Mitigation:
- never print raw credentials
- redact all token/cookie values

---

### 2. Unauthorized Cookie Extraction
`spogo auth import --browser <name>` reads browser cookie stores, which is a privileged operation that should only happen with explicit user consent.

Mitigation:
- require explicit user request with browser name
- confirm before executing

---

### 3. Configuration Tampering
Modifying `~/.config/spotify-player/app.toml` could change `client_id` or other settings unexpectedly.

Mitigation:
- confirm before any config write
- show exact changes

---

### 4. Device Hijacking
Switching playback to wrong device could disrupt other users on shared accounts.

Mitigation:
- confirm device target before switching

---

### 5. Account Metadata Exposure
Listening history and account details could reveal private information.

Mitigation:
- limit output to user-requested scope
- summarize rather than dump raw data

---

## Safe vs Unsafe

Safe:
- search tracks/albums/artists
- check playback status
- basic playback controls (play/pause/next/prev)
- list devices

Confirm:
- cookie import from browser
- config file modifications
- device switching

Block:
- credential exposure
- unsolicited cookie extraction
- sending credentials externally
