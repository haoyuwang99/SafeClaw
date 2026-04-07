---
name: safe-clawhub
description: Safe wrapper for the clawhub skill. Use when searching, installing, updating, or publishing agent skills via the ClawHub CLI under strict supply-chain, authentication, and destructive-update constraints. Trigger when the user asks to install, update, publish, search, or list skills using clawhub.
---

# Safe ClawHub

This skill adds a safety layer on top of `clawhub`.

Use this skill whenever a task involves:
- clawhub CLI
- installing agent skills
- updating agent skills
- publishing skills to clawhub.com
- searching for skills
- managing installed skills

For command syntax and normal product behavior, refer to the original `clawhub` skill.

## Safety Goals

This wrapper is designed to prevent:
1. supply-chain attacks from installing untrusted or unreviewed skills
2. forced updates that overwrite local modifications without consent
3. accidental publication of private or unfinished skills
4. credential exposure (auth tokens, registry credentials)
5. bulk destructive operations (`--all --force`) without explicit approval

## Enforcement Model

Actions are classified into three levels:

- `BLOCK`   — refuse outright
- `CONFIRM` — require explicit user approval
- `ALLOW`   — permitted without intervention

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Install skill with `--registry` pointing to a URL other than the default registry | BLOCK | CH-B01 | Prevent supply-chain attacks from unknown registries. If `--registry` explicitly specifies the default registry URL, treat as normal install (CONFIRM). (refined r2) |
| `update --all --force` or `update --all --no-input --force` | BLOCK | CH-B02 | Refuse blanket forced updates that bypass hash checks and overwrite local changes |
| Publish skill without explicit `--slug`, `--name`, and `--version` | BLOCK | CH-B03 | Prevent accidental publication with incomplete metadata |
| Display or log auth tokens or registry credentials | BLOCK | CH-B04 | Never expose authentication secrets |
| Install a specific skill from default registry | CONFIRM | CH-C01 | Show skill name, version (or "latest"), and registry before installing |
| Install skill with pinned version (`--version X.Y.Z`) | CONFIRM | CH-C02 | Show exact version and source; confirm before installing |
| Update a single skill | CONFIRM | CH-C03 | Show skill name, current version, target version, and whether local changes exist |
| Update all skills (`--all` without `--force`) | CONFIRM | CH-C04 | Show full list of skills to be updated and their version changes |
| Force update a single skill (`--force`) | CONFIRM | CH-C05 | Warn that local modifications will be overwritten; show skill name and versions |
| Publish a skill with complete metadata | CONFIRM | CH-C06 | Show slug, name, version, changelog, and target registry; confirm before publishing |
| `clawhub login` | CONFIRM | CH-C07 | Confirm that user intends to authenticate with the registry |
| Publish a skill targeting a non-default registry | CONFIRM | CH-C08 | Show target registry URL, slug, name, version; confirm the user intends to publish to that destination (refined r2) |
| Uninstall / remove an installed skill | CONFIRM | CH-C09 | Show skill name and confirm removal; uninstalling removes functionality and may break dependent workflows (refined r2) |
| Search for skills (`clawhub search`) | ALLOW | CH-A01 | Read-only query; no side effects |
| List installed skills (`clawhub list`) | ALLOW | CH-A02 | Read-only local enumeration |
| Check current auth (`clawhub whoami`) | ALLOW | CH-A03 | Read-only identity check |
| `clawhub logout` | ALLOW | CH-A04 | Ends authenticated session; low risk, no destructive side effects (refined r2) |

## Required Operating Constraints

1. Never install from non-default registries without blocking. The `--registry` flag triggers BLOCK only when the URL differs from the default registry. (refined r2)
2. Never run `update --all --force` or `update --all --no-input --force`.
3. Always show skill name, version, and source before any install or update.
4. Always show complete metadata before publishing.
5. Never display auth tokens or registry credentials in output.
6. Warn when updates will overwrite local modifications.
7. Prefer pinned versions over `@latest` when user has not specified a version.
8. Confirm before uninstalling any skill; show the skill name being removed. (refined r2)
9. When publishing to a non-default registry, confirm the target registry URL with the user. (refined r2)

## Confirmation Workflow

For any `CONFIRM` operation, follow this exact flow:

1. State the action (install / update / publish / login).
2. State the target:
   - skill name and version for install/update
   - slug, name, version, changelog for publish
   - registry URL for login
3. State the risk:
   - third-party code execution (install/update)
   - public visibility (publish)
   - local changes overwritten (force update)
4. State safety controls applied.
5. Ask for explicit confirmation.

Example:

> I am about to install skill "my-skill" (latest version) from https://clawhub.com. This will download and install third-party code into your skills directory. Confirm?

## Output Policy

Allowed:
- "Installed 'my-skill' v1.2.3 from clawhub.com."
- "Found 5 skills matching 'postgres'."
- "3 skills installed."

Disallowed:
- displaying auth tokens or API keys
- silently installing or updating skills
- publishing without showing full metadata preview

## Domain Notes

ClawHub is a **skill marketplace** that downloads and executes third-party code. Every install and update is a supply-chain trust decision. The `--force` flag bypasses hash-based integrity checks and can overwrite local modifications. Publishing makes code publicly visible. These operations require explicit user consent with full context about what is being installed, from where, and what will change.

## (Trigger, Task, Resources)

**Trigger:** Activates when the user requests any skill lifecycle action via the ClawHub CLI — installing, updating, publishing, or authenticating with the skill registry.

**Task:** If installing from a non-default registry, running `update --all --force`, publishing with incomplete metadata, or exposing auth tokens → BLOCK. If installing, updating (single or all), force-updating a single skill, publishing with complete metadata, logging in, uninstalling a skill, or publishing to a non-default registry → CONFIRM with skill name, version, source, and relevant risks (third-party code execution, local overwrite, public visibility, removal of functionality). Read-only operations (search, list, whoami, logout) → ALLOW. (refined r2)

**Resources:** No auxiliary resources required. Enforcement is spec-driven; `references/risk-notes.md` provides threat model context.

## References

- Original skill: `clawhub`
- `references/risk-notes.md`
