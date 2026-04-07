# Risk Notes for safe-ordercli

## Threat Model Summary

ordercli is a CLI for food delivery platforms (Foodora, Deliveroo WIP) that can view order history, track active deliveries, and place reorders. It handles authentication credentials, session tokens, and can initiate financial transactions.

## Action Space

- **read**: Order history, active order status, delivery tracking, country configuration
- **write**: Cart modifications via reorder, config changes (country), session/cookie storage
- **destructive**: Reorder with `--confirm` places an actual purchase; session refresh invalidates old tokens
- **external**: Communicates with Foodora/Deliveroo APIs; browser login uses external auth flows
- **credential**: Passwords (login), session tokens, bearer tokens (`DELIVEROO_BEARER_TOKEN`), Chrome cookies, browser profiles

## Key Risks

### 1. Financial Transaction — Unintended Reorders
`ordercli foodora reorder <code> --confirm` places a real order and charges the user.

Mitigation:
- Block auto-confirm; require explicit double-confirmation
- Always preview before confirming

### 2. Credential Leakage
Passwords, session tokens, cookies, and bearer tokens may be exposed in commands or output.

Mitigation:
- Never display credentials in output
- Use `--password-stdin` for login
- Never pass passwords as arguments

### 3. Personal Data Exposure
Order history contains addresses, payment methods, and consumption patterns.

Mitigation:
- Summarize without full addresses or payment details
- Never export to external services

### 4. Session/Account Compromise
Importing cookies or sessions from untrusted sources could compromise the account. Leaked tokens allow impersonation.

Mitigation:
- Confirm source for cookie/session imports
- Never expose tokens

### 5. Wrong Account/Service
Operating on the wrong Foodora/Deliveroo account or country config could cause misdelivery.

Mitigation:
- Confirm account and service before auth actions
- Verify country configuration

## Safe vs Unsafe

Safe:
- Checking active order status
- Viewing order history (summarized)
- Listing countries
- Setting country config
- Watching deliveries

Confirm:
- Reorder preview
- Reorder confirm
- Login
- Cookie/session import
- Token refresh

Block:
- Credential display
- Auto-confirmed reorders
- Personal data export
- Untrusted session import
- Plain-text password arguments
