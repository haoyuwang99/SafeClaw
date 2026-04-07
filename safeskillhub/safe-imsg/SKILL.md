---
name: safe-imsg
description: Safe wrapper for the imsg skill. Use when listing iMessage/SMS chats, viewing message history, watching for new messages, or sending messages and attachments via macOS Messages.app. Trigger when the user asks to send a text, read messages, list conversations, send an iMessage, send an SMS, or attach files to a message.
---

# Safe iMessage/SMS CLI

This skill adds a safety layer on top of `imsg`.

Use this skill whenever a task involves:
- `imsg`
- iMessage or SMS sending
- listing chats or conversations
- viewing message history
- watching for new messages
- sending attachments via Messages.app
- specifying iMessage vs SMS service

For command syntax and product behavior, refer to the original `imsg` skill and macOS Messages.app documentation.

## Safety Goals

This wrapper is designed to prevent:
1. sending messages to unintended or unverified recipients
2. bulk or mass messaging to many recipients
3. exposure of private conversation history or contact PII
4. sending unauthorized attachments to external recipients
5. impersonation of the user through unsanctioned message sending

## Enforcement Model

Actions are classified into three levels:

- `BLOCK`   — refuse outright
- `CONFIRM` — require explicit user approval with a risk summary
- `ALLOW`   — permitted under scope and output constraints

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Send messages in a loop, send more than one message per request, or send to more than one recipient in a single request (refined r2) | BLOCK | IM-B01 | Refuse bulk/mass messaging; require exactly one message to one recipient per confirmed request |
| Send a message to a recipient not explicitly named by the user in the current turn | BLOCK | IM-B02 | Refuse; the recipient must be explicitly stated by the user, never inferred or reused from history |
| Send sensitive data (private keys, credentials, financial documents, health records) whether as file attachments or as content pasted into message body text (refined r2) | BLOCK | IM-B03 | Refuse and explain the risk of sending sensitive material over messaging in any form |
| Enumerate or export full chat history across all conversations | BLOCK | IM-B04 | Refuse broad retrieval; require a specific conversation or contact |
| Forward or relay message content from one conversation to another recipient | BLOCK | IM-B05 | Refuse; cross-conversation relay risks unintended disclosure of private content |
| Output raw phone numbers, Apple IDs, or full contact lists into chat or logs | BLOCK | IM-B06 | Refuse; summarize contacts by name or masked identifier only |
| Send a text message to a single, user-specified recipient | CONFIRM | IM-C01 | Show exact recipient, message body, and service (iMessage/SMS) before sending |
| Send an attachment to a single, user-specified recipient | CONFIRM | IM-C02 | Show exact recipient, file name, file size, and service before sending |
| Force a specific service (iMessage or SMS) for sending | CONFIRM | IM-C03 | Show the service choice and recipient; confirm the user intends this routing |
| View message history for a specific, user-named conversation | CONFIRM | IM-C04 | Show the contact/chat being accessed and the scope (number of messages) before proceeding |
| Watch for new incoming messages on a specific conversation | CONFIRM | IM-C05 | Show which conversation will be monitored and confirm before starting |
| List chat names or conversation summaries (metadata only) | ALLOW | IM-A01 | Allowed if output contains only conversation names or masked identifiers, no message content |
| Check Messages.app availability or imsg tool status | ALLOW | IM-A02 | Allowed; no sensitive data involved |
| Display message count or last-message timestamp for a conversation | ALLOW | IM-A03 | Allowed if no message body content is included |

## Required Operating Constraints

1. Never send a message without explicit user confirmation in the same turn.
2. Never send more than one message per confirmed action, and never send to more than one recipient per confirmed action (refined r2).
3. Never infer or auto-fill a recipient from prior conversation context; the user must state the recipient explicitly each time.
4. Never include raw phone numbers or Apple IDs in output; use display names or masked forms (e.g., +1***-***-1234).
5. Never output full message bodies from chat history without user confirmation for that specific conversation.
6. Prefer metadata summaries (chat name, message count, timestamp) over raw message content.
7. Always show the complete message body to the user for review before sending.
8. If the recipient, message content, or attachment is ambiguous, stop and ask for clarification.

## Confirmation Workflow

For any `CONFIRM` operation, follow this exact flow:

1. State the intended operation in one sentence.
2. State the exact scope:
   - recipient (name or masked identifier)
   - message body (full text) or attachment (file name and size)
   - service (iMessage, SMS, or default)
3. State the main risk:
   - irreversible send to wrong recipient
   - private content disclosure
   - sensitive attachment transmission
4. State the safety controls that will be applied:
   - single recipient only
   - no bulk send
   - no auto-inferred recipients
   - message body shown for review
5. Ask for explicit confirmation.

Example confirmation text:

> I am about to send an iMessage to "Alice (masked: +1***-***-5678)" with the following message body: "Meeting moved to 3 PM tomorrow." This message cannot be recalled once sent. I will send to this single recipient only and will not infer additional recipients. Confirm?

## Output Policy

When responding to the user:
- Never include raw phone numbers or Apple IDs; always mask or use display names
- Never dump full conversation transcripts without prior confirmation
- Summarize message history by count, participants, and timeframe rather than raw content
- If message content must be shown, limit to the user-requested scope only

Allowed examples:
- "You have 14 conversations. Most recent: Alice (2 hours ago), Bob (yesterday)."
- "Message sent successfully to Alice via iMessage."
- "Watching for new messages in the conversation with Bob."

Disallowed examples:
- raw phone number: +15551234567
- raw Apple ID email: user@icloud.com
- full unscoped chat transcript across multiple conversations
- message content from a conversation the user did not specifically request

## (Trigger, Task, Resources)

**Trigger:** Activates whenever the user requests any iMessage or SMS operation through the imsg tool, including sending text messages, sending attachments, viewing message history, listing conversations, or watching for incoming messages via macOS Messages.app.

**Task:** If the operation involves bulk/mass messaging (including multiple messages in one request), sending to a recipient not explicitly named in the current turn, sending sensitive data as attachments or message body content (refined r2), exporting full chat history across all conversations, cross-conversation message relay, or exposing raw phone numbers/Apple IDs → BLOCK. If the operation involves sending a message or attachment to a single user-specified recipient, forcing a specific service (iMessage/SMS), viewing history for a named conversation, or watching a specific conversation → CONFIRM with full preview of recipient, message body, and service. If the operation is metadata-only (listing chat names, checking tool status, displaying message counts/timestamps) → ALLOW.

**Resources:** `references/risk-notes.md` — threat model and risk rationale from Phase 1 analysis. No auxiliary config or scripts required.

## References

- Original skill: `imsg`
- `references/risk-notes.md`
