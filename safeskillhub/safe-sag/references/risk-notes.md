# Risk Notes for safe-sag

## Threat Model Summary

`sag` is a CLI wrapper over the ElevenLabs cloud TTS API. Every invocation (except `voices` and `prompting`) sends user-supplied text to ElevenLabs servers over the internet, incurring API quota consumption and exposing text content externally. The CLI requires an API key with full ElevenLabs account access.

## Action Space

```
Skill: sag
Actions:
  - read: list voices (sag voices), view prompting tips (sag prompting)
  - write: generate audio file to disk (-o flag), playback via local speaker
  - destructive: overwrite existing audio file at -o destination path
  - external: ElevenLabs TTS API (api.elevenlabs.io) — paid cloud service; every TTS call sends text externally
  - credential: ELEVENLABS_API_KEY (primary), SAG_API_KEY (alternate), ELEVENLABS_VOICE_ID / SAG_VOICE_ID (voice selection)
```

## Key Risks

### 1. Credential Exposure

`ELEVENLABS_API_KEY` and `SAG_API_KEY` grant full ElevenLabs account access, not just TTS. Exposure in chat, logs, or generated files would allow account takeover and billing abuse.

Mitigation:
- never expose any key or voice ID in chat, logs, or output files
- refuse requests that involve echoing or logging credential values

---

### 2. Text Exfiltration to External Service

Every TTS generation call transmits the full text to ElevenLabs cloud servers. Text containing passwords, secrets, confidential business data, personal information, or internal documents must not be sent.

Mitigation:
- review text content before generation
- block text that contains credentials or secrets
- confirm before sending text with potentially sensitive personal or confidential content

---

### 3. API Cost Explosion

ElevenLabs charges per character synthesised. Long texts, batch calls, or repeated generation of large scripts can accumulate significant charges without the user realising.

Mitigation:
- confirm generation of text longer than ~500 words
- confirm long-form tasks (articles, chapters, scripts) before proceeding
- surface estimated scope to the user before execution

---

### 4. Harmful or Deceptive Audio Content

The CLI passes text directly to a highly realistic TTS engine. This could be used to generate threatening audio, hate speech, or audio that impersonates real people's voices for deceptive purposes.

Mitigation:
- block content that is hateful, sexually explicit, threatening, or illegal
- block content intended to impersonate real individuals deceptively

---

### 5. Data Exfiltration via Audio Output

Generated audio files could be forwarded to external upload endpoints, cloud storage, or messaging services, exfiltrating the synthesised content.

Mitigation:
- block piping or forwarding of audio to external network destinations
- confirm any downstream handling of generated audio files

---

### 6. File Overwrite

The `-o` flag writes to an arbitrary filesystem path. An existing audio file at that path is silently overwritten by default.

Mitigation:
- confirm before overwriting an existing file at the `-o` destination

---

## Safe vs Unsafe

Safe (ALLOW):
- `sag voices` — metadata query only, no text sent
- `sag prompting` — local read-only operation
- short, non-sensitive utterance (<100 words) to a new output file

Confirm (CONFIRM):
- text longer than ~500 words
- overwriting an existing `-o` destination file
- text involving private or personally identifiable content
- non-default model selection
- long-form generation tasks

Block (BLOCK):
- exposing API keys or voice IDs
- sending text containing credentials or secrets to the API
- generating hateful, explicit, threatening, or illegal content
- generating audio to impersonate real people deceptively
- forwarding audio output to external services or upload endpoints
