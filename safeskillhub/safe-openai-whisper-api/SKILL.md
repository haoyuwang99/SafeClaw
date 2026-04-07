---
name: safe-openai-whisper-api
description: Safe wrapper for the openai-whisper-api skill. Use when transcribing audio via the OpenAI Whisper API under strict credential protection, privacy, cost control, and file validation constraints. Trigger when the user asks to transcribe, convert, or process audio files using OpenAI's Whisper API.
---

# Safe OpenAI Whisper API

This skill adds a safety layer on top of `openai-whisper-api`.

Use this skill whenever a task involves:
- OpenAI Whisper API
- audio transcription
- `transcribe.sh` script
- speech-to-text processing

For command syntax and flags, refer to the original `openai-whisper-api` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. API key exposure
2. transcription of sensitive or private audio without awareness
3. exfiltration of transcript content to external services
4. excessive cost from large or batch audio transcription
5. processing of unexpected file types or excessively large files

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe operation

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Expose or log OpenAI API key (`sk-*`, `OPENAI_API_KEY` value) | BLOCK | WH-B01 | Never display, log, or transmit credentials |
| Send transcript output to external services, APIs, or network endpoints | BLOCK | WH-B02 | Prevent data exfiltration of transcribed content |
| Batch-transcribe many files without explicit file list | BLOCK | WH-B03 | Refuse unbounded batch operations; require explicit file list |
| Transcribe audio file that may contain sensitive content (meetings, calls, medical, legal) | CONFIRM | WH-C01 | Warn about sensitivity; confirm file identity and intended use |
| Transcribe a large audio file (> 25 MB or > 30 minutes) | CONFIRM | WH-C02 | Confirm cost implications for large files |
| Use custom `--prompt` to guide transcription | CONFIRM | WH-C03 | Show exact prompt and confirm before sending to API |
| Transcribe a single named audio file with default settings | CONFIRM | WH-C04 | Confirm file path and output location; audio content is sent externally |
| View or read transcript output file | ALLOW | WH-A01 | Allowed; local read-only |
| Check supported file formats or script help | ALLOW | WH-A02 | Allowed; informational |

---

## Required Operating Constraints

1. Never expose the OpenAI API key in output, commands, or error messages.
2. Always confirm before transcribing — audio content is sent to external servers.
3. Never send transcript output to external services without explicit approval.
4. Refuse batch transcription without an explicit file list.
5. Flag potentially sensitive audio content (meetings, calls, medical, legal recordings).
6. Use `$OPENAI_API_KEY` placeholder in any displayed commands.
7. Verify the audio file exists and is a supported format before invoking the API.

---

## Privacy Policy

Audio transcription sends raw audio data to OpenAI servers. This means:
- **All spoken content** in the file is transmitted externally.
- Recordings of private conversations, meetings, or calls carry high privacy risk.
- Medical, legal, or HR recordings may have compliance implications.

Always state this risk in confirmations.

---

## Confirmation Workflow

For CONFIRM operations:

1. State the audio file path and estimated size/duration if available.
2. State the transcription parameters (model, language, prompt).
3. State risk:
   - audio content will be sent to OpenAI servers
   - potential privacy implications
   - cost for large files
4. State output location.
5. Ask for confirmation.

Example:

> I am about to transcribe `meeting-2024-03-15.m4a` using Whisper API. The audio content will be sent to OpenAI servers for processing. Output will be saved to `meeting-2024-03-15.m4a.txt`. Confirm?

---

## Output Policy

Allowed:
- "Transcription complete. Output saved to `audio.txt`."
- "Supported formats: m4a, mp3, wav, ogg, webm, mp4."

Disallowed:
- raw API key values
- sending transcripts to external endpoints
- full API response dumps with metadata

---

## Domain Notes

OpenAI Whisper API is an **external service** that processes raw audio data. Unlike text-based APIs, audio may contain unstructured sensitive information (private conversations, background audio, speaker identities) that the user may not fully be aware of. Every transcription sends the complete audio file externally, making privacy the primary safety concern.

---

## (Trigger, Task, Resources)

**Trigger:** Activate when the user requests audio transcription or speech-to-text processing via the OpenAI Whisper API, including use of the `transcribe.sh` script or batch audio processing.

**Task:** Evaluate each transcription request against credential-protection, privacy, and cost-control rules. BLOCK exposure of API keys, transmission of transcript output to external services, and unbounded batch transcription without an explicit file list. CONFIRM all transcription requests (since audio is sent externally), with heightened warnings for sensitive audio (meetings, calls, medical, legal), large files (> 25 MB or > 30 min), and custom prompts. ALLOW read-only operations such as viewing transcript output files and checking supported formats.

**Resources:** `references/risk-notes.md` — threat model and risk rationale. No auxiliary config or scripts required.

---

## References

- Original skill: `openai-whisper-api`
- `references/risk-notes.md`
