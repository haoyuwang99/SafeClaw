# Risk Notes for safe-openai-whisper

## Threat Model Summary

openai-whisper is a local speech-to-text CLI that processes audio files and writes transcription output to disk. No network calls or API keys are required, but it handles potentially sensitive audio content.

## Action Space

- **read**: Audio files from local filesystem
- **write**: Transcription output files (txt, srt, vtt, json, tsv) to specified output directory
- **destructive**: Overwriting existing output files in target directory
- **external**: None (fully local processing)
- **credential**: None (no API key needed)

## Key Risks

### 1. Privacy — Sensitive Audio Content
Audio files may contain private conversations, medical information, legal discussions, or confidential business meetings.

Mitigation:
- Confirm before transcribing any file
- Do not dump full transcription output into chat
- Treat output with same sensitivity as source audio

### 2. Scope Explosion — Batch Processing
Glob patterns or directory-level processing could inadvertently transcribe many files.

Mitigation:
- Require explicit file listing for batch operations
- Confirm scope for >5 files

### 3. Irreversibility — Output Overwrites
Writing output to directories may overwrite existing files.

Mitigation:
- Confirm output directory before writing
- Block writes to system or sensitive directories

### 4. Resource Consumption
Large models on large files can consume significant CPU/GPU and time.

Mitigation:
- Warn on large model + large file combinations
- Default to smaller models

### 5. Unauthorized Recordings
Processing recordings of third parties without consent raises ethical/legal concerns.

Mitigation:
- Block when consent context is unclear
- Note consent requirements in confirmation

## Safe vs Unsafe

Safe:
- Checking whisper availability
- Listing models
- Help/version commands

Confirm:
- Single file transcription
- Translation tasks
- Batch processing
- Large model usage

Block:
- Files outside working scope
- Output to system directories
- Exfiltrating transcription data
- Processing without consent context
