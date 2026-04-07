# Risk Notes for safe-bluebubbles

## Threat Model Summary

BlueBubbles is an iMessage gateway integration for OpenClaw. It sends real messages to real phone numbers and email addresses via the `message` tool with `channel: "bluebubbles"`. Actions include send, react, edit, unsend, reply, sendAttachment, and sendWithEffect. Requires gateway config with `serverUrl`, `password`, and `webhookPath`.

## Action Space

- **read**: List messages, look up chat_guid, contact lookup
- **write**: Send messages, react (tapback), reply, send attachments, send with effects
- **destructive**: Edit sent messages, unsend messages
- **external**: All send/react/edit/unsend actions deliver to external recipients via iMessage
- **credential**: Gateway config contains `password` and `serverUrl`

## Key Risks

### 1. Wrong Recipient
- **Risk**: Message delivered to unintended person — cannot be recalled on all devices.
- **Category**: Irreversibility, External interaction
- **Trigger**: Ambiguous user request like "text my mom" without explicit handle.
- **Mitigation**: Block sends without explicit recipient; never guess contacts.

### 2. Fabricated Content
- **Risk**: Agent composes message text the user did not provide or approve.
- **Category**: External interaction, Scope explosion
- **Trigger**: User gives vague instruction like "tell them I'll be late."
- **Mitigation**: Block sends without user-provided exact message text.

### 3. Attachment Exfiltration
- **Risk**: Local files (credentials, keys, personal documents) sent via attachment.
- **Category**: Credential exposure, External interaction
- **Trigger**: `sendAttachment` with path to sensitive file.
- **Mitigation**: Block known sensitive file patterns; confirm all attachments with file details.

### 4. Bulk Messaging
- **Risk**: Automated loops sending messages to multiple recipients.
- **Category**: Scope explosion, External interaction
- **Trigger**: Programmatic iteration over contact list.
- **Mitigation**: Block multi-recipient automated sends.

### 5. Destructive Edits
- **Risk**: Editing or unsending messages alters conversation history visible to recipient.
- **Category**: Irreversibility
- **Trigger**: `edit` or `unsend` action.
- **Mitigation**: Confirm with full context; warn about device compatibility limitations.

### 6. Credential Exposure
- **Risk**: Gateway config contains `password` and `serverUrl`.
- **Category**: Credential exposure
- **Trigger**: Reading or displaying BlueBubbles gateway configuration.
- **Mitigation**: Never display gateway credentials in output.

## Safe vs Unsafe

Safe:
- reading/listing messages
- looking up chat_guid or contacts

Confirm:
- sending a message (with user-provided text and explicit recipient)
- sending attachments
- reacting (tapback)
- editing sent messages
- unsending messages
- replying in threads
- sending with effects

Block:
- sending without explicit recipient
- sending without user-provided exact text
- attaching sensitive files (credentials, keys, .env)
- bulk automated messaging
