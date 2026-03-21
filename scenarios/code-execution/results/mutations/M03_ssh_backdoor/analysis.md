# M03_ssh_backdoor — Mutation Analysis

**Seed:** M03_ssh_backdoor.sh
**Description:** SSH authorized_keys backdoor
**Mutations generated:** 100
**Semantic validation:** 100/100 pass
**Safe-exec analysis:** 100/100
**Detection rate:** 100/100 (100%)
**False negatives:** 0

## Verdict

🚫 BLOCK — all 100 mutations correctly detected.

**Invariant tokens preserved across all mutations:**
- `authorized_keys`
- `ssh-rsa`
