---
name: safe-canvas
description: Safe wrapper for the canvas skill. Use when displaying HTML content on connected OpenClaw nodes under strict content safety, JavaScript execution, and navigation constraints. Trigger when the user asks to present, navigate, evaluate JS, snapshot, or hide canvas content on connected nodes.
---

# Safe Canvas

This skill adds a safety layer on top of `canvas`.

Use this skill whenever a task involves:
- canvas / HTML display on OpenClaw nodes
- presenting web content on Mac/iOS/Android nodes
- executing JavaScript in canvas WebViews
- navigating canvas to new URLs
- taking canvas snapshots

For action syntax, configuration, and normal product behavior, refer to the original `canvas` skill.

## Safety Goals

This wrapper is designed to prevent:
1. arbitrary JavaScript execution in connected node WebViews
2. navigation to malicious or external URLs
3. loading untrusted remote content on user devices
4. exfiltration of canvas snapshots
5. unauthorized content display on nodes the user did not target

## Enforcement Model

Actions are classified into three levels:

- `BLOCK`   — refuse outright
- `CONFIRM` — require explicit user approval
- `ALLOW`   — permitted without intervention

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| `eval` with JavaScript that accesses local storage, cookies, filesystem, or fetches external URLs | BLOCK | CV-B01 | Prevent data exfiltration and unauthorized network access from WebView |
| Navigate to URL outside the canvas host (`/__openclaw__/canvas/` prefix) | BLOCK | CV-B02 | Prevent loading arbitrary external web content on user devices |
| Present or navigate to `file://` or non-HTTP(S) scheme URLs | BLOCK | CV-B03 | Prevent local filesystem access from WebView |
| Write HTML files containing `<script>` tags that fetch from external domains | BLOCK | CV-B04 | Prevent injection of external scripts into canvas content |
| Write HTML files containing any element that loads external resources (`<iframe>`, `<object>`, `<embed>`, `<link rel="import">`, `<meta http-equiv="refresh">` with external URLs, or inline JS that dynamically creates external-loading elements) | BLOCK | CV-B06 | Prevent loading untrusted remote content via non-script HTML elements (refined r2) |
| `eval` with JavaScript that uses encoding, obfuscation, or string manipulation to construct dangerous API calls (e.g., `atob()`, string concatenation to build `localStorage`/`document.cookie`, nested `eval()`) | BLOCK | CV-B07 | Prevent obfuscated payloads from bypassing keyword-based detection (refined r2) |
| Navigate to a URL or write to a file path containing path traversal sequences (`../`) — apply after normalization | BLOCK | CV-B08 | Prevent path traversal to escape the canvas root or `/__openclaw__/canvas/` prefix (refined r2) |
| Send canvas snapshots to external services, chat, or network endpoints | BLOCK | CV-B05 | Prevent screenshot exfiltration |
| Present HTML content on a specific node | CONFIRM | CV-C01 | Confirm target node, content file, and URL before displaying |
| Navigate canvas to a new URL within the canvas host | CONFIRM | CV-C02 | Confirm target node and destination URL |
| Execute JavaScript via `eval` (read-only, no external access) | CONFIRM | CV-C03 | Show exact JS code to be executed; confirm before running |
| Take canvas snapshot | CONFIRM | CV-C04 | Confirm target node; output stays local |
| Write or modify HTML files in the canvas root directory | CONFIRM | CV-C05 | Confirm file path and content summary before writing |
| Hide canvas on a node | ALLOW | CV-A01 | Non-destructive; removes displayed content |
| List connected nodes (`openclaw nodes list`) | ALLOW | CV-A02 | Read-only node enumeration |
| Read canvas host configuration | ALLOW | CV-A03 | Read-only config inspection |

## Required Operating Constraints

1. Never execute JavaScript that accesses cookies, local storage, or makes external network requests.
2. Only navigate to URLs within the `/__openclaw__/canvas/` path on the configured canvas host.
3. Never load content from external domains or `file://` URLs.
4. Always confirm the target node before presenting or navigating.
5. Show exact JavaScript code before any `eval` execution.
6. Keep canvas snapshots local; never transmit externally.
7. Validate that HTML content does not contain external script references before writing to canvas root.
8. Validate that HTML content does not contain any elements that load external resources — including `<iframe>`, `<object>`, `<embed>`, `<link rel="import">`, and `<meta http-equiv="refresh">` pointing to external URLs. (refined r2)
9. Analyze JavaScript payloads semantically before eval: decode base64 (`atob`), resolve string concatenation, and unwrap nested `eval()` calls to detect obfuscated access to dangerous APIs. (refined r2)
10. Normalize all URL paths and file paths before validation — reject any containing `../` traversal sequences that would resolve outside the allowed prefix or canvas root directory. (refined r2)

## URL Safety Policy

Allow only URLs matching this pattern:
- `http://<configured-host>:18793/__openclaw__/canvas/<path>`

Block any URL that:
- Points to a domain other than the configured canvas host
- Uses `file://`, `javascript:`, `data:`, or other non-HTTP(S) schemes
- Does not include the `/__openclaw__/canvas/` path prefix
- Contains `../` path traversal sequences that, after normalization, resolve outside `/__openclaw__/canvas/` (refined r2)

## Confirmation Workflow

For any `CONFIRM` operation, follow this exact flow:

1. State the target node (ID and name).
2. State the action (present / navigate / eval / snapshot / write).
3. State the content:
   - HTML file path or URL for present/navigate
   - exact JavaScript code for eval
   - file details for write
4. State the risk:
   - content will render on a real connected device
   - JavaScript executes in the device WebView
   - snapshots capture current visual state
5. Ask for explicit confirmation.

Example:

> I am about to present `snake.html` on node "mac-63599bc4" via URL `http://host:18793/__openclaw__/canvas/snake.html`. This will display content on the connected device's canvas. Confirm?

## Output Policy

Allowed:
- "Canvas presented on node 'mac-63599bc4'."
- "Canvas hidden."
- "Snapshot saved locally."

Disallowed:
- loading external web content on user devices
- executing arbitrary JavaScript without preview
- sending snapshots to external services

## Domain Notes

The canvas skill renders HTML content in **WebViews on connected user devices** (Mac, iOS, Android). The `eval` action executes arbitrary JavaScript in these WebViews, posing data exfiltration and code execution risks. Navigation to external URLs could expose connected devices to malicious web content. Content served through the canvas host should be self-contained and limited to the local canvas root directory.

## (Trigger, Task, Resources)

**Trigger:** Activates when the user requests any canvas action on connected OpenClaw nodes — presenting HTML, navigating to URLs, executing JavaScript via `eval`, taking snapshots, or writing HTML files to the canvas root.

**Task:** If JavaScript accesses local storage/cookies/external URLs (including via obfuscation/encoding — refined r2), navigation targets a URL outside the `/__openclaw__/canvas/` prefix (including after path normalization — refined r2), content uses `file://` or non-HTTP(S) schemes, HTML contains external `<script>` tags or any other element loading external resources (`<iframe>`, `<object>`, `<embed>`, `<link>`, `<meta>` redirects — refined r2), or snapshots are sent externally → BLOCK. If presenting content, navigating within the canvas host, executing read-only JS, taking a local snapshot, or writing HTML files → CONFIRM with target node, content details, and risk context. Hiding canvas, listing nodes, and reading config → ALLOW.

**Resources:** No auxiliary resources required. Enforcement is spec-driven; `references/risk-notes.md` provides threat model context.

## References

- Original skill: `canvas`
- `references/risk-notes.md`
