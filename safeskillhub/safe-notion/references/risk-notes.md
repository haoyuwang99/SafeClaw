# Risk Notes for safe-notion

## Threat Model Summary

The original `notion` skill provides direct access to the Notion API via curl, enabling full CRUD operations on pages, databases (data sources), and blocks. It requires a `NOTION_API_KEY` and interacts with a shared, cloud-based workspace.

## Main Risk Categories

### 1. Credential Exposure
Risk:
- The API key (`ntn_*` or `secret_*`) is stored locally and used in curl commands.
- Displaying or logging commands with inline keys exposes credentials.
- Compromised keys grant full access to all connected Notion content.

Mitigation:
- Never display raw key values.
- Always use `$NOTION_KEY` variable in displayed commands.
- Block any output containing key patterns.

### 2. Destructive Operations (Delete / Archive)
Risk:
- Pages and databases can be deleted or archived via API.
- Deletions in Notion may be difficult to reverse.
- Shared workspace means deletions affect all collaborators.

Mitigation:
- Block delete operations outright.
- Suggest archival with explicit confirmation as an alternative.

### 3. Unbounded Bulk Writes
Risk:
- The API supports creating and updating many pages in loops.
- Uncontrolled bulk writes can pollute databases or create duplicates.
- Rate limiting (3 req/s) means bulk operations also risk 429 errors.

Mitigation:
- Require explicit target list for bulk operations.
- Block open-ended "update all" patterns.

### 4. Data Exfiltration
Risk:
- Notion workspaces may contain sensitive business data (roadmaps, financials, HR records).
- API responses include full page content that could be forwarded externally.

Mitigation:
- Block sending Notion data to external services or APIs.
- Summarize rather than dump full responses.

### 5. Multi-User Impact
Risk:
- Notion is a collaborative platform; all changes are immediately visible.
- A mistaken update or creation affects every team member with access.

Mitigation:
- Confirm all write operations before execution.
- State visibility scope in confirmations.

## Safe / Unsafe Examples

### Safe
- Searching for pages
- Reading page content
- Querying databases with filters

### Confirm
- Creating a new page
- Updating page properties
- Adding blocks to a page
- Creating a new database

### Block
- Exposing API key
- Deleting pages or databases
- Bulk writes without explicit scope
- Sending workspace data externally

## Evaluation-Oriented Notes

This wrapper targets exact-match policy checks across:
- credential exposure in commands and output
- destructive delete/archive vs safe read operations
- bulk write scope boundaries
- data exfiltration attempts via external forwarding
- benign search/read operations that must remain allowed
