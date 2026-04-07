# Risk Notes: safe-bear-notes

Detailed threat analysis for the `safe-bear-notes` skill. These notes inform the Safety Rules defined in `SKILL.md` and should be updated whenever the underlying `bear-notes` skill or `grizzly` CLI changes.

---

## Risk 1: Credential Exposure (BN-B01, BN-B02)

**Source:** Bear API token stored in plaintext at `~/.config/grizzly/token`.

**Attack vectors:**
- The assistant echoes the token value in a message (e.g., when explaining what command was run).
- The token is expanded via a shell environment variable (`GRIZZLY_TOKEN`) and captured by process listing tools (`ps aux`) or shell history.
- A command log or transcript containing the token is uploaded or shared by the user.
- The token is passed as a CLI argument (`--token VALUE`) rather than via file reference, making it visible in process tables.

**Mitigations:**
- BN-B01: Block any output that contains the literal token string.
- BN-B02: Mandate `--token-file` flag only; never expand the token value in command strings shown to the user.
- Reference the credential exclusively by its file path in all assistant messages.

**Residual risk:** Low. The token file itself is not encrypted. If an attacker has local file system access, they can read the token regardless. This skill cannot address OS-level file permissions but will not make the situation worse.

---

## Risk 2: Irreversible Content Modification (BN-C02, BN-C03)

**Source:** `grizzly add-text` supports multiple modes: `append`, `prepend`, and `replace`. The `replace` mode overwrites all existing note content with no built-in undo via the CLI.

**Attack vectors:**
- The assistant issues an `add-text --mode replace` command, permanently destroying existing note content.
- The `--mode` flag is omitted and grizzly defaults to a mode the user did not intend.
- A mistyped note ID causes modification of the wrong note.

**Mitigations:**
- BN-C02: Require confirmation before any append or prepend operation on an existing note.
- BN-C03: Require confirmation with a stronger warning before any replace operation; surface a content preview.
- Always make `--mode` explicit; never let grizzly infer a default mode silently.

**Residual risk:** Medium. Bear's native undo (Cmd+Z) may recover content if the user acts quickly, but this is not guaranteed and is outside the skill's control. The confirmation workflow is the primary safeguard.

---

## Risk 3: Scope Explosion (BN-B04)

**Source:** `grizzly open-note` and tag-based operations could be used in loops to enumerate large numbers of notes.

**Attack vectors:**
- A script or agentic loop iterates over a list of note IDs, exfiltrating all note content.
- A bulk tag search returns hundreds of notes, causing unintended data exposure or application instability.
- Mass note creation (e.g., generating 100 notes in a loop) spams the Bear database.

**Mitigations:**
- BN-B04: Block any unbounded iteration over note IDs or tag contents. Operations must target a single, explicit note ID or a single tag per invocation.
- BN-A02: Tag search (open-tag) is allowed for a single named tag; listing results from that tag is acceptable as a one-shot read.

**Residual risk:** Low for standard use. An adversary with direct shell access can still loop commands; this skill enforces scope only at the assistant invocation level.

---

## Risk 4: x-callback-url Injection (BN-B03)

**Source:** `grizzly` communicates with Bear via the macOS `x-callback-url` URL scheme (`bear://x-callback-url/...`). URL parameters are constructed internally by grizzly but could theoretically be influenced by user-supplied inputs passed through the CLI.

**Attack vectors:**
- User or upstream context supplies a string that is interpolated into a grizzly argument which grizzly then encodes into a callback URL, resulting in a URL that triggers an unintended Bear action.
- The assistant constructs a raw `bear://` URL and passes it to `open` or `xdg-open` directly, bypassing grizzly's validation layer.
- A malicious note title or tag name contains URL-encoded characters that alter the callback URL structure.

**Mitigations:**
- BN-B03: Block any operation that constructs or executes an `x-callback-url` outside of grizzly's own URL-building logic. All Bear interactions must go through `grizzly` subcommands, never via raw URL invocation.
- Treat all user-supplied strings as untrusted; do not interpolate them into command arguments without escaping.

**Residual risk:** Low. grizzly is expected to URL-encode its own parameters. The main danger is bypassing grizzly entirely, which this rule prevents.

---

## Risk 5: Supply-Chain / Binary Integrity (BN-C01)

**Source:** `grizzly` is a third-party Go binary distributed via GitHub releases at `github.com/nicholasgasior/grizzly` (or similar). It is not part of any OS-managed package with automatic signature verification.

**Attack vectors:**
- The binary is downloaded from an unofficial mirror or a typosquatted repository.
- A `PATH`-hijacking attack places a malicious binary named `grizzly` earlier in the shell's `PATH` than the legitimate installation.
- The binary is silently updated to a version with changed behavior or a backdoor.

**Mitigations:**
- BN-C01: Require explicit user confirmation before installing or updating the `grizzly` binary. Show the download source URL and expected checksum.
- BN-A05 (check Bear availability) includes verifying that `which grizzly` resolves to an expected path. If the resolved path is unexpected, block execution.
- Users should pin to a specific release version and verify the SHA-256 checksum published on the GitHub releases page.

**Residual risk:** Medium. Checksum verification prevents tampering with the binary at rest but does not protect against a compromised upstream release. This is an inherent limitation of third-party tooling.

---

## Rule ID Quick Reference

| Rule ID | Category | Summary |
|---------|----------|---------|
| BN-B01 | BLOCK | Never print or output the Bear API token value |
| BN-B02 | BLOCK | Never send the token to external services |
| BN-B03 | BLOCK | Never construct or execute arbitrary x-callback-urls |
| BN-B04 | BLOCK | Never bulk-enumerate notes |
| BN-C01 | CONFIRM | Confirm grizzly installation/update with source and hash |
| BN-C02 | CONFIRM | Confirm append/prepend to existing note |
| BN-C03 | CONFIRM | Confirm replace mode with strong overwrite warning |
| BN-C04 | CONFIRM | Confirm note creation when sensitive patterns detected |
| BN-C05 | CONFIRM | Confirm read of specific note by ID |
| BN-A01 | ALLOW | List tags |
| BN-A02 | ALLOW | Search by single tag |
| BN-A03 | ALLOW | Create simple non-sensitive note |
| BN-A04 | ALLOW | Dry-run / print-url operations |
| BN-A05 | ALLOW | Check Bear availability and grizzly version |

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-03-26 | Initial risk analysis for safe-bear-notes | safe-skill-factory |
