# Risk Notes for safe-slack

## Threat Model Summary

The slack skill provides full control over Slack messaging — sending, editing, deleting messages, reacting, and managing pins. This creates significant risk of unauthorized communication, data exfiltration via outbound messages, accidental mass messaging, and irreversible message deletion.

## Key Risks

### 1. Unauthorized Messaging
The agent could send messages to channels or users without explicit user intent, potentially causing confusion or reputational harm.

Mitigation:
- confirm every outbound message with full content preview
- require explicit channel/user targeting

---

### 2. Data Exfiltration via Messages
Local sensitive data (env vars, file contents, credentials) could be exfiltrated by embedding it in outbound Slack messages.

Mitigation:
- block messages containing detected secrets or credentials
- block inclusion of harvested local file contents

---

### 3. Mass Messaging / Spam
Loops or batch operations could send messages to many channels or users simultaneously.

Mitigation:
- block bulk send operations
- require individual confirmation for each recipient

---

### 4. Message Deletion
Deleting messages is irreversible and could destroy important communications or audit trails.

Mitigation:
- confirm before every delete with message preview
- never batch-delete

---

### 5. Impersonation
Crafted message content could impersonate other users or systems, creating trust violations.

Mitigation:
- block messages designed to impersonate
- ensure transparency about message source

---

### 6. Wrong Recipient
Messages could be sent to unintended channels or users due to ID confusion.

Mitigation:
- always show recipient details in confirmation
- verify channel/user before sending

---

## Safe vs Unsafe

Safe:
- reading messages
- listing reactions, pins, emoji
- reacting to messages
- looking up member info

Confirm:
- sending a message
- editing a message
- deleting a message
- unpinning a message

Block:
- sending credentials via Slack
- mass messaging across channels
- exfiltrating local data through messages
- impersonation via crafted content
