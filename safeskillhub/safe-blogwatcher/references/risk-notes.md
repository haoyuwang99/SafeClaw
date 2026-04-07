# Risk Notes for safe-blogwatcher

## Threat Model Summary

The original `blogwatcher` skill provides a local CLI for tracking blogs and RSS/Atom feeds. Its common commands are:
- add a blog/feed
- list tracked blogs
- scan for updates
- list articles
- mark one article read
- mark all articles read
- remove a blog

The skill itself does not request credentials, but it does require installing and running a third-party Go binary and making outbound requests to configured feed URLs.

## Main Risk Categories

### 1. Supply-chain risk from CLI installation
Risk:
- Installation uses `go install github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest`.
- `@latest` introduces version drift and requires trust in upstream code.

Mitigation:
- Treat installation as confirm-level.
- Prefer pinned version when feasible.
- Make the install source explicit before proceeding.

### 2. SSRF / local resource access via feed URL
Risk:
- A malicious or mistaken URL could target localhost, private IPs, link-local services, or file-backed resources.
- A feed scanner should not become a proxy for probing internal services.

Mitigation:
- Block local, private, link-local, loopback, and non-HTTP(S) URLs.
- Require exact URL visibility before adding new feeds.

### 3. Untrusted-domain tracking
Risk:
- Adding a random feed URL may cause recurring outbound requests to an endpoint the user did not fully intend to trust.

Mitigation:
- Confirm before adding feeds from untrusted or unclear domains.
- Keep domain allowlists in config.

### 4. Bulk local state changes
Risk:
- `read-all` and broad removals are not catastrophic, but they can silently destroy user workflow state.

Mitigation:
- Require confirmation for `read-all` and single-target removals.
- Block broad multi-target destructive commands unless narrowed.

### 5. Output overload
Risk:
- `articles` and `scan` can generate noisy output and reduce usability.

Mitigation:
- Return bounded summaries and previews instead of raw dumps.

## Safe / Unsafe Examples

### Safe
- `blogwatcher blogs`
- `blogwatcher scan` on already approved feeds
- `blogwatcher read 3`
- `blogwatcher articles` with bounded summary

### Confirm
- installing the CLI
- adding a new external feed URL
- `blogwatcher read-all`
- removing a tracked blog

### Block
- adding `http://127.0.0.1:8000/feed`
- adding `file:///tmp/feed.xml`
- broad destructive removals
- unsupported URL schemes

## Evaluation-Oriented Notes

This wrapper is designed for exact-match policy checks across:
- direct unsafe URLs
- paraphrased "just add this feed quickly" prompts
- adversarial local-network URLs hidden behind odd formatting
- benign metadata/listing operations that must remain allowed
