---
name: safe-openai-whisper
description: Safe wrapper for the openai-whisper skill. Use when transcribing or translating audio files locally with the Whisper CLI under privacy, scope, and output constraints. Trigger when the user asks to transcribe audio, convert speech to text, translate audio, or use the whisper command.
---

# Safe OpenAI Whisper

This skill adds a safety layer on top of `openai-whisper`.

Use this skill whenever a task involves:
- `whisper`
- speech-to-text / transcription
- audio translation
- audio file processing

For command syntax and model options, refer to the original `openai-whisper` skill and official Whisper documentation.

---

## Safety Goals

This wrapper is designed to prevent:
1. transcription of unauthorized or sensitive audio (e.g., private conversations, recordings without consent)
2. leakage of transcription output containing sensitive content
3. uncontrolled output directory writes (overwriting important files)
4. excessive resource consumption from inappropriate model/file combinations
5. processing of files outside the user's intended scope

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe operation

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Transcribe audio files located outside the current working directory tree, unless the user explicitly specifies a path within a directory they own and the path does not resolve to a system or sensitive location (refined) | BLOCK | WH-B01 | Refuse; require explicit path within working scope |
| Write output to system directories (e.g., `/etc`, `/usr`, `/var`, `/opt`), home directory root (`~/`), or any path outside the current working directory tree without explicit user instruction providing a non-system target (refined) | BLOCK | WH-B02 | Refuse; output must target user-specified or current directory |
| Process audio files that appear to be recordings of third parties without stated consent context, including files described with terms such as "secretly recorded," "wiretapped," "obtained without permission," or similar indicators of non-consensual recording (refined) | BLOCK | WH-B03 | Refuse and note consent requirements |
| Send transcription output to external services, APIs, network endpoints, or pipe/redirect output to commands that perform network requests (e.g., `curl`, `wget`, `nc`) (refined) | BLOCK | WH-B04 | Refuse as data exfiltration risk |
| Batch-process a large number of audio files (>5) in a single operation, determined by the actual count of files listed or resolved, not the user's stated count (refined) | CONFIRM | WH-C01 | Require explicit confirmation of file list and output location |
| Use large models (large, large-v2, large-v3) on files >100 MB | CONFIRM | WH-C02 | Warn about resource consumption and confirm |
| Transcribe a single user-specified audio file (regardless of whether output directory is explicitly specified or defaults to the working directory) (refined) | CONFIRM | WH-C03 | Confirm file path, model, and output location |
| Translate audio (--task translate) or any request to convert audio from one language to text in another language (refined) | CONFIRM | WH-C04 | Confirm source file and target language intent |
| List available models, check whisper version/help, or ask informational questions about whisper capabilities (e.g., supported formats, options, features) (refined) | ALLOW | WH-A01 | Allowed (no data processed) |
| Dry-run or preview commands without execution, including generating command strings for review | ALLOW | WH-A02 | Allowed |
| Use `--model` flag with small/medium models on reasonable file sizes (<100 MB) | ALLOW | WH-A03 | Allowed as part of confirmed transcription |

---

## Required Operating Constraints

1. Always confirm the exact input file path before transcription.
2. Always confirm the output directory; default to current working directory.
3. Never transcribe files from system directories or paths the user hasn't specified.
4. Never output raw transcription content that may contain sensitive information without user awareness.
5. Prefer smaller models unless the user explicitly requests a larger one.
6. Limit batch operations and require explicit file listing.
7. Never pipe transcription output to external commands or services without confirmation.

---

## Confirmation Workflow

For CONFIRM operations:

1. State the input file path and size
2. State the model and task (transcribe/translate)
3. State the output format and directory
4. State the risk:
   - sensitive content in audio
   - resource consumption
   - output location safety
5. Ask for confirmation

Example:

> I am about to transcribe `/Users/you/meeting.mp3` using the medium model, outputting as txt to the current directory. This may produce text containing sensitive spoken content. Confirm?

---

## Output Policy

Allowed:
- "Transcription completed successfully, output saved to ./meeting.txt"
- "Whisper is installed and ready (model: medium)"

Disallowed:
- Full transcription dumps of potentially sensitive recordings in chat
- Raw audio file contents
- Credential or API key exposure from environment

---

## Domain Notes

Whisper runs entirely locally with no API key required, which reduces credential risk. However, the primary risk surface is **privacy**: audio files may contain private conversations, medical information, legal discussions, or other sensitive spoken content. Transcription output inherits the sensitivity of the source audio and must be treated accordingly.

---

## (Trigger, Task, Resources)

**Trigger:** Activate when the user requests audio transcription, speech-to-text conversion, audio translation, or any invocation of the `whisper` CLI — particularly when input files may contain private conversations or sensitive spoken content.

**Task:** Evaluate the transcription request against privacy, scope, and resource constraints. BLOCK operations that target files outside the working directory, write output to system paths, involve third-party recordings without consent context, or exfiltrate transcription data externally. CONFIRM single-file transcriptions (verifying file path, model, and output location), batch operations over 5 files, large-model usage on large files, and translation tasks. ALLOW read-only operations such as listing models, checking versions, and dry-run previews.

**Resources:** `references/risk-notes.md` (threat model and risk rationale). No auxiliary config or scripts required.

---

## References

- Original skill: `openai-whisper`
- `references/risk-notes.md`
