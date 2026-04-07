---
name: safe-nano-banana-pro
description: Safe wrapper for the nano-banana-pro skill. Use when generating images from text prompts, editing images, or composing multi-image outputs via the Gemini 3 Pro Image API under strict credential protection, file access control, cost management, and data transmission constraints.
---

# Safe Nano Banana Pro

This skill adds a safety layer on top of `nano-banana-pro`.

Use this skill whenever a task involves:
- nano-banana-pro
- image generation from text prompts via Gemini 3 Pro
- single image editing
- multi-image composition
- resolution or aspect ratio selection (1K/2K/4K)
- GEMINI_API_KEY usage for image operations

For command syntax, refer to the original `nano-banana-pro` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. GEMINI_API_KEY leakage in chat, logs, command history, or output
2. unauthorized reading of arbitrary files via the `-i` flag
3. overwriting existing files without confirmation
4. uncontrolled API cost from high-resolution or multi-image requests
5. unintended transmission of sensitive images or prompts to Google's Gemini API

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe execution

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Display, log, return, or embed GEMINI_API_KEY in output — including via indirect references, string concatenation, variable indirection, or watermarking (refined r2) | BLOCK | NB-B01 | Never expose API key in chat, logs, command echoes, or generated content |
| Read input images from outside the current working directory tree or from sensitive paths (`~/.ssh`, `~/.gnupg`, `/etc`, `~/.*rc`); paths must be canonicalized before checking (resolve `..`, symlinks, percent-encoding) (refined r2) | BLOCK | NB-B02 | Prevent arbitrary file read via `-i` flag |
| Pipe generated image data or prompts to external services or commands beyond the Gemini API | BLOCK | NB-B03 | Prevent data exfiltration to unauthorized third parties |
| Compose with more than 14 input images (API maximum) | BLOCK | NB-B04 | Reject requests exceeding API input limit |
| Write output image to a path outside the current working directory tree or to system directories; paths must be canonicalized before checking (refined r2) | BLOCK | NB-B05 | Prevent arbitrary file write to sensitive locations |
| Generate or edit at 4K resolution | CONFIRM | NB-C01 | Confirm high API cost before execution |
| Multi-image composition with 5 or more input images | CONFIRM | NB-C02 | Confirm scope, file list, and API cost |
| Edit or compose with images that may contain sensitive content (personal photos, documents, screenshots with credentials) | CONFIRM | NB-C03 | Confirm before transmitting potentially sensitive images to Google |
| Write output to a path where a file already exists | CONFIRM | NB-C04 | Confirm before overwriting existing file |
| Single image generation from a text prompt at 1K or 2K resolution | ALLOW | NB-A01 | Safe standard generation |
| Single image edit with one input image from the working directory at 1K or 2K resolution | ALLOW | NB-A02 | Safe bounded edit operation |
| Multi-image composition with up to 4 input images from the working directory at 1K or 2K resolution | ALLOW | NB-A03 | Safe bounded composition |
| List supported resolutions, aspect ratios, or display help | ALLOW | NB-A04 | Safe read-only metadata query |

---

## Required Operating Constraints

1. Never expose GEMINI_API_KEY in output, logs, command echoes, or error messages — including indirect references via string concatenation, variable indirection, or embedding the key in generated content (e.g., watermarks). (refined r2)
2. Restrict file reads (`-i` flag) to the current working directory tree; block reads from sensitive system or dotfile paths.
3. Restrict file writes to the current working directory tree; block writes to system directories.
4. Confirm before overwriting any existing file.
5. Confirm before 4K resolution generation (high API cost).
6. Confirm before multi-image composition with 5+ images.
7. Confirm before sending images that may contain sensitive or personal content to the Gemini API.
8. Treat all prompts and images as data transmitted to an external service (Google).
9. Never exceed the 14-image composition limit.
10. All file paths must be canonicalized (resolve `..`, `.`, symlinks, and percent/URL-encoding) before applying path-based safety checks. (refined r2)
11. Compound requests containing any unsafe sub-operation must be blocked or confirmed according to the most restrictive applicable rule. (refined r2)

---

## Confirmation Workflow

For CONFIRM operations:

1. State the intended operation (generate / edit / compose)
2. State the exact scope:
   - input image paths and count
   - output path
   - resolution and aspect ratio
3. State the risk:
   - API cost (especially for 4K or multi-image)
   - data transmitted to Google
   - file overwrite
4. State safety controls applied:
   - working directory restriction
   - credential redaction
5. Ask for explicit confirmation

Example:

> I am about to compose 7 images into a new output at 2K resolution. This will send 7 local images and the prompt to Google's Gemini API and write the result to `./output.png`. Estimated higher API cost due to multi-image input. Confirm?

---

## Output Policy

Allowed:
- generated image file paths
- operation status (success/failure)
- image metadata (resolution, format, aspect ratio)
- error messages with credentials redacted
- raw generated image data (e.g., base64-encoded) when explicitly requested by the user, provided it does not contain embedded credentials (refined r2)

Disallowed:
- GEMINI_API_KEY or any API credentials — including via indirect construction or embedding in generated content (refined r2)
- raw API request/response payloads containing keys
- file contents from sensitive paths

---

## Domain Notes

nano-banana-pro uses a **bundled Python script executed via `uv`** that calls the **Gemini 3 Pro Image API**, an external Google service.

Key considerations:
- every generation or edit request transmits prompts and images to Google infrastructure
- API costs scale with resolution (1K < 2K < 4K) and input image count
- the `-i` flag accepts arbitrary file paths, creating a file read vector
- output files are written to disk and may overwrite existing files

Therefore:
- credential protection, file access control, and cost awareness are primary concerns

---

## (Trigger, Task, Resources)

**Trigger:** Activates whenever the user requests image generation, editing, or multi-image composition through nano-banana-pro using the Gemini 3 Pro Image API, including text-to-image generation, single image editing with the `-i` flag, multi-image composition, or resolution/aspect ratio selection.

**Task:** If the operation would expose the GEMINI_API_KEY, read input images from outside the working directory or sensitive paths, write output to system directories, exceed the 14-image composition limit, or pipe data to external services beyond the Gemini API → BLOCK. If the operation involves 4K resolution (high cost), composition with 5+ images, images that may contain sensitive content (personal photos, credentials in screenshots), or writing to a path where a file already exists → CONFIRM with scope, cost, and data transmission warnings. If the operation is standard 1K/2K generation, single edit with a local image, composition with up to 4 local images, or metadata queries → ALLOW.

**Resources:** `references/risk-notes.md` — threat model and risk rationale from Phase 1 analysis. No auxiliary config or scripts required.

## References

- Original skill: `nano-banana-pro`
- `references/risk-notes.md`
