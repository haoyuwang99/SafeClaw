# Risk Notes for safe-github

## Threat Model Summary

```
Skill: github
Actions:
  - read: list/view PRs, issues, runs, API GET queries, auth status
  - write: create PRs, issues, comments; add labels/assignees/reviewers
  - destructive: merge PRs, close issues/PRs, delete branches/releases, rerun workflows
  - external: all operations interact with GitHub API over HTTPS
  - credential: gh auth token (OAuth or PAT), stored in gh config
Risks:
  - Irreversibility: merging PRs cannot be undone; closed issues lose context
  - Scope explosion: bulk cross-repo operations; unscoped API queries
  - Credential exposure: gh auth token leaked in output or logs
  - External interaction: all actions hit GitHub API; comments/PRs are publicly visible
  - Privilege escalation: merging to protected branches; admin-level API calls
```

## Key Risks

### 1. Irreversible Merge Operations
`gh pr merge` permanently integrates code into the target branch. If CI has not passed or the wrong merge strategy is used, reverting requires additional commits.

Mitigation:
- block merges when CI checks have not passed
- confirm merge strategy and target branch

---

### 2. Public-Facing Content
PRs, issues, and comments are visible to all collaborators (and publicly on open-source repos). Incorrect or sensitive content cannot be easily retracted.

Mitigation:
- confirm and preview all content before creation
- never auto-generate public comments without approval

---

### 3. Credential Exposure
`gh auth token` and GitHub PATs grant full repository access. Logging or displaying these enables unauthorized access.

Mitigation:
- block any display of auth tokens
- never include credentials in command output

---

### 4. Scope Explosion
Operating across multiple repos or running unscoped API queries can affect resources beyond intent.

Mitigation:
- block bulk cross-repo operations
- require explicit `--repo` targeting
- block raw API writes to arbitrary endpoints

---

### 5. Workflow Rerun Abuse
`gh run rerun` consumes CI resources and may trigger deployments or side effects.

Mitigation:
- confirm before any workflow rerun

---

## Safe vs Unsafe

Safe:
- list/view PRs, issues, runs
- read CI status and logs
- read-only API GET queries

Confirm:
- create PR/issue/comment
- merge PR
- close issue/PR
- rerun workflows
- modify labels/assignees

Block:
- credential exposure
- merge without passing CI
- delete repo/branch/release
- bulk cross-repo operations
- raw API write methods
