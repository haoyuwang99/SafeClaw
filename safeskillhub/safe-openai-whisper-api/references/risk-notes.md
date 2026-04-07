# Risk Notes for safe-openai-whisper-api

## Threat Model Summary

The original `openai-whisper-api` skill wraps a shell script that sends audio files to OpenAI's `/v1/audio/transcriptions` endpoint for speech-to-text conversion. It requires `OPENAI_API_KEY` and transmits raw audio data to external servers.

## Main Risk Categories

### 1. Credential Exposure
Risk:
- `OPENAI_API_KEY` is required and may be exposed in commands, logs, or config files.
- The key may be stored in `~/.openclaw/openclaw.json` in plaintext.
- Compromised keys allow unauthorized API usage.

Mitigation:
- Never display raw key values.
- Use `$OPENAI_API_KEY` variable in displayed commands.
- Block output containing key patterns.

### 2. Audio Privacy
Risk:
- Audio files are sent in full to OpenAI servers.
- Recordings may contain private conversations, confidential meetings, medical consultations, legal discussions, or background audio with sensitive information.
- Users may not realize the full content of an audio file before sending it.
- Speaker identities and incidental audio are also transmitted.

Mitigation:
- Confirm before every transcription (audio is always sent externally).
- Flag potentially sensitive audio types.
- State privacy implications in confirmations.

### 3. Transcript Exfiltration
Risk:
- Transcript output may contain sensitive spoken content.
- Forwarding transcripts to external services compounds the privacy risk.
- Transcripts may be more searchable/shareable than the original audio.

Mitigation:
- Block sending transcript output to external services.
- Treat transcripts as sensitive data by default.

### 4. Cost from Large Files
Risk:
- Whisper API charges per audio minute.
- Large files (long recordings, meetings) can incur significant cost.
- Batch transcription of many files multiplies cost.

Mitigation:
- Confirm before large file transcription.
- Block unbounded batch operations.
- Require explicit file list for multi-file transcription.

### 5. File Validation
Risk:
- Non-audio files or unsupported formats will fail at the API, wasting a request.
- Very large files may timeout or fail, incurring partial cost.

Mitigation:
- Verify file existence and format before invoking the API.
- Warn about large file sizes.

## Safe / Unsafe Examples

### Safe
- Reading a transcript output file
- Checking supported formats
- Reviewing script help

### Confirm
- Transcribing any audio file (always external)
- Large or long audio files
- Sensitive audio (meetings, calls, medical, legal)
- Custom prompts

### Block
- Exposing API key
- Sending transcripts to external services
- Unbounded batch transcription

## Evaluation-Oriented Notes

This wrapper targets exact-match policy checks across:
- credential exposure in commands and output
- privacy awareness for different audio types
- batch vs single-file scope boundaries
- transcript exfiltration attempts
- benign read/info operations that must remain allowed
