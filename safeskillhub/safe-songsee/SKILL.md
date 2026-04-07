---
name: safe-songsee
description: Safe wrapper for the songsee skill. Use when generating spectrograms and audio visualizations with the songsee CLI under strict constraints preventing command injection, arbitrary file access, and resource exhaustion. Trigger when the user asks to visualize audio, generate spectrograms, or use songsee.
---

# Safe Songsee

This skill adds a safety layer on top of `songsee`.

Use this skill whenever a task involves:
- generating spectrograms from audio files
- creating multi-panel audio visualizations
- using the `songsee` CLI tool
- processing audio for visual analysis

For CLI usage, flags, and visualization types, refer to the original `songsee` skill.

## Safety Goals

This wrapper is designed to prevent:
1. command injection via crafted filenames or arguments
2. reading or processing files outside the user's intended scope
3. resource exhaustion from processing very large files
4. writing output to sensitive or system-critical paths
5. arbitrary file access through stdin piping patterns

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe execution

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Filenames or arguments containing shell metacharacters (`;`, `&&`, `|`, `$()`, backticks) | BLOCK | SS-B01 | Refuse; sanitize input before execution |
| Writing output to system directories (`/etc`, `/usr`, `/System`, `/var`) | BLOCK | SS-B02 | Refuse; output must go to user-accessible paths only |
| Processing files outside the current working directory or user-specified paths without explicit path | BLOCK | SS-B03 | Refuse; require explicit user-provided file paths |
| Piping arbitrary non-audio data through stdin | BLOCK | SS-B04 | Refuse; stdin input must be from a known audio source |
| Encoded or obfuscated inputs that decode to shell metacharacters or malicious payloads (URL-encoding, base64, unicode escapes) (refined r2) | BLOCK | SS-B05 | Refuse; normalize/decode all inputs before applying safety checks |
| Invalid numeric parameter values: negative/zero --width or --height, negative --start, zero/negative --duration, or extreme values (>10000) (refined r2) | BLOCK | SS-B06 | Refuse; dimensions must be positive integers (1-10000), --start must be non-negative, --duration must be positive |
| Chained or compound operations beyond songsee scope (e.g., file copy, email, shell commands, EXIF editing) requested alongside a songsee command (refined r2) | BLOCK | SS-B07 | Refuse the out-of-scope operation; only execute the songsee portion if it passes all safety checks |
| Processing very large audio files (>500MB) | CONFIRM | SS-C01 | Warn about resource usage and confirm |
| Writing output to paths outside the current working directory | CONFIRM | SS-C02 | Show the output path and confirm |
| Processing multiple files in batch | CONFIRM | SS-C03 | Show file list and confirm scope |
| Generating a spectrogram from a local audio file | ALLOW | SS-A01 | Safe standard operation |
| Using `--viz` to select visualization panels | ALLOW | SS-A02 | Safe; controls rendering only |
| Adjusting `--style`, `--width`, `--height`, FFT settings | ALLOW | SS-A03 | Safe; cosmetic parameters |
| Using `--start` and `--duration` for time slicing | ALLOW | SS-A04 | Safe; limits processing scope |
| Specifying output format (jpg/png) | ALLOW | SS-A05 | Safe; format selection only |

## Required Operating Constraints

1. Always quote filenames to prevent shell injection.
2. Never write output to system-critical directories.
3. Validate that input files exist and are audio files before processing.
4. Confirm before processing very large files.
5. Never execute songsee with unsanitized user-provided arguments.
6. Prefer explicit output paths over defaults for clarity.

## Input Sanitization Policy

Before constructing any songsee command:
- Quote all file paths with double quotes
- Reject filenames containing `;`, `&&`, `||`, `|`, `$(`, `` ` ``, `>`, `<`
- Decode and normalize all inputs (URL-encoding, base64, unicode escapes) before checking for metacharacters (refined r2)
- Validate `--start` is a non-negative numeric value (refined r2)
- Validate `--duration` is a positive numeric value (refined r2)
- Validate `--width` and `--height` are positive integers in range 1-10000 (refined r2)
- Reject any request to perform operations outside songsee's scope (file manipulation, network operations, arbitrary shell commands) (refined r2)

## Output Policy

Allowed:
- spectrogram images in user-accessible directories
- visualization grids
- sliced audio visualizations

Disallowed:
- output written to system directories
- command output containing injected shell results

## (Trigger, Task, Resources)

**Trigger:** Activate when the user asks to generate spectrograms, create audio visualizations, or invoke the `songsee` CLI tool to process audio files.

**Task:** Inspect the songsee command and its arguments against the safety rules. BLOCK if filenames or arguments contain shell metacharacters (including after decoding encoded forms), if output targets system-critical directories, if input files are outside user-accessible paths, if arbitrary non-audio data is piped through stdin, if numeric parameters are invalid or extreme, or if the user requests operations outside songsee's scope (refined r2). CONFIRM before processing very large files (>500MB), writing output outside the current working directory, or batch-processing multiple files. ALLOW standard spectrogram generation from local audio files with safe cosmetic and slicing parameters.

**Resources:** No auxiliary resources required.

## References

- Original skill: `songsee`
- `references/risk-notes.md`
