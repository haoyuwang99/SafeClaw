# Risk Notes for safe-oracle

## Threat Model Summary

oracle bundles local files and prompts into one-shot requests sent to external LLM services (OpenAI, Google) via API or browser automation. It reads local files and sends them to third-party services, making data exfiltration the primary risk.

## Action Space

- **read**: Local project files via `--file` globs, session data from `~/.oracle/sessions`
- **write**: Session files, clipboard content (`--copy`), rendered output
- **destructive**: `--force` bypasses duplicate prompt guard, potentially wasting tokens/cost
- **external**: Sends file contents + prompts to external LLM APIs (OpenAI, Google, etc.) and optionally to remote browser hosts
- **credential**: Uses `OPENAI_API_KEY` for API engine; browser sessions may contain auth cookies; remote browser uses `--remote-token`

## Key Risks

### 1. Data Exfiltration — Sensitive Files Sent Externally
File attachment globs may inadvertently include `.env`, private keys, credentials, or proprietary code sent to third-party LLM services.

Mitigation:
- Block secret file patterns from attachment
- Always preview file list before sending
- Require dry-run before live execution

### 2. Credential Exposure
API keys may be visible in command arguments, logs, or output. Remote browser tokens may leak.

Mitigation:
- Block credentials in command arguments
- Use environment variables only
- Never expose tokens in output

### 3. Cost/Token Waste
Broad file globs or duplicate runs can consume significant API credits.

Mitigation:
- Require `--dry-run` preview for token estimation
- Block `--force` without justification
- Warn on large payloads

### 4. Scope Explosion — Over-broad File Attachment
Globs like `**` or `.` can include the entire project tree.

Mitigation:
- Block unscoped globs
- Require explicit exclusion patterns

### 5. Remote Browser Trust
Sending data to remote browser hosts (`--remote-host`) routes file contents through potentially untrusted infrastructure.

Mitigation:
- Block remote host usage without trust verification

## Safe vs Unsafe

Safe:
- Dry-run commands
- Session status checks
- Help/version

Confirm:
- Live API/browser runs
- File attachments
- Session reattachment
- Clipboard payload preparation

Block:
- Secret file attachment
- Force-bypassing duplicate guard
- Credential exposure in commands
- Unscoped broad globs
- Untrusted remote hosts
