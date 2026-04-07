# Risk Notes for safe-wacli

## Threat Model Summary

The `wacli` skill provides CLI access to WhatsApp for sending messages, files, searching history, and syncing data. It is a high-risk capability: messages are irreversible external communications to real people, and the tool holds persistent session credentials.

## Key Risks

### 1. Unsolicited Messages
Risk:
- An agent could send messages without genuine user intent.
- Adversarial prompts could manipulate the recipient or message content.
- Group messages affect multiple people simultaneously.

Mitigation:
- Require explicit user-provided recipient and message for every send.
- Show exact content in confirmation before sending.
- Extra confirmation for group messages due to broader audience.

### 2. Credential / Session Exposure
Risk:
- `~/.wacli` contains WhatsApp session data equivalent to an auth credential.
- Exposing this data could allow session hijacking.

Mitigation:
- Block all access to `~/.wacli` contents.
- Never display session tokens or auth state.

### 3. Bulk Messaging / Spam
Risk:
- Automated loops could send messages to many recipients.
- This constitutes spam and could result in WhatsApp account ban.

Mitigation:
- Block multi-recipient or looped sending patterns.

### 4. Chat History Privacy
Risk:
- Broad history retrieval could expose private conversations.
- Message search without scope could surface sensitive content.

Mitigation:
- Require specific chat and date range for history queries.
- Block full export or broad dumps.
- Summarize results rather than dumping raw messages.

### 5. File Exfiltration
Risk:
- `wacli send file` could be used to exfiltrate sensitive local files via WhatsApp.

Mitigation:
- Require explicit user confirmation of file path and content safety.
- Block sends of files containing credentials or keys.

### 6. Wrong Recipient
Risk:
- Ambiguous instructions could lead to messaging the wrong person.
- JID confusion (direct vs group) could route messages incorrectly.

Mitigation:
- Display exact recipient (number or JID) before sending.
- Require explicit confirmation.

## Safe vs Unsafe

Safe:
- List chats
- Search messages (scoped)
- Check sync status / doctor

Confirm:
- Send text message
- Send file
- Backfill history
- Group messages
- Auth / QR login

Block:
- Send without explicit recipient/message
- Bulk/loop sending
- Expose session data
- Send sensitive files
- Broad history dumps
