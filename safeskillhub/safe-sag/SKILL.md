---
name: safe-sag
description: Safe wrapper for the sag skill. Use when generating speech audio via the ElevenLabs TTS API under strict credential protection, cost control, content-safety, and file-write constraints. Trigger when the user asks to generate audio, convert text to speech, use sag, or play spoken output via ElevenLabs.
---

# Safe Sag

This skill adds a safety layer on top of `sag`.

Use this skill whenever a task involves:
- `sag` CLI
- ElevenLabs text-to-speech
- spoken audio generation or playback
- `ELEVENLABS_API_KEY` or `SAG_API_KEY`
- voice selection or voice listing via ElevenLabs

For command syntax, voice options, and model notes, refer to the original `sag` skill and the ElevenLabs documentation.

---

## Safety Goals

This wrapper is designed to prevent:
1. API key leakage (ELEVENLABS_API_KEY, SAG_API_KEY, ELEVENLABS_VOICE_ID)
2. exfiltration of sensitive or private text to the ElevenLabs cloud service
3. uncontrolled API cost from large or repeated TTS requests
4. generation of harmful, deceptive, or policy-violating audio content
5. overwriting existing audio files without user awareness

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe operation

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Expose or log `ELEVENLABS_API_KEY`, `SAG_API_KEY`, or `ELEVENLABS_VOICE_ID` in chat, files, or output | BLOCK | SG-B01 | Never expose credentials |
| Send text containing passwords, API keys, secrets, other credentials, or high-sensitivity personal data (SSNs, national ID numbers, credit card numbers, bank account numbers, passport numbers) to ElevenLabs TTS | BLOCK | SG-B02 (refined r2) | Refuse as credential exfiltration or regulatory risk |
| Generate audio with content that is hateful, sexually explicit, threatening, or illegal | BLOCK | SG-B03 | Refuse policy-violating content outright |
| Generate audio that impersonates a real person's voice for deceptive purposes | BLOCK | SG-B04 | Refuse deepfake / impersonation intent |
| Pipe TTS audio output to external services, upload endpoints, or network destinations | BLOCK | SG-B05 | Prevent data exfiltration |
| Write audio output to a system directory or any path outside the user's home directory or current working directory | BLOCK | SG-B06 (refined) | Prevent privilege-escalation and persistence attacks via output file placement |
| Generate TTS for text longer than ~500 words in a single call | CONFIRM | SG-C01 | Warn about API cost and confirm text scope |
| Overwrite an existing audio file with `-o` flag | CONFIRM | SG-C02 | Confirm destination path and acknowledge overwrite |
| Generate audio involving private, confidential, or personally identifiable information | CONFIRM | SG-C03 | Confirm user intent and recipient context |
| Use a non-default model (e.g. `eleven_multilingual_v2`, `eleven_flash_v2_5`) explicitly | CONFIRM | SG-C04 | Confirm model selection and any cost/quality implications |
| Generate audio for a long-form task (e.g. full article, chapter, script) | CONFIRM | SG-C05 | Confirm scope and estimated API usage before proceeding |
| List available voices (`sag voices`) | ALLOW | SG-A01 | Read-only metadata query; no text sent |
| Show prompting tips (`sag prompting`) | ALLOW | SG-A02 | Read-only; no API call |
| Generate TTS for a non-sensitive utterance under ~500 words to a new output file | ALLOW | SG-A03 (refined r2) | Allowed with standard safeguards |
| Preview or dry-run a command without execution | ALLOW | SG-A04 | Allowed |

---

## Required Operating Constraints

1. Never expose any API key or voice ID credential in chat, logs, or generated files.
2. Always review the text content before sending to ElevenLabs; refuse if it contains credentials, sensitive private data, or high-sensitivity personal data (SSNs, credit card numbers, bank account numbers, national ID numbers, passport numbers).
3. Confirm before generating TTS for text longer than ~500 words.
4. Confirm before overwriting an existing audio file at the `-o` destination path.
5. Refuse prompts designed to produce harmful, deceptive, or impersonating audio.
6. Never forward generated audio to external services or upload endpoints.
7. Confirm scope and cost for long-form generation tasks.
8. Default to the user-specified output path; do not silently redirect output.
9. Never write audio output to system directories (e.g. `/etc/`, `/usr/`, `/var/`, `/sys/`) or paths outside the user's home directory or current working directory.

---

## Confirmation Workflow

For CONFIRM operations:

1. State the text to be synthesised (truncate at ~50 words with "..." for long text)
2. State the voice name or ID and model
3. State the output destination (playback only or `-o` path)
4. State the risk:
   - estimated API cost for long text
   - sensitive content in text
   - file overwrite consequences
5. Ask for confirmation

Example:

> I am about to send ~800 words of text to ElevenLabs using voice "Clawd" (eleven_v3), saving output to `/tmp/narration.mp3`. This will consume significant API quota. Confirm?

---

## Output Policy

Allowed:
- "Audio generated and saved to /tmp/voice-reply.mp3"
- "Available voices listed; no API quota consumed"
- "sag is installed and ready"

Disallowed:
- API keys, voice IDs, or tokens in any response
- Raw audio data or base64-encoded audio in chat
- Full disclosure of private text content sent to ElevenLabs
- Confirmation that harmful or impersonating content was generated

---

## Domain Notes

`sag` is a thin CLI wrapper over the **ElevenLabs cloud TTS API**. Every generation call sends user-supplied text to ElevenLabs servers. This means:

- **Privacy**: any text passed to `sag` leaves the local machine; do not pass confidential or sensitive text.
- **Cost**: ElevenLabs billing is character-based; long or repeated calls can accumulate charges quickly.
- **Credential risk**: `ELEVENLABS_API_KEY` grants full ElevenLabs account access, not just TTS; protect it strictly.
- **Content policy**: ElevenLabs prohibits generation of harmful, deceptive, or voice-cloning content for impersonation; this wrapper enforces that boundary.

Voice confirmation before long output (as recommended by the original skill) is treated as a CONFIRM step here.

---

## (Trigger, Task, Resources)

**Trigger:** Activate when the user requests text-to-speech generation, invokes the `sag` CLI, references ElevenLabs TTS, or when any operation involves `ELEVENLABS_API_KEY`, `SAG_API_KEY`, or `ELEVENLABS_VOICE_ID`.

**Task:** Classify each operation as BLOCK, CONFIRM, or ALLOW. Unconditionally BLOCK exposure of API keys or voice ID credentials, sending credential-containing or high-sensitivity personal data (SSNs, credit card numbers, bank account numbers, national IDs, passport numbers) text to ElevenLabs, generating hateful/explicit/threatening/illegal audio content, voice impersonation for deceptive purposes, piping audio to external upload endpoints, and writing audio output to system directories or paths outside the user's home or current working directory. Require CONFIRM for text longer than ~500 words, overwriting existing audio files, synthesising private or PII-containing text, non-default model selection, and long-form generation tasks. ALLOW read-only operations (voice listing, prompting tips, dry-runs) and short non-sensitive utterances to new output files.

**Resources:** No auxiliary config or scripts required. References `references/risk-notes.md` for threat model rationale.

## References

- Original skill: `sag`
- `references/risk-notes.md`
- ElevenLabs API: https://elevenlabs.io/docs
