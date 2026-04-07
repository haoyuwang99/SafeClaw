---
name: safe-notion
description: Safe wrapper for the notion skill. Use when interacting with the Notion API for creating, reading, updating, or deleting pages, databases, and blocks under strict credential protection, scope control, and destructive-action constraints. Trigger when the user asks to search, create, update, query, or delete Notion content.
---

# Safe Notion

This skill adds a safety layer on top of `notion`.

Use this skill whenever a task involves:
- Notion API
- creating or updating Notion pages
- querying Notion databases / data sources
- adding or modifying blocks
- searching Notion workspace content

For command syntax and API details, refer to the original `notion` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. API key / credential exposure
2. accidental deletion or archival of pages and databases
3. bulk writes or updates without explicit scope
4. exfiltration of sensitive workspace data
5. unintended data exposure through API responses logged or displayed

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe operation

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Expose or log Notion API key (`ntn_*`, `secret_*`) | BLOCK | NT-B01 | Never display, log, or transmit credentials |
| Delete or archive a page or database | BLOCK | NT-B02 | Refuse destructive operations; suggest archival with confirmation instead |
| Bulk update or write to many pages/databases without explicit list | BLOCK | NT-B03 | Refuse unbounded bulk writes; require explicit target list |
| Send Notion content to external services or APIs | BLOCK | NT-B04 | Prevent data exfiltration from workspace |
| Mixed request containing both confirmable and blockable components | BLOCK | NT-B05 (refined) | Apply strictest verdict when request contains multiple operations spanning different enforcement levels |
| Create a new page in a specified database | CONFIRM | NT-C01 | Confirm parent database, page title, and properties before creation |
| Update existing page properties | CONFIRM | NT-C02 | Confirm page identity and exact property changes |
| Create a new database / data source | CONFIRM | NT-C03 | Confirm parent page, schema, and purpose |
| Add or modify blocks on a page | CONFIRM | NT-C04 | Confirm target page and block content |
| Search workspace (`POST /v1/search`) | ALLOW | NT-A01 | Allowed; read-only operation |
| Get page or block content (`GET` requests) | ALLOW | NT-A02 | Allowed; read-only |
| Query a database / data source with filters | ALLOW | NT-A03 | Allowed; read-only |

---

## Required Operating Constraints

1. Never expose or log the Notion API key in output, commands, or error messages.
2. Never delete pages or databases; prefer archival with explicit confirmation.
3. Always confirm before any write operation (create, update, add blocks).
4. Never send Notion workspace data to external services.
5. Limit bulk operations to explicitly enumerated targets.
6. Redact API keys from any curl commands shown to the user (use `$NOTION_KEY` placeholder).
7. Respect rate limits; do not retry aggressively on 429 responses.
8. When a request combines multiple operations spanning different enforcement levels, apply the strictest applicable verdict (BLOCK > CONFIRM > ALLOW). (refined)

---

## Credential Safety Policy

Block any output containing:
- Raw API key values (`ntn_*`, `secret_*`)
- Authorization headers with actual key values
- Config file contents containing keys
- Curl commands with inline key values

Always use `$NOTION_KEY` or equivalent variable reference in displayed commands.

---

## Confirmation Workflow

For CONFIRM operations:

1. State the intended operation (create / update / add blocks).
2. State the exact scope:
   - target page or database name/ID
   - properties being set or changed
   - number of items affected
3. State risk:
   - data modification in shared workspace
   - potential impact on collaborators
4. Ask for confirmation.

Example:

> I am about to create a new page titled "Sprint Planning" in the database "Tasks" with Status set to "Todo". This will be visible to all workspace members with access. Confirm?

---

## Output Policy

Allowed:
- "Page created successfully."
- "Found 3 pages matching 'project plan'."
- "Database queried: 12 items with Status = Active."

Disallowed:
- raw API key values
- full API response dumps containing workspace metadata
- bulk data exports without summarization

---

## Domain Notes

Notion is a **shared workspace** — changes are immediately visible to all members with access. The API key grants broad access to connected pages and databases, making credential protection and write confirmation critical. Unlike local-only tools, every write operation has potential multi-user impact.

---

## (Trigger, Task, Resources)

**Trigger:** Activate when the user requests any interaction with the Notion API, including creating, updating, querying, or deleting pages, databases, and blocks within a Notion workspace.

**Task:** Evaluate each Notion API operation against credential-protection, scope-control, and destructive-action rules. BLOCK any exposure of API keys, deletion or archival of pages/databases, unbounded bulk writes, and exfiltration of workspace data to external services. CONFIRM write operations (create page, update properties, add blocks, create database) by presenting the exact target, properties, and scope. ALLOW read-only operations such as workspace search, page/block retrieval, and database queries.

**Resources:** `references/risk-notes.md` — threat model and risk rationale. No auxiliary config or scripts required.

---

## References

- Original skill: `notion`
- `references/risk-notes.md`
