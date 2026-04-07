---
name: safe-blogwatcher
description: Safe wrapper for the blogwatcher skill. Use when monitoring blogs and RSS/Atom feeds with the blogwatcher CLI under controlled installation, URL validation, and bounded state changes. Trigger when the user asks to add, scan, list, read, mark, or remove tracked blogs or articles using blogwatcher.
---

# Safe Blogwatcher

This skill adds a safety layer on top of `blogwatcher`.

Use this skill whenever a task involves:
- `blogwatcher`
- RSS / Atom feeds
- adding blogs or feed URLs
- scanning for updates
- listing articles
- marking articles read
- removing tracked blogs

For command syntax and normal product behavior, refer to the original `blogwatcher` skill.

## Safety Goals

This wrapper is designed to prevent:
1. unsafe installation of third-party CLI code
2. SSRF-style or local-network feed access
3. tracking unintended or untrusted feed URLs
4. destructive bulk state changes without confirmation
5. excessive or noisy output from scans and article dumps

## Enforcement Model

Actions are classified into three levels:

- `BLOCK`   — refuse outright
- `CONFIRM` — require explicit user approval
- `ALLOW`   — permitted under scope and output constraints

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Install `blogwatcher` from unpinned or unreviewed third-party source | CONFIRM | BW-C01 | Require explicit approval; recommend pinned version instead of `@latest` where possible |
| Add feed URL using localhost, loopback, private IP, link-local IP, `file://`, or other local-resource schemes | BLOCK | BW-B01 | Refuse as unsafe local/internal resource access |
| Add feed URL with unsupported or non-HTTP(S) scheme | BLOCK | BW-B02 | Refuse invalid or risky scheme |
| Add feed URL to untrusted domain when user intent is unclear | CONFIRM | BW-C02 | Show exact URL and ask for confirmation |
| Bulk import or add many feeds at once from unspecified source | CONFIRM | BW-C03 | Require source summary and item count before proceeding |
| `blogwatcher blogs` | ALLOW | BW-A01 | Allowed; summarize tracked feeds safely |
| `blogwatcher articles` | ALLOW | BW-A02 | Allowed with bounded output and summarization |
| `blogwatcher scan` against already approved feeds | ALLOW | BW-A03 | Allowed; report summary counts rather than raw verbose dump |
| Mark one article read: `blogwatcher read <id>` | ALLOW | BW-A04 | Allowed if the article id is explicitly specified |
| Mark all articles read: `blogwatcher read-all` | CONFIRM | BW-C04 | Require explicit confirmation due to bulk state change |
| Remove one tracked blog with exact name match | CONFIRM | BW-C05 | Require confirmation before destructive state change |
| Remove many blogs or clear all tracked feeds | BLOCK | BW-B03 | Refuse bulk destructive removal unless re-scoped to specific targets |
| Redirect, pipe, or exfiltrate blogwatcher output to an external URL or untrusted destination | BLOCK | BW-B04 | Refuse as unauthorized data exfiltration |

## Required Operating Constraints

1. Only use HTTP or HTTPS feed URLs.
2. Never access localhost, private-network, link-local, or filesystem-backed URLs.
3. Prefer pinned install versions over `@latest` when installation is requested.
4. Summarize scan results instead of dumping excessive raw output.
5. Limit article listing to a bounded number of entries.
6. Treat bulk state changes (`read-all`, broad removals, bulk imports) conservatively.
7. If the requested blog/feed scope is ambiguous, stop and ask for narrowing details.

## URL Safety Policy

Block any feed URL matching one or more of the following:
- `localhost`
- `127.0.0.0/8`
- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`
- `169.254.0.0/16`
- `::1`
- `fc00::/7`
- `fe80::/10`
- `file://`
- other non-HTTP(S) schemes
- `.local` TLD (mDNS local network resolution) (refined r2)
- `.internal`, `.home.arpa`, or other IANA-reserved local-use domain suffixes (refined r2)

### IP Canonicalization Requirement (refined r2)

Before evaluating a URL hostname against the block list, normalize any IP-based hostname to its canonical form:
- Hex-encoded IPs (e.g., `0x7f000001`) must be decoded to dotted-decimal (`127.0.0.1`)
- Decimal integer IPs (e.g., `2130706433`) must be decoded to dotted-decimal (`127.0.0.1`)
- Octal-encoded IPs (e.g., `017700000001`) must be decoded to dotted-decimal (`127.0.0.1`)
- IPv6 addresses must be expanded to full form before comparison

This prevents bypass of the block list via alternative IP representations. All checks against the blocked IP ranges above apply to the canonicalized address.

## Confirmation Workflow

For any `CONFIRM` operation, follow this exact flow:

1. State the intended operation.
2. State the exact scope:
   - install target / version
   - blog name
   - feed URL
   - number of affected items
3. State the main risk:
   - third-party code install
   - untrusted network endpoint
   - bulk state modification
4. State the safety controls that will be applied.
5. Ask for explicit confirmation.

Example confirmation text:

> I am about to add the feed `https://example.com/feed.xml` to blogwatcher. This will allow the local CLI to make future network requests to that URL during scans. I will only add this single feed and will not import any others. Confirm?

## Output Policy

When responding to the user:
- Prefer summaries over raw dumps
- Do not print excessively large article lists
- Show feed URL only when directly relevant
- Report counts and a bounded preview for scan/article results

Allowed examples:
- "Tracked 3 feeds."
- "Scan completed: 2 feeds checked, 5 new articles found."
- "Marked article 7 as read."
- "Removed tracked blog 'My Blog' after confirmation."

Disallowed examples:
- dumping hundreds of articles by default
- adding or scanning local/internal endpoints
- silently running broad destructive commands

## Domain Notes

The original `blogwatcher` skill is low-risk compared with credentialed tools because it does not request secrets and its command set is narrow. However, it still executes a third-party CLI and performs outbound network fetches to user-supplied URLs, so safe use depends on installation review, URL validation, and conservative handling of bulk state changes.

## (Trigger, Task, Resources)

**Trigger:** Activates whenever the user requests any operation involving the `blogwatcher` CLI, including adding or removing tracked blogs/feeds, scanning for updates, listing or reading articles, or installing the tool.

**Task:** If the operation adds a feed URL targeting localhost, private/link-local IPs, or non-HTTP(S) schemes, attempts bulk removal of all tracked feeds, or redirects/pipes blogwatcher output to an external URL or untrusted destination → BLOCK. If the operation installs `blogwatcher`, adds a feed to an untrusted domain, bulk-imports feeds, marks all articles read, or removes a single tracked blog → CONFIRM with a summary showing the exact URL/target, risk context, and applied controls. If the operation is read-only (list blogs, list articles, scan approved feeds, mark a single article read) → ALLOW with bounded output.

**Resources:** `references/risk-notes.md`

## References

- Original skill: `blogwatcher`
- `references/risk-notes.md`
- `config/allowlist.yaml`
- `scripts/check.py`
