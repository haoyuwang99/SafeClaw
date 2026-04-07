# Risk Notes for safe-video-frames

## Threat Model Summary

The `video-frames` skill wraps ffmpeg to extract single frames or thumbnails from video files. While the skill itself is narrowly scoped, ffmpeg is an extremely powerful tool with a broad attack surface including network access, arbitrary filters, and shell execution vectors.

## Key Risks

### 1. Command Injection via ffmpeg Arguments
Risk:
- ffmpeg accepts complex filter chains, network URLs as input/output, and pipe commands.
- An adversarial prompt could construct ffmpeg invocations that execute arbitrary commands or access network resources.

Mitigation:
- Only allow execution through the provided `frame.sh` script.
- Block raw ffmpeg command construction.

### 2. Unauthorized File Access
Risk:
- ffmpeg can read any file the user has access to, including sensitive video files not intended for processing.

Mitigation:
- Only operate on files explicitly named by the user.
- Block glob patterns or directory-level operations.

### 3. File Overwrite
Risk:
- Writing output to an existing file path could destroy user data.

Mitigation:
- Confirm before writing to any path that may contain existing files.

### 4. Bulk Extraction / Disk Exhaustion
Risk:
- Extracting many frames from a long video could fill disk space rapidly.
- A loop over timestamps could generate thousands of files.

Mitigation:
- Block bulk extraction unless user specifies exact count.
- Default to single-frame extraction.

### 5. Media Exfiltration
Risk:
- Extracted frames could be sent to external services if combined with other tools.

Mitigation:
- Block any external transmission of extracted media.

## Safe vs Unsafe

Safe:
- Extract a single frame to /tmp
- Choose jpg vs png output format
- Use --time for a specific timestamp

Confirm:
- Extract frame (confirm paths)
- Write to a location that may overwrite

Block:
- Raw ffmpeg commands
- Network URLs as input/output
- Bulk extraction loops
- Sending frames externally
