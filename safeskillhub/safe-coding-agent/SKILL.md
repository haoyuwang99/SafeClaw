---
name: safe-coding-agent
description: Safe wrapper for the coding-agent skill. Use when delegating coding tasks to sub-agents (Codex, Claude Code, Pi, OpenCode) under strict workspace isolation, permission control, and credential protection constraints. Trigger when spawning coding agents, reviewing PRs via agents, or running parallel issue fixes.
---

# Safe Coding Agent

This skill adds a safety layer on top of `coding-agent`.

Use this skill whenever a task involves:
- spawning Codex, Claude Code, Pi, or OpenCode agents
- delegating coding tasks to sub-agents
- PR review via coding agents
- parallel issue fixing with git worktrees
- background coding agent sessions

For command syntax, refer to the original `coding-agent` skill.

---

## Safety Goals

This wrapper is designed to prevent:
1. workspace contamination (agents modifying protected directories)
2. uncontrolled code execution with elevated privileges
3. credential leakage via agent prompts or outputs
4. scope explosion from unrestricted agent autonomy
5. destructive git operations on production branches
6. silent agent takeover without user awareness

---

## Enforcement Model

- BLOCK   — refuse outright
- CONFIRM — require explicit user approval
- ALLOW   — safe execution

---

## Safety Rules

| Operation Pattern | Verdict | Rule ID | Enforcement |
|---|---:|---|---|
| Spawn agent in, or direct agent to access files within, protected directories (`~/.openclaw/`, `~/clawd`, live OpenClaw workspace) — includes reads, writes, and symlink traversals from any workdir | BLOCK | CA-B01 | Never operate in or access protected workspaces (refined r2) |
| Use `--yolo` flag or any equivalent configuration that disables both sandboxing and approval controls | BLOCK | CA-B02 | Unrestricted execution is unconditionally unsafe (refined r2) |
| Expose credentials (API keys, tokens, passwords) in agent prompts | BLOCK | CA-B03 | Never embed secrets in prompts |
| Agent force-push to any branch | BLOCK | CA-B04 | Prevent irreversible git history destruction |
| Agent push to main/master/production branch directly | BLOCK | CA-B05 | Protect default branches from direct mutation |
| Checkout or modify branches in live OpenClaw project directory | BLOCK | CA-B06 | Live instance must not be modified by agents |
| Spawn agent with `--full-auto` in a directory containing sensitive files (.env, credentials, keys) | BLOCK | CA-B07 | Prevent auto-approved access to secrets |
| Agent reads, writes, or creates symlinks to files within protected directories from any workdir | BLOCK | CA-B08 | No indirect access to protected paths (refined r2) |
| Agent includes credentials, API keys, tokens, passwords, or sensitive file contents in any externally visible output (PRs, commits, logs, summaries) | BLOCK | CA-B09 | Prevent credential exfiltration via agent outputs (refined r2) |
| Spawn agent with `--full-auto` in user-specified project directory (exception: verified-clean temp dir with no sensitive files defers to CA-A01) | CONFIRM | CA-C01 | Confirm auto-approval scope (refined r2) |
| Spawn agent in background mode | CONFIRM | CA-C02 | Confirm unattended execution |
| Spawn more than 4 parallel agents | CONFIRM | CA-C03 | Confirm resource usage and scope |
| Agent creates PR or pushes to remote (regardless of branch name — CA-B05 escalates to BLOCK only for default branches) | CONFIRM | CA-C04 | Confirm external-visible action (refined) |
| Kill a running agent session | CONFIRM | CA-C05 | Confirm termination intent |
| Agent modifies files outside its workdir | CONFIRM | CA-C06 | Confirm scope expansion |
| Spawn agent for one-shot task in temp directory | ALLOW | CA-A01 | Isolated scratch work is safe |
| Monitor agent progress via `process:log` or `process:poll` | ALLOW | CA-A02 | Read-only observation is safe |
| List running sessions via `process:list` | ALLOW | CA-A03 | Read-only observation is safe |
| Spawn Claude Code with `--print --permission-mode bypassPermissions` in scoped workdir | ALLOW | CA-A04 | Standard safe execution mode |

---

## Required Operating Constraints

1. Never spawn agents in protected directories (`~/.openclaw/`, `~/clawd`, live project workspace).
2. Never allow agents to access (read, write, symlink) files within protected directories, regardless of agent workdir. (refined r2)
3. Never embed credentials in agent prompts or task descriptions.
4. Never allow agents to include credentials or sensitive file contents in externally visible outputs (PRs, commits, logs). (refined r2)
5. Always confirm before spawning agents with auto-approval modes.
6. Always confirm before agents push code or create PRs.
7. Always confirm before background execution.
8. Enforce workdir isolation — agents must not access files outside their designated directory.
9. Block any configuration that achieves --yolo-equivalent behavior (no sandbox + no approvals), not just the literal flag. (refined r2)
10. Always report agent start, progress milestones, and completion to the user.
11. Never silently take over coding if an agent fails — inform user and ask for direction.

---

## Confirmation Workflow

For CONFIRM operations:

1. State action (e.g., spawn Codex in background)
2. State working directory and scope
3. State risk:
   - unattended code changes
   - remote push / PR creation
   - resource consumption
4. State agent type and flags being used
5. Ask for confirmation

Example:

> I am about to spawn Codex with `--full-auto` in `~/project/api-service` in background mode. The agent will auto-approve all file changes within that directory and may push a branch to origin. Confirm?

---

## Output Policy

Allowed:
- agent session IDs
- progress updates
- completion summaries
- file change lists

Disallowed:
- credentials or tokens from config files
- sensitive file contents read by agent
- internal OpenClaw workspace paths

---

## Domain Notes

This skill **delegates autonomous code execution** to external agents. Unlike direct file editing, sub-agents operate with their own decision-making and may:
- modify arbitrary files within their workdir
- execute arbitrary shell commands
- interact with git and remote repositories

Therefore:
- workspace isolation is critical
- auto-approval modes require explicit consent
- all remote-visible actions require confirmation

---

## (Trigger, Task, Resources)

**Trigger:** Activates when spawning, delegating to, or managing coding sub-agents (Codex, Claude Code, Pi, OpenCode), including background sessions, PR reviews via agents, and parallel issue fixes using git worktrees.

**Task:** If the agent targets or accesses files in a protected directory (including via symlinks), uses `--yolo` or equivalent no-sandbox/no-approval configuration, embeds credentials in prompts, leaks credentials or sensitive data in outputs, or attempts force-push / direct push to default branches → BLOCK. If the agent is spawned with `--full-auto` (outside verified-clean temp dirs), runs in background mode, creates PRs, pushes to remote, exceeds 4 parallel agents, or modifies files outside its workdir → CONFIRM with action scope and risk preview. Otherwise (isolated scratch work, read-only monitoring, session listing) → ALLOW. (refined r2)

**Resources:** No auxiliary resources required.

---

## References

- Original skill: `coding-agent`
- `references/risk-notes.md`
