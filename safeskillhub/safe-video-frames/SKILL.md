---
name: safe-video-frames
description: Safe wrapper for the video-frames skill. Use when extracting frames or thumbnails from video files using ffmpeg under strict path, scope, and output constraints. Trigger when the user asks to extract frames, create thumbnails, or use ffmpeg for frame capture.
---

# Safe Video Frames

This skill adds a safety layer on top of `video-frames`.

Use this skill whenever a task involves:
- extracting frames from video files
- creating thumbnails from video
- `ffmpeg` frame capture
- `frame.sh` script usage

For command syntax, refer to the original `video-frames` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. arbitrary command injection via ffmpeg arguments
2. reading video files outside user-intended scope
3. overwriting existing files without consent
4. excessive disk usage from bulk frame extraction
5. exfiltration of extracted frames to external services

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe operation

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Inject shell commands or arbitrary ffmpeg flags beyond frame extraction | BLOCK | VF-B01 | Refuse any ffmpeg usage beyond single-frame or thumbnail extraction |
| Extract frames from files outside the user-specified path | BLOCK | VF-B02 | Refuse access to paths not explicitly provided by the user |
| Send or upload extracted frames to external services, URLs, or APIs, or write them to cloud-synced directories or network-mounted paths (refined r2) | BLOCK | VF-B03 | Refuse all external transmission of extracted media, including indirect exfiltration via cloud-sync folders (Google Drive, Dropbox, OneDrive, iCloud) or network mounts |
| Bulk extraction of many frames without explicit user request | BLOCK | VF-B04 | Refuse batch/loop extraction unless user specifies exact count and purpose |
| Extract one or more frames from a video file (new extraction) (refined) | CONFIRM | VF-C01 | Confirm input file, timestamp(s), and output path(s) before executing. Applies to ALL new frame extractions regardless of whether paths are explicitly specified. For multi-frame requests with exact count, a single consolidated confirmation listing all timestamps is acceptable. |
| Write output to a path that already contains an existing file | CONFIRM | VF-C02 | Warn about overwrite and require confirmation |
| Proceed with extraction after VF-C01 confirmation has been granted (refined) | ALLOW | VF-A01 | Safe to execute once the user has confirmed input path, output path, and timestamp via the confirmation workflow |
| Use `--time` flag for timestamp-based extraction | ALLOW | VF-A02 | Safe parameter for targeted extraction |
| Choose output format (`.jpg` or `.png`) | ALLOW | VF-A03 | Safe format selection |

### Rule Precedence

When multiple rules match a single request, apply them in this order:

1. **BLOCK rules (VF-B01 through VF-B04) always take highest precedence.** If any BLOCK rule matches, the operation is refused regardless of other matching rules.
2. **CONFIRM rules (VF-C01, VF-C02) take precedence over ALLOW rules.** Any new frame extraction triggers VF-C01 confirmation before VF-A01 can apply. VF-A01 only governs the execution step after confirmation.
3. **ALLOW rules (VF-A01 through VF-A03) apply to post-confirmation execution or non-extraction parameter selections** (e.g., choosing a format or flag).

---

## Required Operating Constraints

1. Only invoke ffmpeg through the provided `frame.sh` script.
2. Never construct raw ffmpeg commands with user-supplied arguments.
3. Only operate on files explicitly named by the user.
4. Confirm output path before writing.
5. Never extract frames in a loop or batch without explicit count.
6. Never send extracted frames externally, including to cloud-synced folders or network mounts.
7. Prefer `/tmp` or user-specified directories for output.

---

## Confirmation Workflow

For CONFIRM operations:

1. State the input video file path
2. State the timestamp (or "first frame" if none)
3. State the output file path and format
4. State risk:
   - file overwrite
   - disk usage
5. Ask for confirmation

Example:

> I am about to extract a frame at 00:00:10 from `/path/to/video.mp4` and save it to `/tmp/frame-10s.jpg`. This will create a new file at that location. Confirm?

---

## Output Policy

Allowed:
- "Frame extracted successfully to /tmp/frame.jpg"
- "Thumbnail created at the specified path."

Disallowed:
- raw image data in chat
- base64-encoded frame content
- bulk extraction status dumps

---

## Domain Notes

ffmpeg is a powerful multimedia tool with a vast command surface. This wrapper restricts usage strictly to single-frame extraction via the provided script, preventing the broader ffmpeg attack surface (filters, network streams, arbitrary encoding) from being accessible.

---

## (Trigger, Task, Resources)

**Trigger:** Activate when the user requests frame extraction, thumbnail creation, or any ffmpeg-based frame capture operation, including direct invocation of the `frame.sh` script.

**Task:** Validate every frame extraction request against path, scope, and output constraints. BLOCK operations that involve shell injection via ffmpeg arguments, access to files outside user-specified paths, external transmission of extracted frames, or unrequested bulk extraction. CONFIRM all new frame extractions — regardless of whether paths are explicitly specified — by presenting the input file, timestamp(s), and output path(s) for user approval; also warn before overwriting existing files. After the user confirms, ALLOW execution. ALLOW non-extraction parameter selections (format choice, --time flag) without additional confirmation.

**Resources:** `references/risk-notes.md` — threat model and risk rationale for the video-frames skill. No auxiliary config or scripts required.

---

## References

- Original skill: `video-frames`
- `references/risk-notes.md`
