# Risk Notes for safe-songsee

## Threat Model Summary

Songsee is a CLI tool that processes audio files and generates spectrogram visualizations. Because it accepts file paths and arguments that are passed to shell execution, it presents risks of command injection, arbitrary file access, and resource exhaustion from large file processing.

## Key Risks

### 1. Command Injection
Crafted filenames or arguments containing shell metacharacters could execute arbitrary commands when passed to the songsee CLI.

Mitigation:
- sanitize and quote all file paths
- reject inputs with shell metacharacters

---

### 2. Arbitrary File Access
The tool could be used to probe or process files outside the user's intended scope, including system files.

Mitigation:
- validate file paths against user-accessible directories
- require explicit user-provided paths

---

### 3. Resource Exhaustion
Processing very large audio files can consume significant CPU, memory, and disk space.

Mitigation:
- confirm before processing large files (>500MB)
- confirm batch processing operations

---

### 4. Sensitive Path Writes
Output could be directed to system-critical directories, potentially overwriting important files.

Mitigation:
- block writes to system directories
- confirm writes outside the current working directory

---

### 5. Stdin Abuse
The stdin piping mode (`cat file | songsee -`) could be used to feed arbitrary data to the tool.

Mitigation:
- block piping non-audio data through stdin
- validate source of piped input

---

## Safe vs Unsafe

Safe:
- generating spectrograms from local audio files
- adjusting visualization settings (style, size, panels)
- time-slicing audio for focused visualization

Confirm:
- processing very large audio files
- writing output outside current directory
- batch processing multiple files

Block:
- filenames with shell metacharacters
- writing to system directories
- piping arbitrary data through stdin
