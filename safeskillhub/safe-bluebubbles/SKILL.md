---
name: safe-bluebubbles
description: Safe wrapper for the bluebubbles skill. Use when sending or managing iMessages via BlueBubbles under strict recipient verification, content review, and attachment safety constraints. Trigger when the user asks to send, edit, unsend, react to, or reply to iMessages, or manage group chat participants through BlueBubbles.
---

# Safe BlueBubbles

This skill adds a safety layer on top of `bluebubbles`.

Use this skill whenever a task involves:
- BlueBubbles / iMessage
- sending text messages
- sending attachments via iMessage
- reacting (tapbacks) to messages
- editing or unsending messages
- replying in threads
- managing group chat participants

For action syntax and normal product behavior, refer to the original `bluebubbles` skill.

## Safety Goals

This wrapper is designed to prevent:
1. messages sent to wrong recipients
2. unintended message content (fabricated or altered text)
3. sensitive data leakage via messages or attachments
4. bulk or automated messaging without user control
5. destructive edits or unsends without confirmation
6. attachment exfiltration of local files

## Enforcement Model

Actions are classified into three levels:

- `BLOCK`   — refuse outright
- `CONFIRM` — require explicit user approval
- `ALLOW`   — permitted without intervention

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Send message without user-provided exact message text | BLOCK | BB-B01 | Never fabricate or infer message content; user must supply exact text |
| Send message to recipient the user did not explicitly name | BLOCK | BB-B02 | Never guess or infer recipients; require explicit target |
| Send attachment containing sensitive files (credentials, keys, .env, config with secrets) | BLOCK | BB-B03 | Prevent credential and secret exfiltration |
| Bulk send messages to 3+ recipients or to an automated/derived recipient list | BLOCK | BB-B04 | Prevent automated spam or mass messaging; sending to 2 explicitly named recipients is two separate CONFIRMs, not bulk (refined r2) |
| Send message text containing sensitive data read from credential/secret files (.env, keys, configs with secrets, SSH keys) | BLOCK | BB-B05 | Prevent secret exfiltration via message body, not just attachments (refined r2) |
| Send message with user-provided text to user-specified recipient | CONFIRM | BB-C01 | Show full recipient, message text, and channel before sending |
| Send attachment | CONFIRM | BB-C02 | Show file path, file size, recipient, and caption before sending |
| React (tapback) to a message | CONFIRM | BB-C03 | Show target message, emoji, and recipient before reacting |
| Edit a previously sent message | CONFIRM | BB-C04 | Show original text, new text, and recipient before editing |
| Unsend a message | CONFIRM | BB-C05 | Show message content being unsent and recipient; warn about irreversibility on older iOS |
| Reply to a specific message | CONFIRM | BB-C06 | Show reply target, reply text, and recipient before sending |
| Send with iMessage effect (balloons, slam, etc.) | CONFIRM | BB-C07 | Show effect type, message, and recipient |
| Remove a reaction | CONFIRM | BB-C08 | Show reaction being removed and context |
| Add or remove a participant from a group chat | CONFIRM | BB-C09 | Show participant, group chat, and action (add/remove) before executing (refined r2) |
| Read or list recent messages (no action payload) | ALLOW | BB-A01 | Read-only; no side effects |
| Look up chat_guid or contact information | ALLOW | BB-A02 | Read-only metadata lookup |

## Required Operating Constraints

1. Never compose message text on behalf of the user; only send user-provided exact text.
2. Never infer or guess recipients; require explicit phone number, email, or chat_guid.
3. Always show full message preview (recipient + text + attachments) before any send action.
4. Block sending of files that may contain credentials or secrets.
5. Block sending sensitive data (credentials, keys, secrets) as message text, not just as attachments. (refined r2)
6. Never send messages in automated loops or to 3+ recipients without individual confirmation; two explicitly named recipients get individual CONFIRMs. (refined r2)
7. Confirm all destructive actions (edit, unsend) with full context.
8. Confirm all group chat participant changes (add/remove) with full context. (refined r2)
9. Treat all outbound messages as high-impact external communication.

## Confirmation Workflow

For any `CONFIRM` operation, follow this exact flow:

1. State the recipient (phone number, email, or chat_guid).
2. State the action (send / react / edit / unsend / reply / attachment).
3. State the full content:
   - exact message text
   - attachment file path and size
   - emoji for reactions
   - effect type if applicable
4. State the risk:
   - message will be delivered to a real person
   - edits/unsends may not be reversible on all devices
   - attachments expose local file data
5. Ask for explicit confirmation.

Example:

> I am about to send the following iMessage via BlueBubbles:
> - To: +15551234567
> - Text: "hello from OpenClaw"
> This will deliver a real message to the recipient. Confirm?

## Output Policy

Allowed:
- "Message sent to +15551234567."
- "Tapback ❤️ added to message."
- "Message unsent successfully."

Disallowed:
- sending any message without showing full preview first
- fabricating message content not provided by the user
- sending to recipients the user did not specify
- silently attaching files

## Domain Notes

BlueBubbles is an iMessage integration that sends **real messages to real people**. Every send action has immediate, externally visible consequences that cannot be fully undone. Message content and recipient accuracy are critical — a wrong message to a wrong person is a high-severity failure. Attachments can exfiltrate local files. This skill requires the highest level of pre-send verification among communication tools.

## (Trigger, Task, Resources)

**Trigger:** Activates when the user requests any iMessage action via BlueBubbles — sending, editing, unsending, reacting to, or replying to messages, sending attachments, or managing group chat participants.

**Task:** If the message text is not user-provided, the recipient is not explicitly named, the attachment contains credentials/secrets, or messages are sent in bulk → BLOCK. If sending a message, attachment, reaction, edit, unsend, reply, or effect to a specified recipient with user-provided content → CONFIRM with full preview (recipient, text, attachments, risk). Read-only operations (listing messages, looking up contacts) → ALLOW.

**Resources:** No auxiliary resources required. Enforcement is spec-driven; `references/risk-notes.md` provides threat model context.

## References

- Original skill: `bluebubbles`
- `references/risk-notes.md`
