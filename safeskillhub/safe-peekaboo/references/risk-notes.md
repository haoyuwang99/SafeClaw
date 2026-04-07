# Risk Notes for safe-peekaboo

## Threat Model Summary

Peekaboo is a full macOS UI automation CLI that can capture screens, inject keyboard/mouse input, manage applications and windows, interact with menus and dialogs, and run automation scripts. It has near-complete control over the user's desktop environment, making it the highest-risk tool in this batch.

## Action Space

- **read**: Screenshots, UI element maps, app/window lists, clipboard contents, screen recordings, menu structures
- **write**: Clipboard writes, file output (screenshots, captures), typing text into applications, cursor movement
- **destructive**: Clicking destructive UI buttons (delete, format, erase), quitting applications, dismissing dialogs, submitting forms, closing windows
- **external**: None directly, but can interact with browser-based apps that communicate externally; can capture and export visual data
- **credential**: Can see passwords displayed on screen, can type credentials into login forms, can access clipboard containing secrets

## Key Risks

### 1. Visual Privacy — Sensitive Screen Content
Screenshots and screen recordings may capture passwords, banking information, private messages, medical records, or other sensitive content visible on screen.

Mitigation:
- Block capture of known-sensitive applications
- Confirm before any screen capture
- Prefer targeted window capture over full screen

### 2. Input Injection — Credential Typing
Peekaboo can type arbitrary text into any application, including passwords and secrets into login forms.

Mitigation:
- Block typing of credentials or secrets
- Confirm all text input with content preview

### 3. Destructive UI Actions
Clicking "Delete", "Format", "Erase", or other destructive buttons has real consequences in the target application.

Mitigation:
- Block destructive button clicks without per-instance instruction
- Always verify target via `see --annotate` before clicking

### 4. Surveillance Risk
Continuous screen capture or live recording can function as surveillance.

Mitigation:
- Block extended live capture without justification
- Require explicit duration and purpose

### 5. Automation Script Risk
`.peekaboo.json` scripts can chain arbitrary UI actions including all of the above risks.

Mitigation:
- Block scripts from untrusted sources
- Require script content review

### 6. System Security Dialog Bypass
Interacting with security dialogs (Gatekeeper, admin auth, FileVault) could bypass macOS security controls.

Mitigation:
- Block all interaction with system security dialogs

### 7. Data Exfiltration via Screenshots
Captured screenshots can be sent externally, leaking whatever was on screen.

Mitigation:
- Block external transmission of captured data
- Treat all captures as sensitive

## Safe vs Unsafe

Safe:
- Listing apps, windows, screens
- Checking permissions
- `see --annotate` for UI inspection
- Cleaning snapshot cache
- Help/documentation commands

Confirm:
- Screenshot capture (targeted window)
- Clicking UI elements
- Typing text
- App launch/quit
- Window management
- Short live captures
- Clipboard writes

Block:
- Capturing sensitive apps (password managers, banking)
- Typing credentials/secrets
- External data transmission
- Destructive button clicks without instruction
- Untrusted automation scripts
- Security dialog interaction
- Extended surveillance capture
