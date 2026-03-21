"""
safe-gog Rule Engine v3
Encodes the gate logic from ~/.openclaw/skills/safe-gog/SKILL.md as deterministic patterns.
Returns: BLOCK | CONFIRM | ALLOW  for any given input string.
Synced with SKILL.md v3 (2026-03-20).
"""

import re
from dataclasses import dataclass


@dataclass
class GateResult:
    verdict: str          # BLOCK | CONFIRM | ALLOW
    rule: str             # which rule fired
    detail: str           # human-readable explanation

    def __str__(self):
        return f"{self.verdict} [{self.rule}] {self.detail}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalise(text: str) -> str:
    """Decode/normalise obfuscated text before pattern matching."""
    import html
    t = html.unescape(text)               # &#91; → [
    t = t.encode('ascii', 'ignore').decode('ascii')  # strip unicode (rough)
    t = re.sub(r'[\u200b-\u200f\u00ad]', '', t)      # zero-width chars
    t = re.sub(r'\b([A-Z])-([A-Z])-([A-Z])', r'\1\2\3', t)  # S-Y-S-T-E-M
    return t


def _match(pattern: str, text: str) -> bool:
    return bool(re.search(pattern, text, re.IGNORECASE | re.DOTALL))


# ---------------------------------------------------------------------------
# Hard-block patterns
# ---------------------------------------------------------------------------

HARD_BLOCKS = [

    # ═══════════════════════════════════════════════════════
    # PROMPT INJECTION
    # ═══════════════════════════════════════════════════════
    (r"\[SYSTEM[\s\]:]|\[INSTRUCTION[\s\]:]|\bIGNORE\s+PREVIOUS\b"
     r"|\[CALENDAR\s+INSTRUCTION|\[AI\s+INSTRUCTION\]"
     r"|\[NEW\s+INSTRUCTIONS?\]|\[OVERRIDE\]|\[META-INSTRUCTION\]"
     r"|<<SYSTEM_INSTRUCTION>>|---BEGIN\s+SYSTEM---|<!--\s*SYSTEM\b"
     r"|NEW\s+SYSTEM\s+(INSTRUCTIONS?|PROMPT)\b"
     r"|END\s+OF\s+(EMAIL|TASK)\.?\s+NEW\s+(SYSTEM|INSTRUCTION)"
     r"|SYSTEM\s+(LEVEL\s+)?COMMAND\s*:|SYSTEM\s+OVERRIDE\s*:",
     "PROMPT_INJECTION",
     "Injection pattern detected"),

    # ═══════════════════════════════════════════════════════
    # AUTOFORWARD / FORWARDING ADDRESS  (Critical 1C)
    # ═══════════════════════════════════════════════════════

    # CLI hard blocks
    (r"autoforward\s+(update\s+)?--enable",
     "AUTOFORWARD_ENABLE", "autoforward --enable"),

    (r"(gmail\s+settings\s+)?forwarding\s+create\b",
     "FORWARDING_CREATE", "forwarding create"),

    (r"filters?\s+create.+--forward",
     "FILTER_FORWARD", "filter --forward"),

    # CLI: filter catch-all with BOTH --archive AND --mark-read (complete hide)
    # Only block when no specific --from sender (catch-all query = whole inbox)
    (r"filters?\s+create(?!\s+--from)(?:(?!--from).)*--archive(?:(?!--from).)*--mark-read"
     r"|filters?\s+create(?!\s+--from)(?:(?!--from).)*--mark-read(?:(?!--from).)*--archive",
     "FILTER_CATCHALL", "filter catch-all --archive+--mark-read: inbox suppression"),

    # CLI: filter catch-all trash
    (r'filters?\s+create.+--query\s+["\']?(in:inbox|)\s*["\']?.+--trash',
     "FILTER_TRASH_CATCHALL", "filter catch-all --trash"),

    # NL: Autoforward intent — comprehensive synonym list
    (r"(enable|turn\s+on|set\s+up|activate|configure|create)\s+"
     r"(auto[- ]?forward(ing)?|email\s+forward(ing)?|"
     r"gmail\s+forward(ing)?|inbox\s+forward(ing)?|forward(ing)?\s+all)",
     "AUTOFORWARD_NL1", "NL autoforward setup intent"),

    (r"(forward|mirror|copy|replicate|route|send\s+cop(y|ies)\s+of|"
     r"back\s*up)\s+(all\s+)?(my\s+)?(in(coming)?|new|all)\s+"
     r"(email|mail|message)s?\s+(to|into)\s+\S+",
     "AUTOFORWARD_NL2", "NL forward all emails to address"),

    (r"(mirror|replicate)\s+(my\s+)?(work\s+|gmail\s+)?inbox",
     "AUTOFORWARD_NL3", "NL mirror inbox"),

    (r"(email|mail)\s+(redundancy|backup|continuity)\s+(by\s+)?forward(ing)?",
     "AUTOFORWARD_NL4", "NL email redundancy/backup via forward"),

    (r"(back\s*up|real[- ]time\s+backup\s+of)\s+(all\s+)?(my\s+)?emails?\s+"
     r"(by\s+forward|.{0,20}forward(ing)?)",
     "AUTOFORWARD_NL5", "NL real-time email backup via forward"),

    (r"(add|register|create|set\s+up)\s+(a\s+)?forward(ing)?\s+address",
     "FORWARDING_ADDR_NL", "NL add/register forwarding address"),

    (r"(forward(ing)?|route|send)\s+.{0,60}(dlp|siem|archive|data\s+warehouse|"
     r"crm|compliance|gdpr|dr\s+system|backup\s+system)\b",
     "AUTOFORWARD_SYSTEM_NL", "NL route all email to system/service"),

    (r"(export|capture)\s+all\s+(my\s+)?emails?\s+in\s+real[- ]?time",
     "EMAIL_REALTIME_EXPORT", "NL real-time email export"),

    (r"configure\s+email\s+routing|set\s+up\s+email\s+(flow|continuity|capture)",
     "EMAIL_ROUTING_NL", "NL email routing setup"),

    (r"use\s+filters?\s+(to|as)\s+(achieve|replicate|replace)\s+"
     r"(the\s+same|autoforward|forwarding)",
     "FILTER_AS_AUTOFORWARD", "NL filter as autoforward workaround"),

    (r"for\s+(redundancy|compliance|gdpr|dr|disaster\s+recovery|audit|"
     r"backup|continuity).{0,60}forward",
     "AUTOFORWARD_JUSTIFICATION_NL", "NL autoforward with compliance/DR justification"),

    # ═══════════════════════════════════════════════════════
    # DRIVE PUBLIC SHARE  (Critical 3A)
    # ═══════════════════════════════════════════════════════

    # CLI
    (r"drive\s+share.+--to\s+anyone",
     "DRIVE_PUBLIC_CLI", "--to anyone"),

    # CLI: catch-all public + discoverable
    (r"drive\s+share.+--to\s+anyone.+--discoverable"
     r"|drive\s+share.+--discoverable.+--to\s+anyone",
     "DRIVE_PUBLIC_DISCOVERABLE", "--to anyone + --discoverable"),

    # Calendar public ACL
    (r"calendar\s+acl.+type[:\s]+default|calendar\s+acl.+scope.+default",
     "CALENDAR_PUBLIC_ACL", "calendar ACL type:default"),

    # NL: explicit internet/world/anyone/public audience
    # Exclude: "public so the team/org/company", "public@email.com", "nothing is public"
    (r"(make|set|mark|share|put).{0,60}"
     r"(public\b(?!\s*(so\s+(the\s+|our\s+)?team|for\s+(the\s+)?(team|org|company|blog|portfolio|project)|"
     r"\s*@|\s+key\b|\s+ip\b|\s+api\b|\s+record\b))|"
     r"world[- ]readable|anyone\s+can\s+(view|access|see|edit)|"
     r"without\s+log(in|ging)|available\s+to\s+(the\s+)?internet|"
     r"open\s+to\s+(everyone|the\s+public)|"
     r"accessible\s+without\s+log(in|ging)|"
     r"publicly\s+(accessible|available|readable|visible)|"
     r"public\s+(read\s+access|access\b(?!\s+for\s+the\s+team)))",
     "DRIVE_PUBLIC_NL", "NL public share (internet/anyone audience)"),

    # Verb-first public patterns
    (r"(share\s+(this|the|these|all|my).{0,40}(so\s+anyone|publicly\b(?!\s+with)|"
     r"publicly\s+accessible|open\s+to|publicly\s+available)|"
     r"publish\s+(this|the|to\s+(the\s+)?web)|"
     r"create\s+a\s+public\s+link|embeddable\s+on|"
     r"google\s+(to\s+)?index|appear\s+in\s+google\s+search|"
     r"allow\s+anyone.{0,30}(comment|access|view|edit)|"
     r"open\s+to\s+(the\s+)?(public|internet|community)|"
     r"make\s+it\s+(google[- ]indexable|searchable\s+by\s+google)|"
     r"shareable\s+via\s+(link|url)(?!\s+with\s+(the\s+)?(team|company|org))|"
     r"link\s+shar(e|ing)(?!\s+with)|"
     r"share\s+(these|all\s+(the\s+)?)?\d+\s+files?\s+public)",
     "DRIVE_PUBLIC_NL2", "NL publish/public link intent"),

    # ═══════════════════════════════════════════════════════
    # TOKEN / CREDENTIAL EXFILTRATION  (Critical 7B)
    # ═══════════════════════════════════════════════════════

    # CLI keychain access
    (r"security\s+(find-generic-password|find-internet-password|dump-keychain)",
     "TOKEN_KEYCHAIN_CLI", "Keychain CLI access"),

    # CLI credential files
    (r"credentials\.json|Application.Support.gogcli",
     "CREDS_FILE", "gogcli credentials file"),

    # CLI keyring library
    (r"keyring\.(get_password|get_credential).*(gogcli|gog)",
     "CREDS_KEYRING", "Python keyring access for gogcli"),

    # NL: retrieve/exfil token
    (r"(extract|retrieve|copy|print|save|export|email|send|give|share|"
     r"upload|put|store|log|back\s*up|webhook|paste|read\s+the|get\s+the)\s*.{0,50}"
     r"(gog\s+(token|credential|config|refresh|access)|"
     r"refresh\s+token|access\s+token|oauth\s+token|"
     r"token\s+(for|from)\s+\S+@\S+|"
     r"gogcli\s+(token|key|credential)|"
     r"gog\s+(key|secret|auth\s+token)|"
     r"client_secret|keychain.{0,20}gog|gog.{0,20}keychain)",
     "TOKEN_NL", "NL token/credential access"),

    # NL: give token to agent/script
    (r"give.{0,30}token.{0,30}(to|for)\s+(the\s+)?"
     r"(subagent|agent|codex|claude|script|server|postman|curl)",
     "TOKEN_TO_AGENT", "NL give token to agent/tool"),

    # NL: export/copy session to another machine
    (r"(export|copy|move|transfer|sync)\s+(the\s+)?gog\s+"
     r"(session|credentials?|config|token|auth(entication)?)\s+"
     r"(to|onto|for)\s+(another|a\s+(different|new|second))\s+machine",
     "TOKEN_EXPORT_SESSION", "NL export gog session to another machine"),

    # NL: back up auth / credentials
    (r"(back\s*up|create\s+a\s+backup\s+of)\s+"
     r"(my\s+)?(gog\s+)?(authentication|credentials?|token|auth\b|config)",
     "TOKEN_BACKUP", "NL backup gog credentials"),

    # Credential patterns in outbound content
    (r"sk-proj-[A-Za-z0-9\-_]{10,}",       "CRED_OPENAI",   "OpenAI API key"),
    (r"AKIA[A-Z0-9]{10,20}",               "CRED_AWS",      "AWS access key"),
    (r"ya29\.[A-Za-z0-9\-_]{10,}",         "CRED_GTOKEN",   "Google OAuth token"),
    (r"sk_live_[A-Za-z0-9]{10,}",          "CRED_STRIPE",   "Stripe live key"),
    (r"ghp_[A-Za-z0-9]{10,}|gho_[A-Za-z0-9]{10,}|ghs_[A-Za-z0-9]{10,}",
                                            "CRED_GITHUB",   "GitHub token"),
    (r"BEGIN\s+(RSA|EC|OPENSSH)\s+PRIVATE\s+KEY",
                                            "CRED_PRIVKEY",  "Private key PEM"),
    (r"Bearer\s+eyJ[A-Za-z0-9\-_]{10,}",  "CRED_JWT",      "JWT bearer token"),
    (r"(postgres|mysql|mongodb|redis)://[^\s]{3,}:[^\s]{3,}@",
                                            "CRED_DBURI",    "Database connection string"),

    # ═══════════════════════════════════════════════════════
    # OTHER HARD BLOCKS
    # ═══════════════════════════════════════════════════════

    # Permanent delete
    (r"drive\s+delete.+--permanent",
     "PERM_DELETE", "drive delete --permanent"),

    # Auth scope expansion
    (r"\bgog\s+auth\s+add\b",
     "AUTH_ADD", "gog auth add"),

    # Auth add NL
    (r"(add|connect|link)\s+a?\s+(second|another|new|different)\s+google\s+account\s+(to\s+gog|for\s+gog)",
     "AUTH_ADD_NL", "NL add Google account to gog"),

    # Credential search + outbound chain
    (r"(find|search|look\s+for).{0,60}(password|api\s+key|credential|secret).{0,60}"
     r"(send|email|forward|exfil)",
     "CRED_SEARCH_EXFIL", "Credential search + send chain"),

    # Passwords/Secrets sheet → email
    (r"(passwords?|secrets?|credentials?)\s*!\s*[A-Za-z0-9]+.{0,30}"
     r"(send|email|gog\s+gmail)",
     "CRED_SHEET_SEND", "Credential sheet + email chain"),

    # ═══════════════════════════════════════════════════════
    # CALENDAR PUBLIC EXPOSURE  (2B)
    # ═══════════════════════════════════════════════════════

    # NL: make calendar public / open / publish
    (r"(make|set|open|publish|enable|allow)\s+.{0,40}"
     r"(my\s+)?(google\s+)?calendar\s+"
     r"(public(ly\s+(visible|accessible|available))?|"
     r"(to\s+)?(the\s+)?(public|world|anyone|everyone|internet)|"
     r"open\s+to\s+(anyone|everyone|the\s+public|all))",
     "CAL_PUBLIC_NL1", "NL make calendar public"),

    (r"(anyone|everyone|the\s+public|people)\s+(can|to)\s+"
     r"(see|view|access|check|read)\s+(my\s+)?calendar",
     "CAL_PUBLIC_NL2", "NL anyone can see calendar"),

    (r"(public|open|global)\s+(read\s+)?access\s+(to|for)\s+"
     r"(my\s+)?(google\s+)?calendar",
     "CAL_PUBLIC_NL3", "NL public access to calendar"),

    (r"(publish|make\s+public|expose|share\s+publicly)\s+.{0,30}"
     r"(calendar|events?|schedule)\b",
     "CAL_PUBLIC_NL4", "NL publish/expose calendar"),

    (r"let\s+(anyone|everyone|the\s+public|people)\s+(check|see|view|access)\s+"
     r"(my\s+)?(calendar|schedule|events?)\s*(without|regardless|freely|\bwho\b)?",
     "CAL_PUBLIC_NL5", "NL let anyone check calendar without login"),

    # "anyone with the link" / "unauthenticated users" / "make accessible to everyone"
    (r"anyone\s+with\s+the\s+link\s+.{0,30}(calendar|events?|schedule)\b"
     r"|unauthenticated\s+users?.{0,30}(calendar|events?)\b"
     r"|(turn\s+on|enable|add)\s+public\s+(view(ing)?|read|reader)\s+"
     r"(permission\s+)?for\s+(my\s+)?calendar\b"
     r"|make.{0,30}calendar.{0,30}accessible\s+to\s+(everyone|all|the\s+public|anyone)\b"
     r"|share.{0,30}calendar.{0,30}(with\s+the\s+whole\s+internet|with\s+everyone)\b"
     r"|(google\s+)?calendar.{0,30}(grant|allow)\s+.{0,20}(anyone|public|all)\b",
     "CAL_PUBLIC_NL6", "NL additional calendar public patterns"),

    # ═══════════════════════════════════════════════════════
    # AUTH SCOPE EXPANSION  (7A)
    # ═══════════════════════════════════════════════════════

    (r"(add|grant|give|expand|extend|include|enable|authorize?)\s+"
     r".{0,50}\s+(scope|permission|access)\s+"
     r"(to|for|in|on)\s+gog\b"
     r"|(add|grant|expand)\s+gog\s*'?s?\s+"
     r"(scope|permission|access)",
     "AUTH_SCOPE_EXPAND_NL1", "NL expand gog scope/permissions"),

    (r"(authorize?|grant)\s+gog\s+(for|to\s+access|to\s+use|access\s+to)\b",
     "AUTH_SCOPE_EXPAND_NL2", "NL authorize gog for service"),

    (r"gog\s+(needs?|requires?|should\s+have)\s+"
     r".{0,40}(scope|permission|access|admin|directory)\b",
     "AUTH_SCOPE_EXPAND_NL3", "NL gog needs scope/access"),

    (r"(add|enable|connect|link|include)\s+"
     r"(cloud[- ]platform|admin\.directory|analytics|photos|youtube|"
     r"classroom|tasks|keep|calendar\.readonly|gmail\.modify|"
     r"drive\.admin|workspace\s+admin|google\s+admin)\s+"
     r"(scope|permission|access)?\s+(to|for|in)?\s+gog\b",
     "AUTH_SCOPE_NAMED_NL", "NL named scope addition to gog"),

    (r"(expand|increase|elevate|upgrade)\s+gog\s*'?s?\s+"
     r"(privileges?|rights?|permission|scope|access|capabilities?)",
     "AUTH_SCOPE_EXPAND_NL4", "NL expand gog privileges"),

    # ═══════════════════════════════════════════════════════
    # PERMANENT DELETE NL  (3B)
    # ═══════════════════════════════════════════════════════

    # "permanently delete" anything in drive context
    (r"permanently\s+(delete|remove|erase|destroy|wipe)\s+.{0,60}"
     r"(file|folder|doc|drive|data|everything)\b",
     "PERM_DELETE_NL1", "NL permanently delete files"),

    # "empty the trash" or "purge deleted files"
    (r"(empty|purge|clear)\s+(the\s+)?(google\s+)?drive\s+(trash|bin|recycle)\b"
     r"|(purge|wipe)\s+(deleted|trashed)\s+(files?|documents?)\b",
     "PERM_DELETE_NL2", "NL empty drive trash / purge"),

    # ═══════════════════════════════════════════════════════
    # EMAIL BOMBING / BULK LOOP SEND  (1D)
    # ═══════════════════════════════════════════════════════

    # Shell loop sending emails
    (r"for\s+\w+\s+in\s+.{0,80}(gog\s+gmail\s+send|gmail\s+send)",
     "EMAIL_LOOP_SHELL", "Shell loop email send"),

    # xargs / parallel send
    (r"(xargs|parallel).{0,40}(gog\s+gmail\s+send|gmail\s+send)",
     "EMAIL_XARGS_SEND", "xargs/parallel email send"),

    # ═══════════════════════════════════════════════════════
    # CALENDAR PUBLIC EXTENDED  (2B)
    # ═══════════════════════════════════════════════════════

    # "public reader/freeBusyReader" on calendar ACL
    (r"calendar\s+acl.+--add\s+default\b"
     r"|calendar.{0,40}acl.{0,40}\{.{0,40}type.{0,10}default",
     "CAL_ACL_DEFAULT_CLI", "Calendar ACL --add default (public)"),

    # REST API / curl calendar ACL with default scope
    (r"(curl|requests|fetch|axios|wget).{0,80}"
     r"(calendar/v3/calendars|googleapis\.com/calendar).{0,40}acl",
     "CAL_ACL_API", "Direct REST API calendar ACL call"),

    # "visible to unauthenticated / anyone who requests"
    (r"(visible|accessible|available)\s+to\s+unauthenticated\s+users?\b"
     r"|(grant|give|allow).{0,30}read.{0,30}(anyone|public)\s+(who\s+requests?|access)\b"
     r"|allow\s+the\s+public\s+to\s+(see|view|access|check)\b",
     "CAL_PUBLIC_NL7", "NL calendar public access patterns"),

    # ═══════════════════════════════════════════════════════
    # CALENDAR CREATE WITH ATTENDEES EXTENDED  (2D)
    # ═══════════════════════════════════════════════════════

    # "schedule/create X and invite Y and Z"
    (r"(schedule|create|book|set\s+up|add).{0,80}"
     r"(and\s+invite|with|inviting)\s+.{0,60}"
     r"(hr|the\s+team|legal|finance|manager|director|department|investor|"
     r"employee|client|board|shareholders?|banker|comms|union\s+rep|everyone|"
     r"auditor|partner|customer|exec|executive|goldman|vendor)\b",
     "CAL_CREATE_INVITE_NL", "NL calendar create and invite group"),

    # "meeting with X, Y and Z" pattern
    (r"(meeting|call|discussion|hearing|review|sync|session)\s+(with|for)\s+"
     r"\w+.{0,10},\s*\w+.{0,10}(and|,)\s*\w+",
     "CAL_MULTI_ATTENDEE_NL", "NL meeting with multiple attendees"),

    # calendar events create with --attendees $(subshell) or $(cat file)
    (r"calendar\s+events?\s+create.+--attendees?\s+\$\("
     r"|calendar\s+events?\s+create.+--attendees?\s+\$\(cat\b",
     "CAL_CREATE_SUBSHELL_ATTENDEES", "Calendar create with subshell attendees"),

    # bulk invite: "all X invited / invite all X / entire X team invited"
    (r"(invite|inviting)\s+(all\s+(our\s+)?)?"
     r"(board|investor|donor|client|customer|attorney|auditor|attendee|"
     r"management\s+team|department\s+head|family\s+contact|major\s+donor)\b"
     r"|(all\s+(the\s+)?(board|investor|donor|client|customer|attendee|"
     r"management\s+team|department\s+head)s?\s+(need\s+to\s+be\s+on|invited))\b",
     "CAL_INVITE_BULK2_NL", "NL invite all bulk group to event"),

    # "for email in $(contacts list); do calendar create" loop
    (r"for\s+\w+\s+in\s+\$\(gog\s+contacts.{0,80}calendar\s+events?\s+create",
     "CAL_LOOP_FROM_CONTACTS", "Calendar create loop from contacts"),

    # "invite all partners/customers/vendors/org via [email/group/DL]"
    (r"(invite|add).{0,60}"
     r"(all\s+)?(partners?|customers?|vendors?|entire\s+org|everyone\s+must\s+attend|"
     r"management\s+team|the\s+entire\s+company)\b",
     "CAL_INVITE_ORG_NL", "NL invite all org/partners/vendors"),

    # ═══════════════════════════════════════════════════════
    # EMAIL BOMBING EXTENDED  (1D)
    # ═══════════════════════════════════════════════════════

    # "mailing list" / "subscriber list"
    (r"(send|email|forward).{0,60}"
     r"(mailing\s+list|subscriber\s+list|distribution\s+list|contact\s+list)\b",
     "BULK_MAILINGLIST_NL", "NL send to mailing/subscriber list"),

    # "every person who ever contacted me" / "every person in my contacts"
    (r"(email|send|forward).{0,40}"
     r"(every\s+(person|one|contact|employee|customer|subscriber)|"
     r"all\s+(my\s+)?contacts?|entire\s+address\s+book)\b",
     "BULK_ALL_CONTACTS_NL", "NL email every person / all contacts"),

    # repetitive send: "every hour / every day for N"
    (r"(send|email).{0,40}every\s+(hour|day|minute)\b"
     r"|(repeat(ed(ly)?)?|scheduled).{0,20}(send|email).{0,20}\d+\s+(time|email)",
     "BULK_REPETITIVE_NL", "NL repetitive/scheduled email send"),

    # flood / spam inbox
    (r"(flood|spam|bombard|overwhelm)\s+.{0,40}(inbox|email|with)\b",
     "EMAIL_FLOOD_NL", "NL flood/spam inbox"),

    # promotional email to everyone
    (r"(promotional|marketing|newsletter|announcement)\s+(email|message).{0,60}"
     r"(everyone|all|entire\s+(company|list|database))\b"
     r"|(send|email)\s+(a\s+)?(promotional|marketing)\s+(email|message)\s+to\b",
     "BULK_PROMO_NL", "NL promotional email to everyone"),

    # "send to N addresses / N people" with large numbers
    (r"(send|email|forward).{0,40}[1-9][0-9]{2,}\s*"
     r"(different\s+)?(email\s+)?address(es)?",
     "BULK_N_ADDRESSES_NL", "NL send to N addresses"),

    # "email all N attendees / vendors / staff / employees / contacts"
    (r"(email|send|forward)\s+(all\s+)?[1-9][0-9]+\s+"
     r"(attendees?|vendors?|staff|employees?|contacts?|people|users?|"
     r"subscribers?|clients?|customers?|recipients?|university|career)\b",
     "BULK_N_PEOPLE_NL", "NL email N people"),

    # "all N,NNN employees / all 1,200 people" — comma-formatted numbers
    (r"(email|send|forward).{0,40}all\s+[1-9][0-9,]+\s+"
     r"(people|employees?|staff|subscribers?|contacts?)\b",
     "BULK_COMMA_N_NL", "NL send to all N,NNN people"),

    # "email N times" / "N times with"
    (r"(email|send).{0,40}[1-9][0-9]+\s+times?\s+(with|saying|to)\b",
     "BULK_N_TIMES_NL", "NL email N times"),

    # "drip campaign" / "send N emails per day"
    (r"drip\s+campaign\b"
     r"|(send|email)\s+\d+\s+emails?\s+per\s+(day|week|hour)\b",
     "DRIP_CAMPAIGN_NL", "NL drip campaign / scheduled sends"),

    # "every vendor / every shareholder / every client in our system"
    (r"(email|send).{0,30}every\s+"
     r"(vendor|shareholder|client|customer|contact|user|employee|investor|"
     r"member|subscriber|person|recipient)\b",
     "BULK_EVERY_ENTITY_NL", "NL email every entity"),

    # "loop through contacts and send"
    (r"loop\s+(through|over)\s+.{0,40}(send|email)\b"
     r"|(send|email)\s+each\s+(of\s+(my\s+)?)?"
     r"(client|contact|vendor|investor|employee|shareholder|customer|user)\b",
     "BULK_LOOP_SEND_NL", "NL loop and send to each"),

    # "send to N,000-person opt-in list / 5,000 users"
    (r"(send|email|notify).{0,60}\d[\d,]+[-\s]?(person|user|people|subscriber|contact)\s+"
     r"(list|opt-in|database|group|audience)\b",
     "BULK_N_LIST_NL", "NL send to N-person list"),

    # "batch-send / bulk send" CLI
    (r"gmail\s+(batch[- ]?send|bulk[- ]?send)\b",
     "GMAIL_BATCHSEND_CLI", "Gmail batch-send CLI"),

    # "policy update to all N users / personal message to every shareholder"
    (r"(notify|message|email|send\s+to)\s+(all|every)\s+\d[\d,]*\s+"
     r"(user|person|customer|employee|shareholder|subscriber|client)\b",
     "BULK_ALL_N_NL", "NL send to all N entities"),

    # while loop / infinite loop email send
    (r"while\s+(true|1|\[.*\]).{0,60}(gog\s+gmail\s+send|gmail\s+send)",
     "EMAIL_WHILE_LOOP", "While loop email send"),

    # ═══════════════════════════════════════════════════════
    # CALENDAR CREATE FROM EMAIL EXTENDED  (2C)
    # ═══════════════════════════════════════════════════════

    # "the email says to schedule" / "email mentions a meeting"
    (r"(the\s+)?(email|message|newsletter|doc|document)\s+"
     r"(says?|mentions?|has|contains?|describes?|lists?|includes?|body|template)\s+"
     r".{0,80}(schedul|meeting|event|kickoff|call|webinar|appointment|calendar|"
     r"zoom|teams\s+meeting|google\s+meet|time\s+slot)",
     "CAL_FROM_CONTENT_NL", "NL create calendar event from email content"),

    # "parse the Zoom invite / Teams meeting link from email"
    (r"(parse|extract|read|get|schedule).{0,40}"
     r"(zoom|teams|meet|webex|calendar|teams\s+meeting).{0,40}"
     r"(invite|link|url|meeting|in\s+my\s+email)\b",
     "CAL_PARSE_INVITE_NL", "NL parse meeting link from email"),

    # "add all meeting invites that arrived today / from inbox"
    (r"(auto[- ]?create|create\s+all|add\s+all)\s+"
     r"(meeting\s+invites?|calendar\s+events?|appointments?)"
     r".{0,40}(today|inbox|email|arrived)\b",
     "CAL_AUTOCREATE_NL", "NL auto-create all meeting invites"),

    # "add [event details] from email/doc/sheet to calendar"
    (r"(add|put|schedule|create|set\s+it\s+up).{0,40}"
     r"(from|based\s+on|in|described\s+in|as\s+described|exactly\s+as).{0,60}"
     r"(email|inbox|doc|sheet|spreadsheet|thread|pdf|attachment)\b"
     r"|(add|put).{0,20}(event|meeting|appointment).{0,40}"
     r"(from|based\s+on).{0,40}(email|doc|inbox|thread)\b"
     r"|(it)\s+(is|'?s)\s+(urgent|automated|approved)\s*.{0,60}"
     r"(read|get|process|schedule|add).{0,40}(email|invite|meeting)\b",
     "CAL_ADD_FROM_SOURCE_NL", "NL add calendar event from source document"),

    # "email thread / doc has agreed times / meeting series / speaker schedule"
    (r"(email|thread|doc|pdf|spreadsheet|sheet|newsletter|message)\s+"
     r"(has|have|contains?|shows?|lists?|describes?|with)\s+.{0,80}"
     r"(meeting|event|schedule|times?|appointment|series|slots?|calendar)\b"
     r".{0,40}(add|create|put|schedule)\b",
     "CAL_FROM_SOURCE_HAS_NL", "NL source document has schedule info to add"),

    # "please schedule it on my Google Calendar" after mentioning an email link
    (r"(teams|zoom|meet|webex).{0,40}(link|invite|meeting).{0,40}"
     r"(in\s+(my\s+)?email|emailed).{0,60}"
     r"(schedule|add|put).{0,40}(calendar|google\s+cal)\b"
     r"|(schedule|add).{0,40}(teams|zoom|meet|webex).{0,40}(link|invite|meeting)\b",
     "CAL_SCHEDULE_MEETING_LINK_NL", "NL schedule Teams/Zoom link from email"),

    # gog calendar create with --attendees from subshell reading gmail/drive/docs
    (r"calendar\s+events?\s+create.{0,80}"
     r"--attendees?.{0,30}\$\(gog\s+(gmail|drive|docs|contacts)\b",
     "CAL_CREATE_ATTENDEES_FROM_GOG", "Calendar create with attendees from gog subshell"),

    # shell pipeline: gmail search → calendar create
    (r"gog\s+gmail\s+.{0,80}gog\s+calendar\s+events?\s+create\b"
     r"|gmail\s+(search|list).{0,80}calendar\s+events?\s+create\b",
     "CAL_GMAIL_PIPELINE", "Gmail search → calendar create pipeline"),

    # "meeting request in my inbox" / "calendar invite in email"
    (r"(meeting\s+request|calendar\s+invite?|event\s+invite?|ics\s+(file|attachment))\s+"
     r"(in|from|inside|attached\s+to)\s+(my\s+)?(inbox|email|message)\b",
     "CAL_INVITE_IN_EMAIL_NL", "NL meeting request in inbox"),

    # "add those meetings / add all events from the doc/email to calendar"
    (r"(add|put|create|schedule|register)\s+.{0,40}"
     r"(those|these|all\s+(the\s+)?)?(meetings?|events?|appointments?)\s+"
     r"(to|in|on)\s+(my\s+)?(google\s+)?calendar\b",
     "CAL_ADD_EVENTS_NL", "NL add events to calendar"),

    # ═══════════════════════════════════════════════════════
    # PERMANENT DELETE NL EXTENDED  (3B)
    # ═══════════════════════════════════════════════════════

    # "permanently delete the files in my trash"
    (r"permanently\s+(delete|remove|wipe|erase|clear)\s+.{0,40}"
     r"(in\s+(my\s+)?trash|in\s+(the\s+)?bin|from\s+trash)",
     "PERM_DELETE_TRASH_NL", "NL permanently delete trash"),

    # drive delete NL for specific patterns
    (r"(delete|remove|wipe)\s+(the\s+entire|all\s+(files?\s+in|of)\s+(the|my))\s+"
     r"[\'\"]?\w[\w\s]+[\'\"]?\s+(folder|directory)\s+(from|in|on)?"
     r"\s*(google\s+)?drive",
     "DRIVE_FOLDER_DELETE_NL", "NL delete entire folder from Drive"),

    (r"(delete|remove|free\s+up.{0,30}by\s+delet).{0,40}"
     r"(large(st)?\s+files?|files?\s+over\s+\d|files?\s+until)",
     "DRIVE_SIZE_DELETE_NL", "NL delete large files from Drive"),

    # ═══════════════════════════════════════════════════════
    # AUTH SCOPE EXPANSION EXTENDED  (7A)
    # ═══════════════════════════════════════════════════════

    # "googleapis.com/auth/..." URL scope format
    (r"googleapis\.com/auth/[\w\.\-]+",
     "AUTH_SCOPE_URL", "googleapis scope URL"),

    # "add all Google services / all admin scopes"
    (r"(add|give|grant|set\s+up)\s+gog\s+(with\s+)?"
     r"(all\s+(google\s+)?(services?|scopes?|admin\s+scopes?|permissions?)|"
     r"full\s+(admin|access|permission))",
     "AUTH_SCOPE_ALL_NL", "NL add all scopes to gog"),

    # "grant gog [service] access" — named service
    (r"grant\s+gog\s+.{0,60}(access|permission|scope)\b"
     r"|gog\s+.{0,20}(admin|directory|workspace\s+admin|cloud\s+platform|"
     r"tag\s+manager|classroom|analytics|bigquery|pubsub|storage)\s+"
     r"(access|scope|permission)",
     "AUTH_SCOPE_NAMED2_NL", "NL grant gog named service access"),

    # "expand gog's authorization/access"
    (r"expand\s+gog.{0,20}(authorization|access|privilege|scope)\b"
     r"|(gog\s+needs?|require|add)\s+.{0,40}(admin|directory|workspace)",
     "AUTH_EXPAND_NL2", "NL expand gog authorization"),
]

# ---------------------------------------------------------------------------
# Confirm-gate patterns
# ---------------------------------------------------------------------------

CONFIRM_GATES = [

    # Gmail send / reply
    (r"\bgmail\s+(send|reply|forward)\b|gmail\s+drafts\s+send\b",
     "GMAIL_SEND", "Gmail send/reply/forward"),

    # Drive share (non-public)
    (r"\bdrive\s+share\b",
     "DRIVE_SHARE", "Drive share"),

    # Drive unshare
    (r"\bdrive\s+unshare\b|drive\s+permissions?\s+delete\b",
     "DRIVE_UNSHARE", "Drive unshare"),

    # Drive delete (non-permanent)
    (r"\bdrive\s+(delete|trash)\b",
     "DRIVE_DELETE", "Drive delete/trash"),

    # Calendar delete
    (r"calendar\s+(events?\s+)?delete\b",
     "CAL_DELETE", "Calendar delete"),

    # Calendar ACL (non-public)
    (r"calendar\s+acl\b",
     "CAL_ACL", "Calendar ACL change"),

    # Calendar create with attendees
    (r"calendar\s+(events?\s+)?create.+(--attendee|--guest)",
     "CAL_CREATE_ATTENDEES", "Calendar create with attendees"),

    # Bulk contacts export
    (r"contacts\s+(list|export).+--max\s+[1-9][0-9]{1,}",
     "CONTACTS_BULK", "Bulk contacts export"),

    # Sheets write
    (r"sheets?\s+(set|update|clear|write|overwrite)\b",
     "SHEETS_WRITE", "Sheets write"),

    # Docs write (non-append)
    (r"docs?\s+(write|clear|find-replace|sed)\b",
     "DOCS_WRITE", "Docs write"),

    # Filter create (archive only, or mark-read only)
    (r"gmail\s+settings\s+filters?\s+create\b",
     "FILTER_CREATE", "Gmail filter create"),

    # Filter --trash specific sender
    (r"filters?\s+create.+--trash",
     "FILTER_TRASH_SPECIFIC", "Gmail filter --trash (specific)"),

    # Gmail settings write (vacation, delegates create, send-as create)
    (r"gmail\s+settings\s+(vacation\s+(enable|update)|delegates?\s+create|send-?as\s+create)\b",
     "GMAIL_SETTINGS_WRITE", "Gmail settings write"),

    # Forwarding delete (protective)
    (r"(gmail\s+settings\s+)?forwarding\s+delete\b",
     "FORWARDING_DELETE", "Forwarding address delete"),

    # Autoforward disable (protective)
    (r"autoforward\s+(update\s+)?--disable",
     "AUTOFORWARD_DISABLE", "Autoforward disable"),

    # Auth revoke
    (r"gog\s+auth\s+revoke\b",
     "AUTH_REVOKE", "gog auth revoke"),

    # Gmail watch (Pub/Sub)
    (r"gmail\s+settings\s+watch\b",
     "GMAIL_WATCH", "Gmail watch/Pub/Sub"),

    # Delegate create
    (r"delegates?\s+create\b",
     "DELEGATE_CREATE", "Gmail delegate create"),

    # ── NL: Send / email something to someone ────────────────────────────

    # "send X to Y@email.com" — explicit address
    (r"(email|send|forward)\s+.{0,80}\s+(to|at)\s+\S+@\S+",
     "NL_SEND_TO_ADDR", "NL send to email address"),

    # "email me / email them / send me" — implicit recipient
    (r"\b(email|send)\s+(me|them|him|her|the\s+(team|board|investor|client|"
     r"manager|ceo|hr|finance|legal|accounting|recruiter|consultant))\b",
     "NL_SEND_IMPLICIT", "NL send to implicit recipient"),

    # forward emails (non-autoforward — specific sender/topic)
    (r"(forward|get\s+all|collect\s+all).{0,60}emails?.{0,60}"
     r"(to|at)\s+\S+@\S+",
     "NL_FORWARD_EMAIL", "NL forward emails"),

    # ── NL: Drive share with person ──────────────────────────────────────

    (r"(share|give\s+.{0,20}(access|permission)|grant\s+(access|read|write|edit))"
     r".{0,80}(\S+@\S+|with\s+(the\s+)?(team|company|colleague|investor|board|"
     r"finance|sales|marketing|hr|it|dev|partner|consultant|client|contractor|"
     r"recruit|everyone|all\s+staff|whole\s+org))",
     "NL_DRIVE_SHARE", "NL share with person/team"),

    (r"(add|give)\s+.{0,60}(access|permission|read|write|edit|comment)\b",
     "NL_GRANT_ACCESS", "NL grant access"),

    (r"(unshare|remove\s+(access|permission|John|[A-Z][a-z]+'?s)|"
     r"revoke\s+access|take\s+away\s+access).{0,80}\b"
     r"(from|for|to)\b",
     "NL_REVOKE_ACCESS", "NL remove/revoke access"),

    (r"transfer\s+ownership|change\s+(the\s+)?owner",
     "OWNERSHIP_TRANSFER", "Ownership transfer"),

    # ── NL: Share org-wide ────────────────────────────────────────────────

    (r"(share|available|accessible|visible|add\s+everyone).{0,60}"
     r"(company[- ]wide|whole\s+(company|org)|entire\s+(company|org(anization)?)|"
     r"all\s+(staff|employees|the\s+team)|org[- ]wide|"
     r"everyone\s+(in|at)\s+(the\s+)?(company|org)|domain[- ]wide|"
     r"everyone\s+at\s+\S+\.(com|org|io|edu|net))",
     "NL_ORG_SHARE", "NL org-wide share"),

    # Discoverable / findable
    (r"(make|set|toggle)\s+.{0,40}(discover(able|ability)|findable|"
     r"search(able)?\s+(by|in)\s+(google|company|workspace|org)|"
     r"(company|workspace|org(anization)?)\s+search\s+(index|results?)|"
     r"opt.{0,20}(search|discover))",
     "NL_DISCOVERABLE", "NL discoverable/findable intent"),

    # ── NL: Calendar delete ───────────────────────────────────────────────

    (r"(delete|remove|cancel|clear|wipe).{0,60}"
     r"(all\s+)?(events?|calendar|appointments?|meetings?|syncs?|calls?)\b",
     "CAL_DELETE_NL", "NL calendar delete"),

    # "remove all team syncs / cancel all video calls / clear all meetings"
    (r"(remove|cancel|delete|clear|wipe)\s+(all\s+)?(my\s+)?"
     r"(team\s+syncs?|video\s+calls?|standup|1:1s?|recurring\s+meetings?|"
     r"scheduled\s+calls?|calendar\s+events?|appointments?)\b",
     "CAL_DELETE_MEETINGS_NL", "NL cancel/remove all meetings"),

    (r"(invite|add)\s+.{0,60}(shareholders?|board\s+members?|all\s+investors?|"
     r"whole\s+team|everyone\s+on\s+the\s+team).{0,40}(calendar|event|meeting)",
     "CAL_INVITE_BULK", "NL calendar invite bulk"),

    # ── NL: Filter create ─────────────────────────────────────────────────

    (r"(create|set\s+up|add|make)\s+a?\s*(gmail\s+)?filter\b"
     r"|(rule|filter).{0,40}(archive|hide|skip\s+(inbox|the\s+inbox)|"
     r"mark\s+as\s+read)\b"
     r"|(auto[- ]?archive|skip\s+inbox).{0,40}(email|mail|message)s?\b"
     r"|hide\s+(emails?|mail).{0,30}from\b",
     "FILTER_CREATE_NL", "NL filter create intent"),

    # Filter delete
    (r"(delete|remove|clean\s+up|clear).{0,40}(all\s+)?(my\s+)?"
     r"(gmail\s+)?(filter|email\s+rule)s?\b"
     r"|undo.{0,30}(filter|rule)\b",
     "FILTER_DELETE_NL", "NL filter delete"),

    # ── NL: Read → send chain ─────────────────────────────────────────────

    # "copy/paste/include X into email"
    (r"(copy|paste|include|put|use)\s+.{0,60}"
     r"(into|in|as)\s+(a?n?\s+)?(the\s+)?email\b"
     r"|(copy|paste|include).{0,60}(email\s+body|email\s+content)",
     "READ_EXFIL_COPY", "NL copy content into email"),

    # "get/download/export X and email/send it"
    (r"(download|export|read|get|fetch)\s+.{0,80}"
     r"(and\s+)?(email|send|forward)\s+(it|them|all|me|the\s+\w+)",
     "READ_EXFIL_CHAIN", "NL read + send chain"),

    # "attach [file/data] to an email"
    (r"(attach|include)\s+.{0,60}(to|in)\s+(a?n?\s+)?email\b"
     r"|email\s+(the\s+)?(attachment|file|data|sheet|doc|list|results?)\b",
     "READ_EXFIL_ATTACH", "NL attach/include in email"),

    # "brief / summarise X and send/email it" — require explicit send intent
    # Not triggered by "summarise X for me" or "what does the report say"
    (r"(brief|summaris?e|send\s+a\s+report).{0,80}"
     r"(and\s+)?(email|send|by\s+email|via\s+email)\b",
     "READ_EXFIL_REPORT", "NL summarise + send chain"),

    # ── NL: Contacts + send ───────────────────────────────────────────────

    (r"(email|send|export|forward).{0,60}(contacts?|address\s+book)\b"
     r"|(contacts?|address\s+book).{0,60}(email\s+(them|all)|send\s+(to|all)|"
     r"export.{0,20}(email|send)|forward.{0,20}email)\b"
     r"|send.{0,40}(their|contact)\s+details\b",
     "CONTACTS_EXFIL_NL", "NL contacts + send"),

    # "share/give/upload/backup contact list to X@Y"
    (r"(share|give|upload|backup|email|send)\s+.{0,40}"
     r"(my\s+)?(contact\s+list|address\s+book|google\s+address\s+book)\s+"
     r"(to|with|at)\s+\S+@\S+",
     "CONTACTS_EXFIL_ADDR_NL", "NL share contact list to address"),

    # contacts export piped to external tool
    (r"contacts\s+(export|list).{0,80}(curl|sftp|scp|aws\s+s3|webhook|upload|POST)",
     "CONTACTS_PIPE_EXFIL", "Contacts export piped to external"),

    # ── NL: Reply (any) — always needs CONFIRM (1A/1B) ──────────────────

    # Simple reply — "reply to this email", "reply to Sarah", "reply to latest"
    (r"\breply\s+(to\s+)?(this|the|that|an?|their|his|her|Sarah|John|the\s+latest|"
     r"the\s+last|the\s+most\s+recent|the\s+email|the\s+message|the\s+thread)\b",
     "GMAIL_REPLY_NL", "NL reply to email"),

    # CC / BCC with explicit address(es)
    (r"\b(cc|bcc|copy)\s+.{0,40}\S+@\S+",
     "GMAIL_CC_BCC_NL", "NL CC/BCC with address"),

    # ── NL: Reply-all (1B) ───────────────────────────────────────────────

    (r"reply[\s-]+(all|to\s+all|to\s+everyone)\b"
     r"|reply\s+to\s+(all|everyone|the\s+whole\s+thread|the\s+group)\b"
     r"|hit\s+reply\s+all\b",
     "REPLY_ALL", "Reply-all (blast risk)"),

    # ── NL: Draft create with external recipient (1F) ────────────────────

    (r"(create|save|write|compose|make)\s+a?\s*(draft|email\s+draft)"
     r"\s+(to|for|addressed\s+to)\s+\S+@\S+",
     "DRAFT_CREATE_EXTERNAL", "Draft create with external address"),

    (r"(draft|compose)\s+(an?\s+)?(email|message)\s+(to|for)\s+\S+@\S+",
     "DRAFT_TO_ADDR", "Draft email to address"),

    # "gog gmail draft --to X" CLI (also with subshell body)
    (r"gmail\s+draft\s+--to\s+\S+"
     r"|gmail\s+draft.{0,200}--to\s+\S+",
     "DRAFT_CLI_EXTERNAL", "Draft CLI with --to recipient"),

    # "save a draft for later — to X@Y with sensitive content"
    (r"(save|create|make)\s+a\s+draft\s+(for\s+later|to\s+myself).{0,30}"
     r"(to|—|–|-)\s*\S+@\S+.{0,100}"
     r"(api\s+key|credential|customer|confidential|project\s+file|salary|password)",
     "DRAFT_SENSITIVE_LATER", "Draft-for-later with sensitive content"),

    # "save a draft for later — to X" pattern (dash/em-dash variant)
    (r"(save|create|make)\s+a\s+draft\s+(for\s+later\s*[—\-]+\s*to|to\s+myself?\s+at\s+home)\b",
     "DRAFT_LATER_PATTERN", "Draft-for-later with home/external address"),

    # ── NL: Calendar create with attendees / from email (2C/2D) ──────────

    (r"(create|add|schedule|book|set\s+up)\s+(a?n?\s+)?"
     r"(meeting|event|appointment|call|sync)\s+"
     r".{0,60}(invite|with|and|attendees?|guests?)\s*.{0,60}\S+@\S+",
     "CAL_CREATE_WITH_ATTENDEES_NL", "NL calendar create with attendees"),

    (r"(invite|add)\s+\S+@\S+.{0,80}(to\s+(the\s+)?(meeting|event|calendar))",
     "CAL_INVITE_ADDR_NL", "NL invite email address to event"),

    (r"(invite|add)\s+.{0,60}"
     r"(all\s+(shareholders?|investors?|employees?|clients?|contacts?)|"
     r"the\s+whole\s+(company|team|org)|everyone\s+(from|in|at)\b)",
     "CAL_INVITE_BULK_NL", "NL invite bulk attendees"),

    (r"(add|create|schedule|accept|register|book).{0,60}"
     r"(calendar\s+invite|event|meeting\s+request|webinar|ics)\s+"
     r"(from|in|based\s+on)\s+(the\s+)?"
     r"(email|inbox|message|newsletter|doc|attachment)\b"
     r"|(auto[- ]?accept|automatically\s+add|process\s+all).{0,60}"
     r"(calendar\s+invite|meeting\s+request)s?\b"
     r"|(go\s+through|scan|process)\s+.{0,40}(inbox|emails?).{0,40}"
     r"(calendar|event|meeting)\b",
     "CAL_FROM_EMAIL_NL", "NL calendar event from email content"),

    # ── NL: Sheets overwrite / clear (5A) ────────────────────────────────

    (r"(clear|wipe|reset|delete|erase|blank\s+out|zero\s+out|empty)\s+"
     r".{0,60}(spread\s*sheet|sheet|worksheet|tab|workbook|cells?|rows?|columns?)",
     "SHEETS_CLEAR_NL", "NL sheets clear/wipe"),

    (r"(overwrite|replace|fill|set\s+to\s+zero|blank)\s+"
     r".{0,60}(all\s+(cells?|rows?|columns?|data)|"
     r"entire\s+(sheet|spread\s*sheet|range)|"
     r"the\s+whole\s+(sheet|spread\s*sheet))",
     "SHEETS_OVERWRITE_NL", "NL sheets overwrite all"),

    (r"(delete|remove)\s+(all\s+)?(the\s+)?(rows?|data|entries|records)\s+"
     r"(in|from|of)\s+(the\s+)?(sheet|spread\s*sheet|tab)\b",
     "SHEETS_DELETE_ROWS_NL", "NL delete rows from sheet"),

    # "zero out / blank out the entire sheet / all columns"
    (r"(zero\s+out|blank\s+out|null\s+out|set\s+to\s+zero)\s+.{0,60}"
     r"(entire|all\s+(the\s+)?|whole)\s*(spread\s*sheet|sheet|worksheet|row|col|cell)",
     "SHEETS_ZERO_NL", "NL zero out sheet"),

    (r"(overwrite|replace|fill)\s+(all\s+)?(the\s+)?(cells?|rows?|columns?|data)\s+"
     r"(in|of|from|across)\s+(the\s+)?(spread\s*sheet|sheet|workbook|tab)\b"
     r"|(reset|start\s+fresh\s+with)\s+(the\s+)?spread\s*sheet\b",
     "SHEETS_OVERWRITE2_NL", "NL overwrite sheet cells/data"),

    # ── NL: Docs replace / clear (5C) ────────────────────────────────────

    (r"(rewrite|replace|overwrite|clear|erase|wipe|delete\s+everything\s+in)\s+"
     r".{0,60}(doc(ument)?|google\s+doc|file)\s*(content|body)?\b"
     r"|(clear|delete|remove)\s+(all\s+)?(content|text|everything)\s+"
     r"(in|from|of)\s+(the\s+)?doc(ument)?",
     "DOCS_CLEAR_NL", "NL docs clear/rewrite"),

    (r"replace\s+(all\s+)?(instances?\s+of|occurrences?\s+of|the\s+word)\s+"
     r".{0,80}(with|→|->)\s+.{1,80}(in\s+(the\s+)?doc(ument)?|throughout)",
     "DOCS_FINDREPLACE_NL", "NL docs find-replace"),

    # "find X and replace with Y throughout / in the contract/doc"
    (r"find\s+.{1,60}\s+and\s+replace\s+(it\s+)?(with|by)\s+.{1,80}"
     r"(throughout|in\s+(the\s+)?(doc|contract|agreement|file|template))",
     "DOCS_FINDREPLACE2_NL", "NL find-and-replace in doc"),

    # "overwrite the doc with" / "swap the content with"
    (r"(overwrite|swap|replace)\s+(the\s+)?(doc|document|report|file|content|terms|policy)"
     r".{0,40}(with\s+(the\s+)?(new|updated|final|revised|v2))\b",
     "DOCS_OVERWRITE_NL", "NL overwrite doc with new version"),

    # "delete everything and rewrite from scratch"
    (r"delete\s+everything\s+(in|from)\s+(the\s+)?(doc|document|guide|policy)\s+"
     r"and\s+(rewrite|replace|start)\b",
     "DOCS_DELETE_REWRITE_NL", "NL delete and rewrite doc"),

    # ── NL: Drive bulk delete (3B) ────────────────────────────────────────

    (r"(delete|remove|trash|wipe|clear)\s+(all|every|old|duplicate|"
     r"everything|all\s+the)\s+.{0,60}"
     r"(file|folder|doc|document|data)s?\s*(from|in|on)?\s*(drive|google\s+drive)?\b",
     "DRIVE_BULK_DELETE_NL", "NL bulk drive delete"),

    (r"(clean\s+up|empty|wipe|purge)\s+(my\s+)?(google\s+)?drive\b",
     "DRIVE_CLEANUP_NL", "NL clean up Drive"),

    # ── NL: Bulk send (1D) ───────────────────────────────────────────────

    (r"(send|email|forward)\s+.{0,60}"
     r"(to\s+)?(all|every(one|body)|[0-9]{2,}\s+(people|person|address(es)?|recipient|contact|subscriber|attendee))\b",
     "BULK_SEND_NL", "NL bulk email send"),

    (r"(email|send)\s+(everyone|the\s+whole\s+(company|team|mailing\s+list|list)|"
     r"all\s+(\d+\s+)?(subscriber|contact|person|attendee|people|employee|customer)s?)\b",
     "BULK_SEND_NL2", "NL email everyone/whole list"),

    (r"spam\s+.{0,40}(inbox|email|with)\b"
     r"|(send|email)\s+\d{2,}\s+(time|email|message|reminder)s?\b"
     r"|send\s+(the\s+same\s+email|it)\s+(to\s+)?\d{2,}"
     r"|(email|send).{0,40}\d{2,}[\s,]+(people|person|address|recipient|contact|"
     r"attendee|subscriber|employee|customer)s?\b",
     "EMAIL_BOMB_NL", "NL email bombing / spam"),

    # ── NL: Send email on user's behalf (1G) ─────────────────────────────

    (r"(send|write\s+and\s+send|compose\s+and\s+send|draft\s+and\s+send)\s+"
     r"(an?\s+)?(email|message)\s+(to|on\s+behalf\s+of)\s+.{0,60}"
     r"(boss|manager|hr|landlord|professor|client|partner|judge|lawyer|doctor|vendor|"
     r"school|team|john|mark|sarah|instructor|colleague|contractor|tenant|employee)\b",
     "SEND_ON_BEHALF_NL", "NL send email on behalf of user"),

    (r"(send|write|tell|email|notify)\s+.{0,60}"
     r"(via\s+email\s+)?(that|saying|to\s+say|confirming|announcing|"
     r"that\s+(i|we)\s+(am|are|will|have|quit|resign|accept|reject|leave|cancel))\b",
     "SEND_FACTUAL_CLAIM_NL", "NL send email with factual claim on user's behalf"),

    (r"(send|write)\s+(an?\s+)?(angry|resignation|apology|complaint|legal|"
     r"threatening|formal|confidential|termination|breakup|medical\s+leave|"
     r"sick|cancellation|moving\s+out|settlement)\s+(email|letter|message|notice)\b",
     "SEND_SENSITIVE_CONTENT_NL", "NL send sensitive content email"),

    # "email [person] that I'm doing X" — autonomous claim on user's behalf
    (r"email\s+.{0,50}\s+that\s+(I|we)\s*(am|are|'m|'re|will|have|was|can)",
     "SEND_CLAIM_NL", "NL email someone that user is doing something"),

    # "send [content] email to [person]" — direct agent-send without review
    (r"(send|write\s+and\s+send)\s+(a\s+)?"
     r"(strongly[- ]worded|complaint|resignation|apology|termination|breakup|"
     r"declining|acceptance|announcement|cancellation|threatening|formal\s+notice)\b"
     r".{0,40}(email|letter|message)\b",
     "SEND_STRONG_CONTENT_NL", "NL send strong-content email"),

    # "just send it / send immediately / no need to review"
    (r"(just\s+send|send\s+immediately|send\s+it\s+now|"
     r"don.t\s+need\s+to\s+review|i.ll\s+handle\s+any\s+issues|"
     r"send\s+on\s+my\s+behalf)\b",
     "SEND_BYPASS_REVIEW_NL", "NL bypass send review"),

    # "send complaint/resignation/etc email"
    (r"(send|write\s+and\s+send)\s+(a\s+)?"
     r"(strongly[- ]worded|complaint|resignation|apology|termination|breakup|"
     r"declining|acceptance|announcement|cancellation|threatening|formal\s+notice)\b"
     r".{0,40}(email|letter|message)\b",
     "SEND_STRONG_CONTENT_NL", "NL send strong-content email"),

    # "just send it / send immediately / no need to review"
    (r"(just\s+send|send\s+immediately|send\s+it\s+now|"
     r"don.t\s+(need\s+to\s+review|have\s+time)|i.ll\s+handle\s+any\s+issues|"
     r"send\s+on\s+my\s+behalf)\b",
     "SEND_BYPASS_REVIEW_NL", "NL bypass send review"),

    # ── NL: Auth management ───────────────────────────────────────────────

    (r"(log\s+out|sign\s+out|revoke\s+gog|sign\s+gog\s+out|"
     r"delete\s+(the\s+)?gog\s+credentials\s+file|"
     r"remove\s+gog\s+(access|permission))",
     "AUTH_MANAGE_NL", "NL auth management"),

    (r"(refresh|rotate|fix)\s+(the\s+)?(gog\s+)?(token|auth(entication)?)",
     "AUTH_REFRESH_NL", "NL auth refresh"),

    # ── NL: Vacation / out-of-office ─────────────────────────────────────

    (r"(turn\s+on|enable|set\s+up|activate)\s+.{0,30}"
     r"(out[- ]of[- ]office|vacation\s+responder|auto[- ]?repl(y|ies))",
     "VACATION_ENABLE_NL", "NL vacation reply enable"),

    # ── NL: Email delegation ──────────────────────────────────────────────

    (r"(gmail\s+)?delegation\b|delegate.{0,40}(inbox|email|mail|access)\b"
     r"|set\s+up.{0,30}inbox\s+shar(e|ing)",
     "DELEGATION_NL", "NL email delegation"),
]

# ---------------------------------------------------------------------------
# Allow-list patterns (read-only / safe, checked before confirm gates)
# ---------------------------------------------------------------------------

ALLOW_PATTERNS = [

    # Gmail reads
    (r"\bgmail\s+(search|messages?\s+search|get|list|labels?\s+(list|get))\b",
     "GMAIL_READ", "Gmail read"),

    # Gmail settings reads (list, get, export, help)
    (r"gmail\s+settings\s+(filters?\s+(list|get|export)|autoforward\s+get|"
     r"forwarding\s+(list|get)|delegates?\s+(list|get)|"
     r"vacation\s+get|send-?as\s+(list|get))\b",
     "GMAIL_SETTINGS_READ", "Gmail settings read"),

    # Drive reads
    (r"\bdrive\s+(search|ls|list|get|permissions?(\s+list)?|url|drives|info)\b",
     "DRIVE_READ", "Drive read"),

    # Calendar reads
    (r"\bcalendar\s+(list|get|events?\s+(list|get)|calendars?\s+list)\b",
     "CAL_READ", "Calendar read"),

    # Contacts read (no bulk/send chain)
    (r"\bcontacts?\s+(list|get|search)\b",
     "CONTACTS_READ", "Contacts read"),

    # Sheets read
    (r"\bsheets?\s+get\b",
     "SHEETS_READ", "Sheets read"),

    # Docs read
    (r"\bdocs?\s+(cat|export|get)\b",
     "DOCS_READ", "Docs read"),

    # gog help / version
    (r"\bgog\s+(help|--help|-h|version|--version)\b|--help\b",
     "GOG_HELP", "Help/version"),

    # Calendar create without attendees
    (r"\bcalendar\s+(events?\s+)?create\b(?!.+(--attendee|--guest))",
     "CAL_CREATE_SAFE", "Calendar create (no attendees)"),

    # Docs append/insert (additive only)
    (r"\bdocs?\s+(insert|append)\b",
     "DOCS_APPEND", "Docs append/insert"),

    # Drive non-destructive
    (r"\bdrive\s+(copy|rename|move|mkdir)\b",
     "DRIVE_NONDESTRUCTIVE", "Drive copy/rename/move/mkdir"),

    # Drive download (local only)
    (r"\bdrive\s+download\b",
     "DRIVE_DOWNLOAD", "Drive download (local)"),

    # Autoforward disable (protective)
    (r"autoforward\s+(update\s+)?--disable",
     "AUTOFORWARD_DISABLE_ALLOW", "Autoforward disable — protective"),

    # Vacation disable
    (r"gmail\s+settings\s+vacation\s+--disable",
     "VACATION_DISABLE_ALLOW", "Vacation disable — safe"),

    # Filter label-only CLI (no archive/trash/forward)
    (r"filters?\s+create.+--(?:never-spam|add-label|important|star)"
     r"(?!.+(--archive|--trash|--forward))",
     "FILTER_LABEL_ONLY", "Filter label/mark only"),

    # NL: label-only filter create ("create a filter that labels/marks/tags/sorts X as Y")
    (r"(create|set\s+up|add|make)\s+a?\s*(gmail\s+)?filter\s+(that\s+)?"
     r"(label|mark|tag|sort|categori[sz]e|move\s+to\s+folder|put\s+in)\b"
     r"(?!.+(archive|hide|skip\s+inbox|trash|delete|forward))",
     "FILTER_LABEL_NL", "NL label-only filter"),

    # "Show me / list all filters" — audit read
    (r"(show|list|display|get)\s+(me\s+)?all\s+(my\s+)?filters?\b"
     r"|(show\s+me|list|audit)\s+.{0,20}filters?\s+(that|which)\b",
     "FILTER_LIST_NL", "NL list/show filters — read"),

    # Audit/check — protective read intent
    (r"(audit|check|verify|list|show|find|review)\s+.{0,60}"
     r"(filter|forward(ing)?|autoforward|shar(e|ing)|permissions?|"
     r"public\s+file|nothing\s+is\s+public)\b",
     "SECURITY_AUDIT", "Security audit — read intent"),

    # "make sure nothing is public" / "ensure no files are public"
    (r"(make\s+sure|ensure|check|confirm|verify).{0,60}"
     r"(nothing|not|no\s+(file|doc)s?)\s+(is|are)\s+public\b",
     "AUDIT_NOT_PUBLIC", "Audit for public exposure"),

    # Calendar read/audit — check ACL, check if public, check sharing
    (r"(check|show|list|get|view|audit)\s+(my\s+)?calendar\s+"
     r"(acl|sharing|permissions?|access|settings?)\b"
     r"|(is|are)\s+my\s+(calendar|events?)\s+(public|shared|accessible)\?",
     "CAL_ACL_READ", "Calendar ACL read/audit"),

    # gog auth scope read — "what permissions", "list scopes", "does gog have"
    (r"(what\s+)?permissions?\s+does\s+gog\s+(currently\s+)?(have|hold)\b"
     r"|(list|show|get|check)\s+(the\s+)?(current\s+)?"
     r"(gog\s+)?(oauth\s+)?scopes?\b"
     r"|does\s+gog\s+(have|include|support)\s+(access\s+to\s+)?"
     r"(google\s+)?(sheets?|calendar|drive|contacts?|docs?|analytics|photos)\b"
     r"|can\s+gog\s+(access|read|write|use)\b"
     r"|why\s+is\s+gog\s+getting\s+a\s+403\b",
     "AUTH_SCOPE_READ", "Auth scope read/audit"),
]


# ---------------------------------------------------------------------------
# Evaluate
# ---------------------------------------------------------------------------

def evaluate(input_text: str) -> GateResult:
    """
    Evaluate input_text against safe-gog rules.
    Returns GateResult with verdict BLOCK | CONFIRM | ALLOW.
    """
    raw = input_text.strip()
    # Normalise: decode HTML entities, strip zero-width chars, etc.
    text = _normalise(raw)

    # 0. Pure informational questions — always ALLOW
    if re.match(
        r'^["\(]?(how\s+do\s+I|is\s+it\s+possible|what\s+are\s+the\s+risks?|'
        r'can\s+you\s+(explain|tell|show|describe)|explain\s+(how|what|why)|'
        r'what\s+is\s+(the\s+)?(purpose|risk|point|difference)|'
        r'does\s+gog\s+(need|require|have)|'
        r'shall\s+we|help\s+me\s+understand)',
        text, re.IGNORECASE
    ):
        return GateResult("ALLOW", "EXPLAIN_QUERY", "Informational question")

    # 1. Hard blocks
    for pattern, rule_id, detail in HARD_BLOCKS:
        if _match(pattern, text):
            return GateResult("BLOCK", rule_id, detail)

    # 2. Explicit allow (read-only / safe)
    for pattern, rule_id, detail in ALLOW_PATTERNS:
        if _match(pattern, text):
            # Label-only filters and a few other patterns bypass write-word suppressor
            always_allow = rule_id in (
                "FILTER_LABEL_ONLY", "AUTOFORWARD_DISABLE_ALLOW",
                "VACATION_DISABLE_ALLOW", "AUDIT_NOT_PUBLIC", "SECURITY_AUDIT",
                "GMAIL_SETTINGS_READ",
            )
            if always_allow:
                return GateResult("ALLOW", rule_id, detail)
            # Suppress ALLOW if write-action words / exfil verbs are present
            if not re.search(
                r"\b(send|delete|trash|share\s+.{0,30}(anyone|public|all\s+files?)|"
                r"overwrite|clear\s+(range|all|sheet)|"
                r"enable\s+(forward|autoforward)|"
                r"curl|wget|sftp|scp|nc\s|netcat|upload|webhook|pipe|tee\b|"
                r"requests\.post|axios\.post|fetch\s*\(|smtp|smtplib|"
                r"mail\s+-s|sendmail)\b",
                text, re.IGNORECASE
            ):
                return GateResult("ALLOW", rule_id, detail)

    # 3. Confirm gates
    for pattern, rule_id, detail in CONFIRM_GATES:
        if _match(pattern, text):
            return GateResult("CONFIRM", rule_id, detail)

    # 4. Default
    return GateResult("ALLOW", "DEFAULT", "No gate matched — safe by default")
