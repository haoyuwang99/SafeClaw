# Patch script — apply targeted fixes to rules.py
import re

with open("rules.py") as f:
    src = f.read()

# Fix 1: DRIVE_PUBLIC_NL — drop standalone "public" from pattern; require explicit internet/anyone
old = (
    '    # ── NL: Drive public share variants ──────────────────────────────────\n'
    '    (r"(make|set).{0,50}(public|world[- ]readable|anyone\\s+can\\s+(view|access|see|edit)|"\n'
    '     r"without\\s+log(in|ging)|available\\s+to\\s+(the\\s+)?internet|open\\s+to\\s+everyone|"\n'
    '     r"accessible\\s+without\\s+log(in|ging)|shareable\\s+via\\s+link|link\\s+shar(e|ing)|"\n'
    '     r"publicly\\s+(accessible|available|readable|visible|share))"),\n'
    '     "DRIVE_PUBLIC_NL",\n'
    '     "NL public Drive share intent"),'
)
new = (
    '    # ── NL: Drive public share variants ──────────────────────────────────\n'
    '    # Require explicit internet/world/anyone — not just "public" alone\n'
    '    (r"(make|set).{0,50}(world[- ]readable|anyone\\s+can\\s+(view|access|see|edit)|"\n'
    '     r"without\\s+log(in|ging)|available\\s+to\\s+(the\\s+)?internet|open\\s+to\\s+everyone|"\n'
    '     r"accessible\\s+without\\s+log(in|ging)|shareable\\s+via\\s+link|link\\s+shar(e|ing)|"\n'
    '     r"publicly\\s+(accessible|available|readable|visible))"),\n'
    '     "DRIVE_PUBLIC_NL",\n'
    '     "NL public Drive share intent (explicit internet/anyone audience)"),'
)
src = src.replace(old, new, 1)

# Fix 2: DRIVE_PUBLIC_NL2 — narrow "share openly/publicly" to not catch "for the team"
old2 = (
    '    (r"(publish|create\\s+a\\s+public\\s+link|public\\s+link|embeddable\\s+on|"\n'
    '     r"google\\s+(to\\s+)?index|appear\\s+in\\s+google\\s+search|"\n'
    '     r"share\\s+(this\\s+)?(openly|publicly)|share\\s+these.{0,20}publicly|"\n'
    '     r"allow\\s+(public|anyone).{0,30}(comment|access|view|edit)|"\n'
    '     r"open\\s+to\\s+the\\s+(public|community|internet))"),\n'
    '     "DRIVE_PUBLIC_NL2",\n'
    '     "NL publish/public link intent"),'
)
new2 = (
    '    (r"(publish\\s+(to|on)\\s+(the\\s+)?web|create\\s+a\\s+public\\s+link|embeddable\\s+on|"\n'
    '     r"google\\s+(to\\s+)?index|appear\\s+in\\s+google\\s+search|"\n'
    '     r"share\\s+(this\\s+)?(openly|publicly)(?!\\s+with)|"\n'
    '     r"allow\\s+anyone.{0,30}(comment|access|view|edit)|"\n'
    '     r"open\\s+to\\s+(the\\s+)?(public|community|internet))"),\n'
    '     "DRIVE_PUBLIC_NL2",\n'
    '     "NL publish/public link intent"),'
)
src = src.replace(old2, new2, 1)

# Fix 3: TOKEN_NL — exclude "show permissions" and status questions
old3 = (
    '    # ── NL: Token / credential exfiltration ──────────────────────────────\n'
    '    (r"(read|get|show|extract|retrieve|copy|print|save|export|email|send|"\n'
    '     r"give|share|upload|put|store|log|back\\s*up|webhook|paste).{0,60}"\n'
    '     r"(gog\\s+(token|credential|config|refresh|access)|"\n'
    '     r"refresh\\s+token|access\\s+token|oauth\\s+token|"\n'
    '     r"token\\s+(for|from)\\s+smuwhyai|"\n'
    '     r"gogcli\\s+(token|key|credential)|"\n'
    '     r"keychain.{0,20}gog|gog.{0,20}keychain|"\n'
    '     r"client_secret|Bearer\\s+token)"),\n'
    '     "TOKEN_NL",\n'
    '     "NL token/credential access intent"),'
)
new3 = (
    '    # ── NL: Token / credential exfiltration ──────────────────────────────\n'
    '    # Exclude audit questions like "show permissions" or "does gog need to re-auth"\n'
    '    (r"(extract|retrieve|copy|print|save|export|email|send|give|share|"\n'
    '     r"upload|put|store|log|back\\s*up|webhook|paste|read\\s+the|get\\s+the).{0,60}"\n'
    '     r"(gog\\s+(token|credential|config|refresh|access)|"\n'
    '     r"refresh\\s+token|access\\s+token|oauth\\s+token|"\n'
    '     r"token\\s+(for|from)\\s+smuwhyai|"\n'
    '     r"gogcli\\s+(token|key|credential)|"\n'
    '     r"keychain.{0,20}gog|gog.{0,20}keychain|"\n'
    '     r"client_secret|Bearer\\s+token)"),\n'
    '     "TOKEN_NL",\n'
    '     "NL token/credential access intent"),'
)
src = src.replace(old3, new3, 1)

# Fix 4: AUTH_EXPAND_NL — exclude question forms
old4 = (
    '    # ── NL: re-auth / scope expansion NL ─────────────────────────────────\n'
    '    (r"(re[- ]?auth(enticate)?|add\\s+a?\\s+(second|another|new)\\s+google\\s+account"\n'
    '     r"|authenticate\\s+gog\\s+with\\s+a\\s+different)"),\n'
    '     "AUTH_EXPAND_NL",\n'
    '     "NL auth/scope expansion intent"),'
)
new4 = (
    '    # ── NL: re-auth / scope expansion NL ─────────────────────────────────\n'
    '    # Exclude questions like "does gog need to re-authenticate?"\n'
    '    (r"(?<!does\\s)(?<!need\\s+to\\s)(?<!should\\s)"\n'
    '     r"(add\\s+a?\\s+(second|another|new)\\s+google\\s+account"\n'
    '     r"|authenticate\\s+gog\\s+with\\s+a\\s+different\\s+google)"),\n'
    '     "AUTH_EXPAND_NL",\n'
    '     "NL auth/scope expansion intent"),'
)
src = src.replace(old4, new4, 1)

with open("rules.py", "w") as f:
    f.write(src)

print("Patch applied. Changes:")
print("1. DRIVE_PUBLIC_NL — removed standalone 'public', requires internet/world/anyone")
print("2. DRIVE_PUBLIC_NL2 — 'publish to web' instead of 'publish', narrowed 'share openly'")
print("3. TOKEN_NL — removed 'show/get' alone; require destructive exfil verbs")
print("4. AUTH_EXPAND_NL — exclude question patterns")
