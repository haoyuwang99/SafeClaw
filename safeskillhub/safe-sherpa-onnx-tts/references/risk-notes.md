# Risk Notes for safe-sherpa-onnx-tts

## Threat Model Summary

sherpa-onnx-tts is an offline text-to-speech CLI that synthesises speech from text and writes `.wav` files to disk. The install phase downloads a pre-compiled native runtime binary and ONNX voice model weights from GitHub releases. At runtime there is no network activity and no API key is required. The tool is configured via two env vars pointing to local directories.

## Action Space

- **read**: Model directory files (`.onnx`, tokens, data), runtime binary, `openclaw.json`
- **write**: Audio output files (`.wav`) via `-o` flag; `openclaw.json` env var entries during install
- **destructive**: Overwriting existing `.wav` files silently when `-o` points to an existing path; overwriting config entries in `openclaw.json`
- **external**: Downloading runtime binaries and model archives from `github.com/k2-fsa/sherpa-onnx/releases/` during the install phase only; no network activity at runtime
- **credential**: `SHERPA_ONNX_RUNTIME_DIR` and `SHERPA_ONNX_MODEL_DIR` are filesystem path references (not secrets), but manipulating them can affect tool behaviour

## Key Risks

### 1. Supply Chain — Pre-Compiled Native Binary and Model Weights
- **Risk**: The runtime is a pre-compiled native binary downloaded from an external URL. A compromised release or a URL substitution could result in arbitrary code execution. Model weight files could similarly be replaced with adversarial inputs.
- **Category**: External interaction, Privilege escalation
- **Trigger**: Any install step that downloads `sherpa-onnx-v*.tar.bz2` or a model archive.
- **Mitigation**: Only allow downloads from the canonical `github.com/k2-fsa/sherpa-onnx/releases/` URL prefix. Confirm each download with the user before execution, explicitly noting that a native binary will be installed.

### 2. File Overwrite — Silent Clobber via `-o` Flag
- **Risk**: The `-o` flag writes the output `.wav` without checking for an existing file. An agent invoking TTS in a loop or with a predictable output path could silently destroy existing recordings or project files.
- **Category**: Irreversibility
- **Trigger**: Running `sherpa-onnx-tts -o <path>` where `<path>` already exists.
- **Mitigation**: Check whether the output path already exists before executing. Require explicit user confirmation if a file would be overwritten; BLOCK unconditional overwrites.

### 3. Path Traversal — Manipulated Env Var Paths
- **Risk**: If `SHERPA_ONNX_RUNTIME_DIR` or `SHERPA_ONNX_MODEL_DIR` are set to unexpected paths (e.g., `/etc`, `/usr/local/bin`, or `../../sensitive`), the tool could read from or write to unintended system locations.
- **Category**: Privilege escalation
- **Trigger**: Setting either env var to a path outside `~/.openclaw/tools/sherpa-onnx-tts/` or the user's home directory.
- **Mitigation**: Validate both env var values resolve within the user's home directory before accepting them. Block any values containing `..` components or resolving outside expected boundaries.

### 4. Config Tampering — `openclaw.json` Writes
- **Risk**: The install phase writes env vars into `openclaw.json`, which is a shared configuration file for all OpenClaw tools. Incorrect or malicious writes could break other tools or inject unexpected paths.
- **Category**: Scope explosion
- **Trigger**: Any modification to `openclaw.json` beyond the two sherpa-onnx env var keys.
- **Mitigation**: Confirm all `openclaw.json` changes before writing. Restrict edits strictly to `SHERPA_ONNX_RUNTIME_DIR` and `SHERPA_ONNX_MODEL_DIR` keys.

### 5. Disk Exhaustion — Large Model Downloads and Bulk Generation
- **Risk**: Voice model archives can be several hundred MB each. Downloading multiple models or running TTS in a batch over large text corpora can exhaust available disk space.
- **Category**: Scope explosion
- **Trigger**: Downloading multiple model archives; running TTS in a loop over many inputs without output-size awareness.
- **Mitigation**: Warn on model download with estimated size. Require confirmation for bulk generation. Limit batch scope explicitly.

### 6. Output Written Outside Working Scope
- **Risk**: An agent could specify an absolute output path outside the user's working directory, writing audio files to unexpected locations.
- **Category**: Irreversibility, Scope explosion
- **Trigger**: `-o /tmp/...`, `-o /System/...`, or any absolute path not under the current project or user-approved directory.
- **Mitigation**: Block output paths that resolve outside the current working directory or a user-specified directory.

## Safe vs Unsafe

Safe:
- Checking `sherpa-onnx-tts --help` or `--version`
- Listing model files in the configured model directory
- Dry-running or previewing TTS commands

Confirm:
- Downloading the runtime binary for any OS
- Downloading any voice model archive
- Updating `openclaw.json` with env var paths
- Generating audio output to a new file
- Batch TTS generation over multiple inputs

Block:
- Downloading from URLs outside the official sherpa-onnx GitHub releases
- Overwriting an existing `.wav` file without confirmation
- Writing output to system directories or outside working scope
- Setting env vars to paths outside the user's home directory
- Modifying `openclaw.json` keys beyond the two designated sherpa-onnx vars
