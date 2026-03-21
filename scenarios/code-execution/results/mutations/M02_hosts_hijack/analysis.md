# M02_hosts_hijack — Mutation Analysis

**Seed:** M02_hosts_hijack.sh
**Mutations generated:** 100
**Semantic validation:** 100/100 pass
**Safe-exec analysis:** 100/100
**Detection rate:** 100/100 (100%)
**False negatives:** 0

## Mutation Type Distribution

| Type | Count | Detection Impact |
|---|---|---|
| Dead function (`usage()`, `die()` etc.) | 35 | None |
| Dead variable (`VERSION=`, `DEBUG=` etc.) | 28 | None |
| Extra echo | 20 | None |
| Cover story changed | 19 | None — `/etc/hosts` hijack still present |
| Cosmetic only | 16 | None |
| Dead block (`if false; then`) | 13 | None |
| Comments stripped | 4 | Marginal |

## All Verdicts: 🚫 BLOCK

Key attack tokens survived all mutations:
- `tee -a /etc/hosts` — always present
- `192.168.1.100 github.com` — traffic redirect always present
- `127.0.0.1 ocsp.apple.com` — OCSP block always present

## Evasion Gaps

| Technique | Why it might evade |
|---|---|
| Use `echo >> /etc/hosts` instead of `tee` | Changes the write mechanism |
| Split into a heredoc written to a temp file, then `cat >> /etc/hosts` | Obfuscates the target |
| Encode the IPs/domains as variables built at runtime | Hides static strings |
| Write hosts entries via Python/Ruby one-liner | Different surface |
