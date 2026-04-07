---
name: safe-himalaya
description: Safe wrapper for the himalaya skill. Use when managing emails via the himalaya CLI including listing, reading, composing, replying, forwarding, searching, deleting emails, managing folders, handling attachments, managing flags, and working with multiple IMAP/SMTP accounts. Trigger when the user asks to use himalaya, email CLI, IMAP, SMTP, mailbox operations, or MML composition.
---

# Safe Himalaya CLI

This skill adds a safety layer on top of `himalaya`.

Use this skill whenever a task involves:
- `himalaya`
- Email CLI operations (list, read, send, reply, forward, delete)
- IMAP/SMTP account management
- Mailbox / folder operations
- Attachment handling
- MML email composition
- Flag management
- Envelope listing or searching

For command syntax and product behavior, refer to the original `himalaya` skill and official himalaya documentation.

## Safety Goals

This wrapper is designed to prevent:
1. Irreversible email deletion without explicit user confirmation
2. Unintended email sending to wrong or overly broad recipients
3. Credential exposure of IMAP/SMTP passwords in chat, logs, or files
4. Bulk destructive operations across accounts or folders without scoped approval
5. Downloading or executing potentially malicious attachments without awareness
6. Operating on the wrong account or mailbox unintentionally

## Enforcement Model

Actions are classified into three levels:

- `BLOCK`   — refuse outright
- `CONFIRM` — require explicit user approval with a risk summary
- `ALLOW`   — permitted under scope and output constraints

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Print, paste, or return IMAP/SMTP passwords, app passwords, or auth tokens into chat/logs/code | BLOCK | HM-B01 | Refuse and explain that credentials must never be exposed in conversation output |
| Bulk delete emails across an entire folder or account without narrow user-specified scope (a search query alone does not count as narrow scope if the result count is unknown or unbounded; require explicit message IDs or a bounded count) | BLOCK | HM-B02 | Refuse broad deletion and ask for specific message IDs or a bounded filter with known result count (refined r2) |
| Send email to more than 10 recipients or to distribution lists without explicit enumeration | BLOCK | HM-B03 | Refuse and require the user to confirm each recipient or narrow the list |
| Execute or open downloaded attachments directly | BLOCK | HM-B04 | Refuse; attachments must only be saved to disk for manual user review |
| Read, display, or export IMAP/SMTP config files containing plaintext credentials | BLOCK | HM-B05 | Refuse and recommend reviewing config files manually outside the agent |
| Bulk move, copy, or forward all messages from one folder/account to another without narrow scope | BLOCK | HM-B06 | Refuse broad operations (including bulk forwarding of unbounded message sets) and ask for specific message IDs or a bounded filter (refined r2) |
| Send email to any external recipient | CONFIRM | HM-C01 | Show full recipient list, subject, and body summary; warn that sending is irreversible |
| Reply or reply-all to a message | CONFIRM | HM-C02 | Show all recipients (including CC), subject, and body summary; highlight reply-all scope |
| Forward a message to a new recipient | CONFIRM | HM-C03 | Show the forward target, original sender, subject, and body summary |
| Delete one or more specific emails | CONFIRM | HM-C04 | Show message IDs, subjects, and folder; warn that deletion may be irreversible |
| Move or copy specific messages between folders or accounts | CONFIRM | HM-C05 | Show source folder, target folder, message IDs, and note that move removes from source |
| Download attachments from a message | CONFIRM | HM-C06 | Show attachment filenames, sender, and destination path; warn about untrusted senders |
| Add or remove flags on messages (e.g., mark as read, star, archive) | CONFIRM | HM-C07 | Show message IDs, current flags, and intended flag change |
| Switch active account for subsequent operations | CONFIRM | HM-C08 | Show current account and target account; require confirmation to avoid cross-account mistakes |
| List folders / mailboxes for the current account | ALLOW | HM-A01 | Allowed; metadata only |
| List envelopes (subject, sender, date) in a specific folder | ALLOW | HM-A02 | Allowed; summarize without exposing full message bodies |
| Read a specific message by ID | ALLOW | HM-A03 | Allowed; display content but redact any embedded credentials or tokens |
| Search emails by query within a specific folder | ALLOW | HM-A04 | Allowed; return envelope summaries only |
| List configured accounts (names only, no credentials) | ALLOW | HM-A05 | Allowed; never include passwords, hostnames with embedded credentials, or auth tokens |
| Check himalaya version or connection status | ALLOW | HM-A06 | Allowed; non-sensitive diagnostic information |

## Required Operating Constraints

1. Never display IMAP/SMTP passwords, app passwords, or auth tokens in any output.
2. Never send an email without showing the user the full recipient list, subject, and body summary first.
3. Never delete emails in bulk without explicit per-batch confirmation and a bounded scope. A search query alone is not sufficient scope — require explicit message IDs or a confirmed bounded count. (refined r2)
4. Never operate on an account the user has not explicitly selected or confirmed.
5. Never execute or directly open downloaded attachments; only save them to a user-specified path.
6. Never expose raw config file contents that may contain credentials.
7. Prefer envelope summaries over full message dumps when listing emails.
8. If account or folder scope is ambiguous, stop and ask for clarification.

## Confirmation Workflow

For any `CONFIRM` operation, follow this exact flow:

1. State the intended operation in one sentence.
2. State the exact scope:
   - account
   - folder
   - message ID(s) or recipient(s)
   - action (send / delete / move / flag change)
3. State the main risk:
   - irreversible send
   - irreversible deletion
   - wrong-account operation
   - untrusted attachment
   - reply-all to large recipient list
4. State the safety controls that will be applied:
   - no credential exposure
   - scoped to listed messages only
   - recipient list fully enumerated
   - attachment saved but not executed
5. Ask for explicit confirmation.

Example confirmation text:

> I am about to send an email from account `<account>` to `<recipient>` with subject "<subject>". The body is <N> lines. Sending is irreversible and the message cannot be recalled. I will not expose any account credentials. Confirm?

## Output Policy

When responding to the user:
- Never include IMAP/SMTP passwords, app passwords, or auth tokens
- Never include raw config file contents with embedded credentials
- Summarize email content rather than dumping full raw MIME unless specifically requested
- If a message contains embedded credentials or tokens, redact them before display
- For sent emails, confirm delivery status without re-displaying full message content

Allowed examples:
- "Listed 25 envelopes in INBOX for account X."
- "Message #42 from sender@example.com, subject: 'Meeting notes', 3 attachments."
- "Email sent successfully to recipient@example.com."
- "Moved messages #10, #11 from INBOX to Archive."

Disallowed examples:
- IMAP/SMTP password or app password
- OAuth token or refresh token
- Raw config file with `password =` or `password-cmd =` lines
- Full MIME dump containing auth headers

## (Trigger, Task, Resources)

**Trigger:** Activates whenever the user requests any email operation through the himalaya CLI, including sending, replying, forwarding, deleting, moving, downloading attachments, managing flags, switching accounts, or accessing IMAP/SMTP configuration.

**Task:** If the operation involves credential exposure (passwords, tokens, auth configs), bulk unscoped deletion/move, mass recipient sends (>10), executing attachments, or reading raw credential files → BLOCK. If the operation involves sending, replying, forwarding, deleting specific messages, moving/copying messages, downloading attachments, changing flags, or switching accounts → CONFIRM with full scope preview (recipients, subjects, message IDs, account, folder) and risk warning. If the operation is read-only metadata retrieval (listing folders, envelopes, reading a message by ID, searching, listing account names, or checking version) → ALLOW with credential redaction.

**Resources:** `references/risk-notes.md` — threat model and risk rationale from Phase 1 analysis. No auxiliary config or scripts required.

## References

- Original skill: `himalaya`
- `references/risk-notes.md`
