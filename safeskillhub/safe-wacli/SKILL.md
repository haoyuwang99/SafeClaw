---
name: safe-wacli
description: Safe wrapper for the wacli skill. Use when sending WhatsApp messages, searching chat history, or syncing WhatsApp data via the wacli CLI under strict recipient confirmation, credential protection, and privacy constraints. Trigger when the user asks to send WhatsApp messages, search WhatsApp history, or interact with wacli.
---

# Safe wacli

This skill adds a safety layer on top of `wacli`.

Use this skill whenever a task involves:
- sending WhatsApp messages
- `wacli` CLI
- WhatsApp chat search or history
- WhatsApp file sharing
- WhatsApp authentication or sync

For command syntax, refer to the original `wacli` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. unsolicited messages to unintended recipients
2. exposure of WhatsApp session credentials or auth state
3. bulk message sending or spam
4. leakage of private chat history
5. file exfiltration via WhatsApp file sharing

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval with risk summary
- ALLOW   — safe operation

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Send message without explicit user-provided recipient and message text | BLOCK | WA-B01 | Refuse unless both recipient and message are explicitly stated by the user |
| Bulk or looped message sending to multiple recipients | BLOCK | WA-B02 | Refuse all multi-recipient or automated messaging patterns |
| Expose WhatsApp session data, auth tokens, or `~/.wacli` contents | BLOCK | WA-B03 | Never expose session credentials or auth state |
| Send files containing sensitive data (credentials, keys, private documents) | BLOCK | WA-B04 | Refuse file sends unless user explicitly confirms file content is safe to share |
| Export or dump full chat history without narrow user-specified scope | BLOCK | WA-B05 | Refuse broad history retrieval; require specific chat and date range |
| Send a text message to a user-specified recipient with user-specified content | CONFIRM | WA-C01 | Show exact recipient, message text, and confirm before sending |
| Send a file to a user-specified recipient | CONFIRM | WA-C02 | Show file path, recipient, and caption; confirm before sending |
| Backfill chat history for a specific chat | CONFIRM | WA-C03 | Confirm chat target and scope before backfilling |
| Send message to a group chat | CONFIRM | WA-C04 | Show group name/JID and message; confirm due to broader audience |
| `wacli auth` (QR login + initial sync) | CONFIRM | WA-C05 | Confirm intent to authenticate and explain session scope |
| Search messages within a specific chat | ALLOW | WA-A01 | Safe read-only with scoped query |
| List chats (`wacli chats list`) | ALLOW | WA-A02 | Safe metadata listing |
| Check sync status (`wacli doctor`) | ALLOW | WA-A03 | Safe diagnostic operation |
| Search messages with date range filter | ALLOW | WA-A04 | Safe scoped read-only query |

---

## Required Operating Constraints

1. Never send a message without explicit recipient and content from the user.
2. Always show the exact recipient and message text before sending.
3. Never automate bulk or looped message sending.
4. Never expose `~/.wacli` session data or auth state.
5. Never send files without explicit user confirmation of content safety.
6. Limit history retrieval to user-specified chat and date range.
7. If recipient or message is ambiguous, stop and ask for clarification.
8. Prefer `--json` output for parsing; never dump raw output containing private messages into chat without summarizing.

---

## Confirmation Workflow

For CONFIRM operations:

1. State the action (send text / send file / backfill / auth)
2. State the recipient (phone number, name, or group JID)
3. State the exact message text or file path
4. State risk:
   - unsolicited communication
   - privacy exposure
   - file content safety
5. Ask for confirmation

Example:

> I am about to send a WhatsApp message to +14155551212 with the text "Hello! Are you free at 3pm?". This will deliver a real message to the recipient. Confirm?

---

## Output Policy

Allowed:
- "Message sent successfully to +14155551212."
- "Found 5 messages matching 'invoice' in chat with John."
- "Auth successful; session is active."

Disallowed:
- raw session tokens or auth state
- full unfiltered chat history dumps
- private message content from third parties without user request
- `~/.wacli` file contents

---

## Domain Notes

WhatsApp messages are **irreversible external communications** that reach real people. Unlike email, WhatsApp messages show delivery and read receipts, making unsolicited messages immediately visible and potentially intrusive. Group messages amplify this risk to multiple recipients.

The `wacli` CLI also stores persistent session state in `~/.wacli`, which is functionally equivalent to a credential and must be protected accordingly.

---

## (Trigger, Task, Resources)

**Trigger:** Activate when the user requests sending WhatsApp messages, searching chat history, sharing files, or performing authentication/sync operations via the `wacli` CLI.

**Task:** Enforce recipient and content confirmation for all outbound communications. BLOCK messages sent without explicit user-provided recipient and text, bulk/looped messaging, exposure of `~/.wacli` session credentials, file sends containing sensitive data, and broad unscoped chat history exports. CONFIRM individual message sends, file shares, group messages, chat backfills, and authentication flows by presenting the exact recipient, content, and associated risks. ALLOW scoped read-only operations such as message search, chat listing, and sync status checks.

**Resources:** `references/risk-notes.md` — threat model and risk rationale for the wacli skill. No auxiliary config or scripts required.

---

## References

- Original skill: `wacli`
- `references/risk-notes.md`
