# Risk Notes for safe-gifgrep

## Threat Model Summary

```
Skill: gifgrep
Actions:
  - read: search GIF providers (Tenor/Giphy), view metadata, preview thumbnails
  - write: download GIFs to ~/Downloads, extract stills/sheets to disk
  - destructive: overwrite existing files during still/sheet extraction
  - external: HTTP requests to Tenor API, Giphy API
  - credential: GIPHY_API_KEY, TENOR_API_KEY environment variables
Risks:
  - Credential exposure: API keys leaked in output, logs, or piped commands
  - Scope explosion: bulk downloads filling disk; excessive API queries hitting rate limits
  - External interaction: every search sends queries to third-party APIs
  - Irreversibility: file overwrites during still/sheet extraction
```

## Key Risks

### 1. API Key Leakage
`GIPHY_API_KEY` and `TENOR_API_KEY` are stored as environment variables. Commands using `--json` or piped output could inadvertently expose these.

Mitigation:
- block any operation that displays or logs API keys
- never include keys in command output or summaries

---

### 2. Uncontrolled Bulk Downloads
`--download --max N` writes N GIF files to `~/Downloads`. Large values consume disk space and bandwidth without user awareness.

Mitigation:
- hard cap at 10 downloads per invocation (BLOCK above)
- confirm any download operation (CONFIRM at or below cap)

---

### 3. Excessive API Usage
Large `--max` values or repeated searches can exhaust API quotas or trigger rate limiting.

Mitigation:
- confirm searches with `--max` > 20
- allow bounded searches ≤ 20

---

### 4. File Overwrite
`gifgrep still` and `gifgrep sheet` write output files (`-o` flag). Existing files at the target path may be silently overwritten.

Mitigation:
- confirm before extraction operations
- verify output path does not overwrite important files

---

### 5. Data Exfiltration via Piping
GIF URLs piped to external commands (`curl`, `wget`, or custom scripts) could exfiltrate data.

Mitigation:
- block piping URLs to external commands or services

---

## Safe vs Unsafe

Safe:
- basic search (metadata/URLs)
- TUI browsing
- thumbnail preview

Confirm:
- download (≤ 10)
- still/sheet extraction
- large result sets
- Finder reveal

Block:
- credential exposure
- bulk download (> 10)
- piping to external services
