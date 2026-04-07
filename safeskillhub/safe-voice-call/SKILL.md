---
name: safe-voice-call
description: Safe wrapper for the voice-call skill. Use when initiating, managing, or inspecting voice calls via the OpenClaw voice-call plugin under strict recipient confirmation, credential protection, and scope constraints. Trigger when the user asks to make phone calls, check call status, or interact with Twilio/Telnyx/Plivo telephony.
---

# Safe Voice Call

This skill adds a safety layer on top of `voice-call`.

Use this skill whenever a task involves:
- initiating voice calls
- `openclaw voicecall`
- Twilio / Telnyx / Plivo telephony
- `voice_call` tool actions
- call status checks

For command syntax, refer to the original `voice-call` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. unsolicited or unauthorized phone calls
2. telephony credential exposure (account SIDs, auth tokens, API keys)
3. calls to unintended or unverified recipients
4. message content injection or manipulation
5. excessive call volume or cost

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval with risk summary
- ALLOW   — safe operation

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Expose telephony credentials (accountSid, authToken, apiKey, fromNumber) | BLOCK | VC-B01 | Never expose provider secrets in chat, logs, or output |
| Initiate call without explicit user-provided recipient and message | BLOCK | VC-B02 | Refuse unless both recipient number and message text are explicitly stated by the user |
| Batch or loop calls to multiple recipients | BLOCK | VC-B03 | Refuse all multi-recipient or automated dialing patterns |
| Call emergency numbers (911, 112, 999, etc.) | BLOCK | VC-B04 | Refuse calls to known emergency service numbers |
| Modify plugin configuration or provider settings | BLOCK | VC-B05 | Refuse config changes; user must configure manually |
| Initiate a single call to a user-specified recipient with user-specified message | CONFIRM | VC-C01 | Show recipient number, message text, and provider before proceeding |
| Continue or speak into an active call (`continue_call`, `speak_to_user`) | CONFIRM | VC-C02 | Confirm message content before sending |
| End an active call (`end_call`) | CONFIRM | VC-C03 | Confirm call ID and intent before terminating |
| Check call status (`get_status`) | ALLOW | VC-A01 | Safe read-only operation |
| Check auth status or plugin configuration existence | ALLOW | VC-A02 | Safe metadata check |

---

## Required Operating Constraints

1. Never initiate a call without explicit recipient and message from the user.
2. Never expose telephony credentials or provider configuration secrets.
3. Always show the exact recipient number and message text before calling.
4. Never automate repeated or bulk calls.
5. Never call emergency numbers.
6. Only use the `mock` provider for testing; confirm before using live providers.
7. If recipient or message is ambiguous, stop and ask for clarification.

---

## Confirmation Workflow

For CONFIRM operations:

1. State the action (initiate / continue / end call)
2. State the recipient phone number
3. State the exact message text
4. State the provider (Twilio / Telnyx / Plivo / mock)
5. State risk:
   - unsolicited communication
   - telephony cost
6. Ask for confirmation

Example:

> I am about to initiate a voice call to +15555550123 with the message "Hello from OpenClaw" via Twilio. This will place a real phone call and may incur telephony charges. Confirm?

---

## Output Policy

Allowed:
- "Call initiated successfully. Call ID: <id>"
- "Call status: ringing / in-progress / completed"
- "Plugin is enabled and configured."

Disallowed:
- raw telephony credentials
- accountSid, authToken, apiKey values
- full plugin configuration dumps

---

## Domain Notes

Voice calls are **irreversible external actions** that directly affect real people. Unlike text-based tools, a phone call cannot be "undone" — it rings the recipient's phone immediately. This makes recipient and message confirmation critical before every call initiation.

The mock provider should be preferred for testing and development scenarios.

---

## (Trigger, Task, Resources)

**Trigger:** Activate when the user requests initiating, managing, or inspecting voice calls via `openclaw voicecall` or any Twilio/Telnyx/Plivo telephony interaction.

**Task:** Enforce strict recipient and message confirmation before any call initiation. BLOCK exposure of telephony credentials, calls without explicit user-provided recipient and message, batch/loop dialing, calls to emergency numbers, and provider configuration changes. CONFIRM single calls by displaying the recipient number, message text, and provider; also confirm before continuing, speaking into, or ending active calls. ALLOW read-only operations such as checking call status or plugin configuration existence.

**Resources:** `references/risk-notes.md` — threat model and risk rationale for the voice-call skill. No auxiliary config or scripts required.

---

## References

- Original skill: `voice-call`
- `references/risk-notes.md`
