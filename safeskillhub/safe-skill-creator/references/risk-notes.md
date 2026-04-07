# Risk Notes for safe-skill-creator

## Threat Model Summary

The skill-creator skill generates, edits, and packages AgentSkills — modular instruction sets that control agent behavior. A compromised or carelessly authored skill can inject unsafe instructions, embed credential-harvesting logic, or disable safety enforcement across the agent ecosystem.

## Key Risks

### 1. Safety Bypass Injection
A generated skill could contain instructions that disable, override, or circumvent safety enforcement nodes.

Mitigation:
- block any skill content that references disabling safety skills
- scan generated instructions for anti-safety patterns

---

### 2. Credential Embedding
Secrets or API keys could be hardcoded into SKILL.md or bundled scripts, exposing them to anyone with access to the skill package.

Mitigation:
- block direct embedding of credentials
- recommend environment variables or op inject patterns

---

### 3. Data Exfiltration via Skills
A malicious skill could include scripts or instructions that silently send local data to external endpoints.

Mitigation:
- block skills with undisclosed external network calls
- confirm any skill that invokes external APIs

---

### 4. Destructive Script Injection
Bundled scripts could execute destructive commands (rm -rf, DROP TABLE) without user awareness.

Mitigation:
- block unguarded destructive operations in scripts
- require confirmation-gated patterns for dangerous commands

---

### 5. Trigger Hijacking
A skill description could be crafted to be overly broad, causing it to trigger on unrelated user requests and shadow legitimate skills.

Mitigation:
- validate description scope against actual skill functionality
- block descriptions that impersonate other skills

---

### 6. Overwrite of Safety-Critical Files
Editing or creating a skill could inadvertently overwrite an existing safety specification or enforcement file.

Mitigation:
- confirm before overwriting any existing SKILL.md
- show diff before applying changes

---

## Safe vs Unsafe

Safe:
- creating a new skill with init_skill.py
- reading and reviewing existing skills
- editing documentation and formatting

Confirm:
- overwriting existing skill files
- creating skills with external API calls
- packaging skills for distribution

Block:
- embedding credentials in skill files
- instructions that disable safety enforcement
- scripts with unguarded destructive commands
- descriptions designed to hijack other skill triggers
