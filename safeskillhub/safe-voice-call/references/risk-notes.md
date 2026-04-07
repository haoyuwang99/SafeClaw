# Risk Notes for safe-voice-call

## Threat Model Summary

The `voice-call` skill enables agent-initiated phone calls via Twilio, Telnyx, or Plivo through the OpenClaw voice-call plugin. This is a high-risk capability: calls are irreversible external actions that directly contact real people and incur cost.

## Key Risks

### 1. Unsolicited Calls
Risk:
- An agent could initiate calls without genuine user intent.
- Adversarial prompts could trick the agent into calling unintended recipients.

Mitigation:
- Require explicit user-provided recipient and message for every call.
- Block automated or bulk dialing.

### 2. Credential Exposure
Risk:
- Telephony provider credentials (Twilio accountSid/authToken, Telnyx apiKey, Plivo authId/authToken) could be leaked in chat or logs.
- Plugin config contains sensitive fromNumber and provider secrets.

Mitigation:
- Block all display or logging of provider credentials.
- Never read or dump plugin configuration values.

### 3. Wrong Recipient
Risk:
- Ambiguous instructions ("call John") could lead to calling the wrong person.
- Number formatting errors could route calls incorrectly.

Mitigation:
- Always display the exact phone number before calling.
- Require explicit confirmation.

### 4. Message Manipulation
Risk:
- Adversarial prompt injection could alter the message content spoken during a call.

Mitigation:
- Display exact message text in confirmation.
- Block calls where message source is ambiguous.

### 5. Cost and Abuse
Risk:
- Repeated calls or calls to premium numbers could incur significant charges.
- Bulk calling could constitute harassment or spam.

Mitigation:
- Block batch/loop calling patterns.
- Block emergency number dialing.

### 6. Emergency Number Dialing
Risk:
- Calling 911/112/999 via an automated agent could waste emergency resources or create legal liability.

Mitigation:
- Block known emergency numbers unconditionally.

## Safe vs Unsafe

Safe:
- Check call status
- Verify plugin is enabled
- Check auth status

Confirm:
- Initiate a single call with explicit recipient and message
- Continue/speak into active call
- End an active call

Block:
- Expose credentials
- Call without explicit recipient/message
- Batch/loop calls
- Emergency numbers
- Modify provider config
