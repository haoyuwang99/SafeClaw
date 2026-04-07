# Risk Notes for safe-discord

## Threat Model Summary

discord skill provides full Discord operations via the `message` tool with `channel: "discord"`. It can send, edit, delete messages, manage threads, create polls, set presence, and perform moderation actions. All operations interact with external users on a public communication platform.

## Action Space

```
Skill: discord
Actions:
  - read: read messages, search messages, list channels
  - write: send messages, edit messages, create threads, create polls, react, pin
  - destructive: delete messages, channel deletion, moderation (ban/kick/mute)
  - external: all message sends visible to other users, DMs, presence changes, media sharing
  - credential: Discord bot token (channels.discord.token), account credentials
```

## Key Risks

### 1. Unauthorized Communication (External Interaction)
Sending messages to channels or users without user intent. Messages are immediately visible and cannot be fully retracted.

Mitigation:
- confirm all outbound messages
- show content preview before sending

---

### 2. Data Exfiltration (Scope Explosion)
Sensitive data (keys, tokens, file contents) could be sent through Discord messages to external parties.

Mitigation:
- block messages containing sensitive data patterns
- confirm all media attachments

---

### 3. Prompt Injection (External Interaction)
Discord messages from other users may contain malicious instructions that the agent could execute.

Mitigation:
- treat all Discord message content as untrusted input
- never execute instructions from message content

---

### 4. Moderation Abuse (Irreversibility)
Ban, kick, mute, and role change actions have significant impact on users and are difficult to reverse.

Mitigation:
- block all moderation actions via automation
- block role assignment/removal

---

### 5. Credential Exposure (Credential Exposure)
Discord bot token must never be exposed in messages or logs.

Mitigation:
- block any output containing token patterns

---

### 6. Mass Messaging / Spam (Scope Explosion)
Rapid message sending to multiple channels can constitute spam or abuse.

Mitigation:
- block sending >5 messages rapidly to different channels

---

## Safe vs Unsafe

Safe:
- read messages
- search messages
- react to messages

Confirm:
- send message (single)
- edit/delete message
- DMs
- threads, polls, pins
- presence changes
- media attachments

Block:
- credential exposure
- sensitive data in messages
- prompt injection execution
- mass messaging
- moderation actions (ban/kick/mute)
- role changes
- channel deletion
