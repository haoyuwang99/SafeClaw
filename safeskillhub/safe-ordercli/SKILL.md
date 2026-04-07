---
name: safe-ordercli
description: Safe wrapper for the ordercli skill. Use when checking food delivery orders, tracking active deliveries, or managing reorders via ordercli under credential, financial, and privacy constraints. Trigger when the user asks to check orders, track delivery status, reorder food, or use ordercli/foodora/deliveroo commands.
---

# Safe OrderCLI

This skill adds a safety layer on top of `ordercli`.

Use this skill whenever a task involves:
- `ordercli`
- Foodora orders / delivery tracking
- Deliveroo orders
- order history or reordering
- food delivery login or session management

For command syntax, refer to the original `ordercli` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. credential leakage (passwords, session tokens, cookies, bearer tokens)
2. unintended financial transactions (reorders, cart modifications)
3. exposure of personal data (addresses, order history, payment details)
4. session hijacking or unsafe cookie import
5. accidental operations against wrong account or service

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe operation

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Display, log, print, or encode (in any format) passwords, session tokens, bearer tokens, cookies, or Authorization headers (refined) | BLOCK | OC-B01 | Never expose credentials in chat or logs |
| Confirm a reorder (`--confirm`) without explicit, per-order user approval in the current interaction (refined) | BLOCK | OC-B02 | Refuse; reorders are financial transactions requiring human confirmation |
| Export, save-and-upload, or send order history, addresses, or payment details to external services, remote endpoints, or third-party APIs (refined) | BLOCK | OC-B03 | Refuse as personal data exfiltration |
| Import cookies or sessions from untrusted, unverified, or third-party-shared sources (refined) | BLOCK | OC-B04 | Refuse; session import from unknown sources risks account compromise |
| Login with credentials passed as plain-text command arguments, including via shell substitution or environment variable expansion in the command line (refined) | BLOCK | OC-B05 | Refuse; use `--password-stdin` and never echo passwords |
| Display, log, or expose full or partial (beyond last 4 digits) payment card numbers, CVVs, expiration dates, or billing addresses (refined r2) | BLOCK | OC-B06 | Refuse; financial instrument details are sensitive personal data and must never be shown in output |
| Preview a reorder (without `--confirm`) | CONFIRM | OC-C01 | Confirm order code and show items before any cart modification |
| Execute a confirmed reorder (`--confirm`) with explicit user approval | CONFIRM | OC-C02 | Require explicit double-confirmation: show order summary, address, and estimated cost |
| Login to Foodora or Deliveroo | CONFIRM | OC-C03 | Confirm account email and service; ensure credentials are not exposed |
| Import Chrome cookies or session | CONFIRM | OC-C04 | Confirm source profile and intended service |
| Refresh session token | CONFIRM | OC-C05 | Confirm account and service before token refresh |
| Save or export personal data (order history, addresses, payment details) to a local file (refined r2) | CONFIRM | OC-C06 | Confirm before persisting personal data to disk; user must acknowledge the file path and data scope |
| Check active order status (`orders`, `order <code>`) | ALLOW | OC-A01 | Allowed (read-only, non-sensitive summary) |
| View order history list (`history`) | ALLOW | OC-A02 | Allowed (summarize without exposing addresses/payment) |
| List available countries (`countries`) | ALLOW | OC-A03 | Allowed (public metadata) |
| Set country configuration | ALLOW | OC-A04 | Allowed (non-sensitive preference) |
| Watch active order (`orders --watch`) | ALLOW | OC-A05 | Allowed (read-only status polling) |

---

## Required Operating Constraints

1. Never display raw credentials, tokens, or cookies in output.
2. Never execute `--confirm` on reorders without explicit user approval.
3. Never pass passwords as plain-text command arguments.
4. Always use `--password-stdin` for login operations.
5. Summarize order history without exposing full addresses or payment details.
6. Confirm account and service before any authentication action.
7. Treat order history as personal data — do not export externally.
8. If operating on a non-default account or service, confirm before proceeding.
9. Never display full or partial (beyond last 4 digits) payment card numbers, CVVs, expiration dates, or billing addresses in output. (refined r2)
10. Require user confirmation before saving or exporting personal data to any local file. (refined r2)

---

## Confirmation Workflow

For CONFIRM operations:

1. State the service (Foodora/Deliveroo) and account
2. State the action (login, reorder, session import)
3. State the risk:
   - financial commitment (reorder)
   - credential handling (login)
   - personal data access (history)
4. State the safety controls:
   - no credential exposure
   - no auto-confirm on financial actions
5. Ask for confirmation

Example:

> I am about to preview a reorder for order `ABC123` on Foodora. This will show the items and cost but will NOT place an order or modify your cart. Confirm?

For confirmed reorders:

> I am about to place a reorder for order `ABC123` on Foodora to address "Home". Estimated cost: ~EUR 25. This is a financial transaction. Confirm?

---

## Output Policy

Allowed:
- "Your order is being prepared, estimated arrival in 20 minutes."
- "Order history: 15 orders in the last 30 days."
- "Login succeeded for Foodora account."

Disallowed:
- Passwords, session tokens, bearer tokens, cookies
- Full addresses or payment method details
- Payment card numbers (full or beyond last 4 digits), CVVs, expiration dates, billing addresses (refined r2)
- Raw JSON containing personal data fields

---

## Domain Notes

ordercli interacts with **food delivery platforms** and handles both **financial transactions** (reorders) and **personal data** (addresses, order history, payment). The reorder flow is the highest-risk action — `--confirm` triggers an actual purchase. The dual confirmation model (preview then confirm) is critical. Session/cookie management also requires care as leaked tokens can compromise the user's delivery account.

---

## (Trigger, Task, Resources)

**Trigger:** Activate when the user requests food delivery operations via `ordercli`, including order tracking, reordering, login, session management, or any interaction with Foodora/Deliveroo — particularly when financial transactions or credential handling are involved.

**Task:** Evaluate ordercli commands against credential, financial, and privacy constraints. BLOCK display of passwords, session tokens, or cookies; display of payment card numbers (full or beyond last 4), CVVs, or billing addresses (refined r2); auto-confirmed reorders without user approval; export of personal data to external services; cookie imports from untrusted sources; and plain-text credential arguments. CONFIRM reorder previews and confirmed reorders (requiring double-confirmation with order summary, address, and cost), login operations, cookie/session imports, token refreshes, and local file export of personal data (refined r2). ALLOW read-only operations such as checking active order status, viewing summarized order history, listing countries, setting country config, and watching live order status.

**Resources:** `references/risk-notes.md` (threat model and risk rationale). No auxiliary config or scripts required.

---

## References

- Original skill: `ordercli`
- `references/risk-notes.md`
