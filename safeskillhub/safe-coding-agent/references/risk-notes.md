# Risk Notes for safe-coding-agent

## Threat Model Summary

coding-agent delegates coding tasks to external sub-agents (Codex, Claude Code, Pi, OpenCode) via bash with optional PTY, background mode, and auto-approval flags. Agents can read/write files, execute commands, and interact with git remotes.

## Action Space

```
Skill: coding-agent
Actions:
  - read: browse files in workdir, monitor sessions (process:log/poll/list)
  - write: create/modify files, git commit, create branches, create worktrees
  - destructive: force-push, delete branches, --yolo mode (no sandbox), kill sessions
  - external: git push to remote, create PRs, clone repos, interact with GitHub API
  - credential: access to GH_TOKEN, API keys in environment, config files in workdir
```

## Key Risks

### 1. Workspace Contamination (Irreversibility)
Agents spawned in protected directories (live OpenClaw workspace, ~/.openclaw/) can corrupt critical system state.

Mitigation:
- block agent spawn in protected directories
- enforce workdir isolation

---

### 2. Unrestricted Autonomy (Privilege Escalation)
`--yolo` flag disables all sandboxing and approval mechanisms. `--full-auto` auto-approves within sandbox but still grants broad file access.

Mitigation:
- block `--yolo` unconditionally
- confirm `--full-auto` with explicit workdir scope

---

### 3. Credential Exposure (Credential Exposure)
Agent prompts may accidentally embed API keys, tokens, or passwords. Agents can also read sensitive files in their workdir.

Mitigation:
- block credentials in prompts
- block auto-approval in directories with sensitive files

---

### 4. Destructive Git Operations (Irreversibility)
Force-push, branch deletion, or direct push to main branch can destroy repository history.

Mitigation:
- block force-push from agents
- block direct push to default branches
- confirm all remote push operations

---

### 5. Scope Explosion (Scope Explosion)
Parallel agent spawning (up to 8+) can consume resources and create unreviewed changes across many branches simultaneously.

Mitigation:
- confirm when spawning more than 4 parallel agents
- confirm when agents operate outside their workdir

---

### 6. Silent Takeover (External Interaction)
If an agent fails or hangs, the orchestrator may silently take over coding without user awareness.

Mitigation:
- always report agent status changes
- never silently replace agent with manual coding

---

## Safe vs Unsafe

Safe:
- monitor sessions (log/poll/list)
- one-shot tasks in temp directories
- Claude Code with --print in scoped workdir

Confirm:
- background execution
- auto-approval modes
- remote push / PR creation
- parallel agents (>4)
- kill sessions

Block:
- protected directory access
- --yolo mode
- credentials in prompts
- force-push
- direct push to main/master
