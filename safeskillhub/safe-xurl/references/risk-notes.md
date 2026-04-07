# Risk Notes for safe-xurl

## Threat Model Summary

The `xurl` skill provides full CLI access to the X (Twitter) API v2, including posting, replying, DMs, follows, blocks, media upload, and raw endpoint access. This is a high-risk capability: actions are publicly visible, tied to user identity, and largely irreversible in practice.

The original skill already identifies credential safety as mandatory and bans `--verbose` and inline secret flags. This safe wrapper enforces those constraints and adds content confirmation for all public-facing actions.

## Key Risks

### 1. Credential Exposure
Risk:
- `~/.xurl` contains OAuth tokens, API keys, and app secrets in YAML format.
- `--verbose` flag outputs HTTP headers including Authorization tokens.
- Inline secret flags (--bearer-token, etc.) expose credentials in shell history and logs.

Mitigation:
- Block all access to `~/.xurl`.
- Block `--verbose`/`-v` flag.
- Block all inline secret flags.
- App registration must be done outside agent context.

### 2. Unreviewed Public Posts
Risk:
- An agent could post tweets, replies, or quotes without the user reviewing the exact content.
- Adversarial prompts could manipulate post content.
- Public posts are immediately visible and archived by third parties.

Mitigation:
- Block posting without explicit user-provided text.
- Show exact text in confirmation before publishing.

### 3. Unsolicited DMs
Risk:
- Agent-initiated DMs constitute unsolicited contact.
- Could be used for spam or harassment.

Mitigation:
- Require explicit recipient and message from user.
- Confirm before every DM send.

### 4. Bulk Engagement Abuse
Risk:
- Automated mass follow/like/repost loops violate X platform rules.
- Can trigger rate limits, suspensions, or bans.
- Could constitute spam or manipulation.

Mitigation:
- Block all bulk/looped engagement patterns.

### 5. Destructive Actions
Risk:
- `xurl delete` permanently removes posts.
- `xurl block` severs social connections.
- These cannot be undone (deleted content is gone).

Mitigation:
- Require confirmation for all destructive actions.

### 6. Media Upload / Exfiltration
Risk:
- `xurl media upload` sends local files to X servers.
- Could be used to exfiltrate sensitive files.

Mitigation:
- Require confirmation with explicit file path before any upload.

### 7. Raw API Access
Risk:
- xurl supports raw curl-style access to any v2 endpoint.
- This bypasses shortcut-level safety and could access undocumented or dangerous endpoints.

Mitigation:
- Apply the same confirmation rules to raw API calls.
- Block raw calls that would expose credentials or perform write operations without confirmation.

## Safe vs Unsafe

Safe:
- Read posts, search, timeline, mentions
- Auth status check
- Profile lookups
- List bookmarks, likes, followers

Confirm:
- Post, reply, quote tweets
- Send DMs
- Delete posts
- Follow/unfollow, block/unblock
- Like, repost
- Upload media
- OAuth authentication

Block:
- Expose ~/.xurl or tokens
- Use --verbose flag
- Use inline secret flags
- Bulk engagement loops
- Post without user-provided content
- Register app credentials in agent context
