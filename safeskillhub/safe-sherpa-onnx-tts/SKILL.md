---
name: safe-sherpa-onnx-tts
description: Safe wrapper for the sherpa-onnx-tts skill. Use when generating speech audio from text locally via the sherpa-onnx offline CLI under strict output, path, and install constraints. Trigger when the user asks to convert text to speech, generate audio output, run TTS, or use sherpa-onnx-tts.
---

# Safe Sherpa-ONNX TTS

This skill adds a safety layer on top of `sherpa-onnx-tts`.

Use this skill whenever a task involves:
- `sherpa-onnx-tts`
- text-to-speech / TTS
- local audio generation
- speech synthesis
- downloading sherpa-onnx runtime or voice models

For command syntax, model selection, and platform-specific invocation, refer to the original `sherpa-onnx-tts` skill and official sherpa-onnx documentation.

---

## Safety Goals

This wrapper is designed to prevent:
1. overwriting existing audio files without user awareness
2. supply chain compromise via unverified runtime or model downloads
3. path traversal through manipulated `SHERPA_ONNX_RUNTIME_DIR` or `SHERPA_ONNX_MODEL_DIR` values
4. disk exhaustion from large model downloads or bulk audio generation
5. tampering with `openclaw.json` that could affect unrelated tools
6. execution of downloaded native binaries without user acknowledgement

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe operation

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Download runtime or model from a URL that is not an official sherpa-onnx GitHub release (`github.com/k2-fsa/sherpa-onnx/releases/`) | BLOCK | ST-B01 | Refuse; only official release URLs are trusted |
| Set `SHERPA_ONNX_RUNTIME_DIR` or `SHERPA_ONNX_MODEL_DIR` to a path outside the user's home directory or the designated tool directory | BLOCK | ST-B02 | Refuse; reject paths traversing to system directories |
| Overwrite an existing audio output file at the path specified by `-o` without explicit confirmation | BLOCK | ST-B03 | Refuse; require confirmation before overwriting |
| Modify `openclaw.json` to alter settings unrelated to sherpa-onnx env vars | BLOCK | ST-B04 | Refuse; config changes must be scoped to this tool only |
| Generate audio output to a system directory, a sensitive dotfile directory (~/.ssh, ~/.gnupg, ~/.aws, ~/.config), or any path outside the current working directory that is not an explicitly intended audio output location | BLOCK | ST-B05 | Refuse; output must target a safe, user-specified or current directory; sensitive dotfile directories are never valid audio output targets |
| Pipe, redirect, or stream TTS audio output to external commands, services, or network destinations | BLOCK | ST-B06 | Refuse; audio output must be written to a local file path only |
| Download and install the sherpa-onnx runtime binary for the current OS | CONFIRM | ST-C01 | Confirm target OS, download URL, and destination directory before proceeding |
| Download and install a voice model | CONFIRM | ST-C02 | Confirm model name, download URL, disk size estimate, and target directory |
| Update `openclaw.json` to set `SHERPA_ONNX_RUNTIME_DIR` or `SHERPA_ONNX_MODEL_DIR` | CONFIRM | ST-C03 | Confirm the exact key-value changes being written |
| Generate speech audio to a new file path with `-o` | CONFIRM | ST-C04 | Confirm output path, text content, and that no existing file will be overwritten |
| Generate speech audio in a bulk loop or batch over multiple text inputs | CONFIRM | ST-C05 | Require explicit confirmation of all output paths and estimated disk usage |
| Check installed runtime version or invoke `--help` / `--version` | ALLOW | ST-A01 | Allowed (no data written, no downloads) |
| List available model files in the configured model directory | ALLOW | ST-A02 | Allowed (read-only enumeration) |
| Preview or dry-run a TTS command without executing it | ALLOW | ST-A03 | Allowed |

---

## Required Operating Constraints

1. Only download runtime and model files from `https://github.com/k2-fsa/sherpa-onnx/releases/`.
2. Always confirm the output path before writing any `.wav` file; check whether a file already exists at that path.
3. Never write audio output to system directories, home directory root, or paths the user has not specified.
4. Always confirm `openclaw.json` changes before writing; limit changes to sherpa-onnx env var keys only.
5. Reject any `SHERPA_ONNX_RUNTIME_DIR` or `SHERPA_ONNX_MODEL_DIR` values that resolve outside the user's home directory.
6. Warn the user that downloaded runtime binaries are pre-compiled native code before proceeding with any install step.
7. Never pipe, redirect, or stream TTS output to external commands, services, or network destinations. Audio output must always be written to a local file path.

---

## Confirmation Workflow

For CONFIRM operations:

1. State the action being taken (download, generate audio, update config)
2. State the target path or URL
3. State the risk:
   - file overwrite (existing audio at output path)
   - supply chain (downloaded binary is native code from external URL)
   - disk usage (model/runtime size)
   - config change scope
4. Ask for confirmation

Example (audio generation):

> I am about to run `sherpa-onnx-tts -o ./tts.wav "Hello from local TTS."` No file currently exists at `./tts.wav`. The output will be saved locally. Confirm?

Example (runtime install):

> I am about to download the sherpa-onnx runtime for macOS from `https://github.com/k2-fsa/sherpa-onnx/releases/download/v1.12.23/sherpa-onnx-v1.12.23-osx-universal2-shared.tar.bz2` and extract it into `~/.openclaw/tools/sherpa-onnx-tts/runtime`. This is a pre-compiled native binary. Confirm?

---

## Output Policy

Allowed:
- "Audio saved to ./tts.wav"
- "sherpa-onnx-tts runtime v1.12.23 installed to ~/.openclaw/tools/sherpa-onnx-tts/runtime"
- "Model vits-piper-en_US-lessac-high extracted to ~/.openclaw/tools/sherpa-onnx-tts/models"

Disallowed:
- Dumping raw `.wav` binary or base64 audio content into chat
- Exposing internal directory structures beyond the tool's own directories
- Logging or displaying the full contents of `openclaw.json`

---

## Domain Notes

Sherpa-onnx-tts runs entirely offline with no API key required, which eliminates credential and cloud-privacy risks at runtime. The primary risk surfaces are: (1) **supply chain** — the install phase downloads a pre-compiled native binary and model weights from GitHub, requiring trust in the release provenance; (2) **file overwrite** — the `-o` flag silently overwrites existing `.wav` files; (3) **disk exhaustion** — voice models can be several hundred MB each, and bulk generation can consume significant storage. The env vars (`SHERPA_ONNX_RUNTIME_DIR`, `SHERPA_ONNX_MODEL_DIR`) are path references, not secrets, but manipulating them to point outside expected directories creates a path traversal risk.

---

## (Trigger, Task, Resources)

**Trigger:** Activate when the user requests text-to-speech generation, invokes `sherpa-onnx-tts`, asks to download or install the sherpa-onnx runtime or voice models, or modifies `SHERPA_ONNX_RUNTIME_DIR` / `SHERPA_ONNX_MODEL_DIR` environment variables.

**Task:** Classify each operation as BLOCK, CONFIRM, or ALLOW. Unconditionally BLOCK downloads from non-official URLs (only `github.com/k2-fsa/sherpa-onnx/releases/` is trusted), path traversal via runtime/model directory values pointing outside the user's home directory, overwriting existing audio files without confirmation, unscoped `openclaw.json` modifications, audio output to system directories or sensitive dotfile directories (~/.ssh, ~/.gnupg, ~/.aws, ~/.config), and piping/redirecting TTS output to external commands or network destinations. Require CONFIRM for runtime binary downloads, voice model installs, `openclaw.json` env var updates, audio generation to new file paths, and bulk/batch TTS operations. ALLOW version/help checks, model directory listing, and dry-run previews.

**Resources:** No auxiliary config or scripts required. References `references/risk-notes.md` for threat model rationale.

## References

- Original skill: `sherpa-onnx-tts`
- `references/risk-notes.md`
