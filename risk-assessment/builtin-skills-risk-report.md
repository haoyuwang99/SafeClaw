# OpenClaw Built-in Skills — Security Risk Report

**Generated:** 2026-03-19 08:58 GMT+8  
**Last corrected:** 2026-03-23 (post-deep-review reclassifications applied)  
**Host:** HaoyutekiMacBook-Air (Darwin arm64)  
**Scope:** 55 classified built-in skills  
**Analyst:** Stan (AI Assistant)

---

## Executive Summary

| Risk Level | Count | Description |
|---|---|---|
| 🔴 Critical | 6 | Can cause irreversible harm (credential theft, financial loss, mass messaging, live surveillance) |
| 🟠 High | 14 | Can send messages, execute code, or expose private data |
| 🟡 Medium | 23 | Can leak data, overwrite files, or interact with cloud services |
| 🟢 Low | 12 | Read-only or well-sandboxed; minimal risk |

> **Reclassifications applied vs. initial report:**  
> `gh-issues` ↑ High → Critical · `ordercli` ↓ Critical → High · `xurl` ↑ Medium → High · `sonoscli` ↑ Low → Medium · `oracle` ↓ High → Medium · `nano-banana-pro` Unknown → Medium · `mcporter` Unknown → Medium · `canvas` Unknown → Medium

---

## Detailed Risk Profiles

---

### 🍎 Apple / macOS Skills

---

#### `apple-notes`

- **Function:** Create, edit, search, delete Apple Notes
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Notes may contain sensitive information (passwords stored in plain text by users, personal journals, financial info)
  - Bulk delete operations are irreversible without iCloud backup recovery
  - Search queries could expose note contents to logs
- **Threat Scenarios:**
  1. Agent misinterprets a "clear" command and deletes all notes
  2. Note contents leaked through session logs or summaries

---

#### `apple-reminders`

- **Function:** List, add, complete, delete Apple Reminders
- **Risk Level:** 🟢 Low
- **Attack Surface:**
  - Reminder deletion is recoverable via iCloud
  - No external network access
- **Threat Scenarios:**
  1. Accidental bulk completion of reminders

---

#### `bear-notes`

- **Function:** Manage Bear app notes (create, edit, search, delete)
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Same as apple-notes
  - Bear notes often used for long-form writing; bulk delete is especially destructive
  - Bear uses local SQLite DB; direct DB manipulation could corrupt data
- **Threat Scenarios:**
  1. Deletion of Bear notes without iCloud/backup recovery path
  2. Tag-based bulk operations could wipe entire categories

---

#### `things-mac`

- **Function:** Manage Things 3 task manager (add, complete, delete tasks/projects)
- **Risk Level:** 🟢 Low
- **Attack Surface:**
  - Deleting projects removes all sub-tasks permanently
  - No external network access in standard use
- **Threat Scenarios:**
  1. Project deletion cascades to all tasks

---

#### `imsg`

- **Function:** Send and read iMessages / SMS via macOS Messages app
- **Risk Level:** 🟠 High
- **Attack Surface:**
  - Sends real messages to real contacts — no undo
  - Access to full message history (privacy risk)
  - Could be used for social engineering or impersonation
  - SMS fallback means international charges possible
- **Threat Scenarios:**
  1. Agent sends a draft message prematurely to wrong contact
  2. Sensitive conversation history exposed in session context
  3. Automated message sending used for harassment or spam

---

### 📝 Notes & Productivity Skills

---

#### `notion`

- **Function:** Read/write Notion pages, databases, and workspaces
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Notion data is cloud-hosted; writes are immediately live
  - Pages can be shared publicly — agent could expose private data
  - Workspace admin tokens can delete entire databases
- **Threat Scenarios:**
  1. Agent modifies shared Notion page visible to entire team
  2. Private database records inadvertently shared or deleted
  3. API token with broad permissions used beyond intended scope

---

#### `obsidian`

- **Function:** Manage Obsidian vault (markdown notes, links, search)
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Direct filesystem access to vault directory
  - No recycle bin by default — deletions are permanent unless git-backed
  - Large vaults could overwhelm context window
- **Threat Scenarios:**
  1. Note deletion without backup
  2. Large vault loaded entirely into context
  3. Frontmatter manipulation breaking plugins

---

#### `canvas`

- **Function:** LMS integration (Canvas by Instructure) — submit assignments, post grades, manage course content
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Can submit assignments, post grades, or modify course content
  - Scope of API token may be broader than expected
- **Threat Scenarios:**
  1. Unintended assignment submission or grade modification
  2. Course content posted or deleted inadvertently

---

#### `trello`

- **Function:** Manage Trello boards, cards, and lists
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Boards can be public; agent could expose private cards
  - Card/board deletion is irreversible without backup
  - Trello Power-Ups and webhooks could be misconfigured
- **Threat Scenarios:**
  1. Moving cards to wrong board inadvertently
  2. Deleting board shared with team members

---

#### `oracle`

- **Function:** AI code analysis — bundle repo files and send to an external AI model (GPT) for review
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Source code and potentially secrets sent to external AI service
  - Large repos could overwhelm context or hit API cost limits
  - API key exposure through config or logs
- **Threat Scenarios:**
  1. Proprietary source code or secrets sent to third-party AI service
  2. Large repo bundle causes runaway API cost
  3. API key leaked in error logs

---

### 💬 Messaging & Communication Skills

---

#### `himalaya`

- **Function:** Send/receive email via IMAP/SMTP (any provider)
- **Risk Level:** 🟠 High
- **Attack Surface:**
  - Sends real emails — irreversible
  - Access to full inbox (sensitive/private emails)
  - Could be used for phishing or spam if compromised
  - SMTP credentials stored in config
- **Threat Scenarios:**
  1. Draft email sent before review to wrong recipient
  2. Sensitive inbox contents exposed in session context
  3. Bulk email send triggered accidentally

---

#### `discord`

- **Function:** Send messages, manage servers/channels on Discord
- **Risk Level:** 🟠 High
- **Attack Surface:**
  - Messages sent to public/shared channels are immediately visible
  - Bot tokens can have admin-level server permissions
  - Can kick/ban members or delete channels if permissions allow
  - Message deletion is possible but leaves audit trails
- **Threat Scenarios:**
  1. Sensitive message sent to wrong channel (e.g., DM intended, sent to public)
  2. Bot token with admin perms used to delete channels
  3. Mass mention (@everyone) triggered accidentally

---

#### `slack`

- **Function:** Send messages, manage workspaces and channels on Slack
- **Risk Level:** 🟠 High
- **Attack Surface:**
  - Messages sent to shared workspaces; colleagues will see them
  - Workspace admin tokens can archive channels, remove members
  - File uploads can expose sensitive documents
  - Slash commands can trigger integrations
- **Threat Scenarios:**
  1. Private message accidentally sent to public channel
  2. File with sensitive data uploaded to shared channel
  3. Channel archived or member removed by mistake

---

#### `wacli`

- **Function:** Send/receive WhatsApp messages via CLI
- **Risk Level:** 🟠 High
- **Attack Surface:**
  - Sends real WhatsApp messages to real phone numbers
  - Access to full chat history
  - WhatsApp groups — accidental sends visible to all members
  - Media sends could expose files
- **Threat Scenarios:**
  1. Message sent to wrong contact or group
  2. Private conversation context leaked to session
  3. Automated flood of messages causing WhatsApp account ban

---

#### `bluebubbles`

- **Function:** iMessage relay via BlueBubbles server (for non-Apple devices)
- **Risk Level:** 🟠 High
- **Attack Surface:**
  - Sends iMessages routed through a self-hosted server
  - Server security is user-managed; potential for interception if misconfigured
  - Same social risks as `imsg`
  - Server endpoint could be a single point of failure or compromise
- **Threat Scenarios:**
  1. BlueBubbles server misconfigured and exposed to internet
  2. Message sent to wrong contact
  3. iMessage history exposed via server logs

---

#### `voice-call`

- **Function:** Initiate voice calls (VoIP or system dialer)
- **Risk Level:** 🔴 Critical
- **Attack Surface:**
  - Initiates real phone calls — cannot be unsent
  - International calls could incur significant charges
  - Could be used for harassment or social engineering
  - Automated calling could trigger robocall detection/bans
- **Threat Scenarios:**
  1. Call initiated to wrong number
  2. International call racking up charges
  3. Call to emergency services (911/999) accidentally
  4. Repeated automated calls flagged as harassment

---

### 🌐 Google & Web Skills

---

#### `gog`

- **Function:** Gmail, Calendar, Drive, Contacts, Sheets, Docs via Google Workspace
- **Risk Level:** 🔴 Critical
- **Attack Surface:**
  - Gmail send: real emails to real people, irreversible
  - Drive: can delete/share files; shared links expose data publicly
  - Calendar: can delete/modify events affecting other attendees
  - Contacts: bulk export is a privacy risk
  - Sheets/Docs: edits are immediately live and synced
  - OAuth tokens can have very broad scopes
- **Threat Scenarios:**
  1. Email sent to wrong recipient with sensitive attachment
  2. Drive file shared publicly by mistake
  3. All calendar events deleted
  4. Contact list exported and leaked
  5. Financial spreadsheet overwritten

---

#### `xurl`

- **Function:** Post tweets, reply, quote, search, read posts, manage followers, send DMs, upload media via X (Twitter) API v2
- **Risk Level:** 🟠 High
- **Attack Surface:**
  - Posts publicly visible content to X/Twitter — irreversible without deletion
  - DMs sent to real accounts with no undo
  - Follow/block/mute actions affect real social relationships
  - API credentials (bearer token, OAuth) stored in config
  - Prompt injection via fetched tweet content
- **Threat Scenarios:**
  1. Tweet posted publicly with sensitive or embarrassing content
  2. DM sent to wrong user
  3. Mass follow/unfollow triggering account rate-limit or ban
  4. API credentials leaked in error logs

---

#### `goplaces`

- **Function:** Google Places / Maps integration (location search, directions, place details)
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Location queries reveal user's location or points of interest
  - API key exposure in logs
  - Location history could be inferred from search patterns
- **Threat Scenarios:**
  1. User's home/work location inferred from repeated queries
  2. API key leaked in error logs

---

#### `blogwatcher`

- **Function:** Monitor RSS feeds and blogs for new content
- **Risk Level:** 🟢 Low
- **Attack Surface:**
  - Large RSS feeds could overwhelm context
  - Fetched content could contain prompt injection
- **Threat Scenarios:**
  1. Malicious RSS entry injects instructions into agent context

---

### 💻 Development & Code Skills

---

#### `coding-agent`

- **Function:** Spawn Codex / Claude Code / Pi agents for coding tasks
- **Risk Level:** 🟠 High
- **Attack Surface:**
  - Sub-agents execute shell commands with `bypassPermissions`
  - Can modify, delete, or overwrite any file in the workspace
  - Can install packages (`npm install`, `pip install`) — supply chain risk
  - Git operations: force push, branch deletion
  - Network access during builds could fetch malicious dependencies
- **Threat Scenarios:**
  1. Sub-agent runs `rm -rf` or wipes project files
  2. Malicious package installed via npm/pip
  3. Force push overwrites main branch history
  4. Agent exfiltrates source code or secrets via network call

---

#### `github`

- **Function:** GitHub CLI operations — issues, PRs, CI, branches, releases
- **Risk Level:** 🟠 High
- **Attack Surface:**
  - Can delete branches, close issues, merge PRs without review
  - Release creation publishes to public npm/package registries
  - GitHub Actions can be triggered — runs arbitrary CI code
  - Repository deletion (if token has admin scope)
  - Secret exposure via CI log verbosity
- **Threat Scenarios:**
  1. Production branch deleted accidentally
  2. PR merged without required review
  3. GitHub Actions triggered with malicious workflow
  4. Repository made public accidentally

---

#### `gh-issues`

- **Function:** Fetch GitHub issues, spawn sub-agents to implement fixes, and open PRs automatically; supports `--yes --cron` for fully autonomous unattended pipelines
- **Risk Level:** 🔴 Critical
- **Attack Surface:**
  - Combines `coding-agent` + `github` risks in a single autonomous pipeline
  - `--yes --cron` mode = zero human oversight; runs indefinitely
  - Issue body content fed directly into sub-agent prompt — prompt injection vector
  - Auto-opened PRs may contain unreviewed or malicious code
  - Sub-agents spawned with `bypassPermissions`
- **Threat Scenarios:**
  1. Malicious issue body hijacks sub-agent to exfiltrate secrets or delete files
  2. Auto-opened PR with vulnerable code merged by another automation
  3. `--cron` mode left running, spawning agents indefinitely and consuming resources
  4. Sub-agent makes irreversible git changes (force push, branch delete) without review

---

#### `tmux`

- **Function:** Remote-control tmux sessions via keystroke injection and pane scraping
- **Risk Level:** 🟠 High
- **Attack Surface:**
  - Can inject arbitrary keystrokes into any tmux pane
  - Could target panes running databases, production servers, or sensitive CLIs
  - Pane scraping could capture passwords typed in terminal
  - No inherent scope limiting — all sessions accessible
- **Threat Scenarios:**
  1. Agent sends destructive keystrokes to wrong tmux pane
  2. Password typed into terminal captured by pane scrape
  3. Production server SSH session hijacked via keystroke injection
  4. Database shell receives destructive SQL via injected keys

---

### 🤖 AI & Media Generation Skills

---

#### `gemini`

- **Function:** Google Gemini CLI for one-shot Q&A, summaries, and generation
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - User data sent to Google's servers
  - Prompt injection in Gemini responses could influence agent
  - API key exposure
- **Threat Scenarios:**
  1. Sensitive data (PII, proprietary code) sent to Google
  2. Gemini response contains injected instructions

---

#### `openai-image-gen`

- **Function:** Generate images via OpenAI DALL-E API
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Content policy violations (generating NSFW/harmful imagery)
  - Prompt content sent to OpenAI servers
  - API cost — large-scale generation could incur significant charges
- **Threat Scenarios:**
  1. Policy-violating content generated
  2. High API spend from repeated generation

---

#### `openai-whisper`

- **Function:** Transcribe audio locally via OpenAI Whisper (local model)
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Audio files may contain sensitive spoken information
  - Large audio files could overwhelm context/memory
- **Threat Scenarios:**
  1. Private conversation transcribed and stored in plaintext

---

#### `openai-whisper-api`

- **Function:** Transcribe audio via OpenAI Whisper API (cloud)
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Audio data sent to OpenAI cloud — stronger privacy risk than local
  - API cost for large files
- **Threat Scenarios:**
  1. Sensitive audio (medical, legal, private calls) sent to OpenAI

---

#### `video-frames`

- **Function:** Extract frames from video files for analysis
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Large video files could cause memory/disk issues
  - Extracted frames stored on disk — sensitive video content persisted
- **Threat Scenarios:**
  1. Disk exhaustion from frame extraction of large video
  2. Sensitive video frames persisted unintentionally

---

#### `gifgrep`

- **Function:** Search and manipulate GIF files
- **Risk Level:** 🟢 Low
- **Attack Surface:**
  - Local file operations only; no network access
- **Threat Scenarios:**
  1. None significant

---

#### `songsee`

- **Function:** Music/lyrics search and display
- **Risk Level:** 🟢 Low
- **Attack Surface:**
  - Read-only external queries; no credentials or writes
- **Threat Scenarios:**
  1. None significant

---

### 🎵 Music & Audio Skills

---

#### `spotify-player`

- **Function:** Control Spotify playback (play, pause, skip, search)
- **Risk Level:** 🟢 Low
- **Attack Surface:**
  - Spotify credentials/token in config
  - Could interrupt active listening sessions
- **Threat Scenarios:**
  1. Playback interrupted unexpectedly

---

#### `sonoscli`

- **Function:** Control Sonos speakers (play, pause, volume, speaker grouping, queue management)
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Volume changes can be disruptive (sudden loud audio)
  - Speaker grouping/ungrouping affects all rooms
  - Local network only, but affects shared household audio
- **Threat Scenarios:**
  1. Volume set to maximum unexpectedly
  2. Multi-room grouping changed, disrupting other household members
  3. Playback queue cleared or replaced without warning

---

#### `sag`

- **Function:** ElevenLabs TTS — generate speech from text, including voice cloning
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Text content sent to ElevenLabs servers
  - Voice cloning features could be misused for impersonation/deepfake audio
  - API cost for large-scale generation
- **Threat Scenarios:**
  1. Voice cloning used to create deepfake audio of a real person
  2. Private text content sent to ElevenLabs cloud

---

#### `sherpa-onnx-tts`

- **Function:** Local TTS using Sherpa-ONNX models (fully offline)
- **Risk Level:** 🟢 Low
- **Attack Surface:**
  - Fully local — no network, no API keys
- **Threat Scenarios:**
  1. None significant

---

### 🏠 Smart Home & Hardware Skills

---

#### `openhue`

- **Function:** Control Philips Hue lights (on/off, color, brightness, scenes)
- **Risk Level:** 🟢 Low
- **Attack Surface:**
  - Local network only
  - Flashing lights could be problematic for photosensitive users
- **Threat Scenarios:**
  1. Rapid light changes triggered near photosensitive individuals

---

#### `camsnap`

- **Function:** Capture snapshots or clips from RTSP/ONVIF network cameras
- **Risk Level:** 🟠 High
- **Attack Surface:**
  - Captures images from physical cameras — serious privacy implications
  - Images stored on disk — sensitive visual content persisted
  - If camera covers private spaces (bedroom, bathroom), captures are extremely sensitive
- **Threat Scenarios:**
  1. Camera in private space captures images without consent
  2. Snapshots stored unencrypted and accessible to other processes
  3. Automated periodic capture creates unauthorized surveillance

---

#### `peekaboo`

- **Function:** macOS UI automation — screen capture, UI interaction, keyboard/mouse input, app control, clipboard access
- **Risk Level:** 🔴 Critical
- **Attack Surface:**
  - Screen capture reveals everything on screen (credentials, private messages, documents)
  - Keyboard/mouse injection can control any application
  - Clipboard access exposes copied passwords, tokens, and sensitive data
  - macOS TCC permission grants persistent access — no per-use prompt after initial grant
- **Threat Scenarios:**
  1. Screen capture exposes password manager or banking UI
  2. Keyboard injection types credentials into wrong application
  3. Clipboard read extracts a copied password or API key
  4. Sub-agent with bypassPermissions uses peekaboo for persistent screen surveillance

---

#### `blucli`

- **Function:** Control BluOS audio players (play, pause, volume, source selection, speaker grouping) on Bluesound/NAD devices
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Volume changes can be disruptive (sudden loud audio)
  - Multi-room grouping affects all paired speakers
  - Local network only, but affects shared household audio
- **Threat Scenarios:**
  1. Volume set to maximum unexpectedly on a NAD/Bluesound device
  2. Speaker grouping changed, disrupting other household members

---

#### `eightctl`

- **Function:** Control Eight Sleep smart mattress (temperature settings, schedules, sleep data)
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Sleep schedule and health biometrics are sensitive data
  - Disrupting sleep temperature unexpectedly during the night
  - Eight Sleep cloud account credentials
- **Threat Scenarios:**
  1. Sleep temperature changed during night unexpectedly
  2. Biometric sleep data exposed in session logs

---

#### `nano-banana-pro`

- **Function:** Gemini image generation and editing (via Google Gemini 3 Pro)
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Prompts and local images sent to Google's servers
  - Image generation of real people could create harmful content
  - API cost for bulk generation
- **Threat Scenarios:**
  1. Image of a real person generated without consent
  2. NSFW or policy-violating image generated
  3. Sensitive local image sent to Google cloud

---

### 🔐 Security & Secrets Skills

---

#### `healthcheck`

- **Function:** Security audits, firewall/SSH hardening, risk posture reviews for OpenClaw deployments
- **Risk Level:** 🟢 Low
- **Attack Surface:**
  - Reads system config files — non-destructive
  - Audit results could reveal exploitable weaknesses if logged insecurely
- **Threat Scenarios:**
  1. Audit report containing system vulnerabilities stored in plaintext

---

#### `1password`

- **Function:** Access 1Password vault (retrieve credentials, manage vault items)
- **Risk Level:** 🔴 Critical
- **Attack Surface:**
  - Direct access to all stored credentials — passwords, API keys, certificates
  - A single compromised session could expose entire vault
  - Credentials surfaced in agent context could be logged
  - Vault item creation/deletion is irreversible without backup
- **Threat Scenarios:**
  1. All vault credentials exposed in session context/logs
  2. Master password or Secret Key extracted
  3. Credential shared to wrong service or person
  4. Vault item deleted accidentally

---

#### `safe`

- **Function:** Secrets/vault management (local secrets store, analogous to macOS Keychain or a custom vault)
- **Risk Level:** 🔴 Critical
- **Attack Surface:**
  - Same risk profile as `1password`
  - Scope of stored secrets may be broader than expected
- **Threat Scenarios:**
  1. Credential or secret exposed in session context
  2. Secrets written to logs unintentionally
  3. Vault item deleted without recovery path

---

#### `safety-confirm`

- **Function:** Meta-skill that gates operations behind explicit human confirmation
- **Risk Level:** 🟢 Low
- **Attack Surface:**
  - This is a safety control, not a risk source
  - Cannot be bypassed by downstream prompts (by design)
- **Threat Scenarios:**
  1. None — this skill reduces risk for other skills

---

### 🧠 Skills Management Skills

---

#### `clawhub`

- **Function:** Install, update, search, and publish agent skills from clawhub.com
- **Risk Level:** 🟠 High
- **Attack Surface:**
  - Installing a malicious or poisoned skill can compromise the entire agent
  - Skills execute arbitrary code with agent-level permissions
  - Supply chain attack via compromised skill package
  - `clawhub publish` could accidentally expose private skills publicly
- **Threat Scenarios:**
  1. Malicious skill installed from clawhub containing prompt injection or RCE
  2. Skill with embedded exfiltration code installed
  3. Compromised skill package in clawhub registry
  4. Private skill published publicly by mistake

---

#### `skill-creator`

- **Function:** Create, edit, improve, or audit AgentSkills and SKILL.md files
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Created skills execute with agent-level trust
  - Poorly-authored skills could introduce unintended behavior
  - SKILL.md prompt injection if content comes from an untrusted source
- **Threat Scenarios:**
  1. User-provided skill spec contains embedded malicious instructions
  2. Created skill has unintended side effects (e.g., auto-sending messages on activation)

---

#### `skill-logger`

- **Function:** Log skill activation and usage events
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Logs could capture sensitive parameters (passwords, API keys passed to skills)
  - Log files accessible to other processes on the system
  - Log accumulation — large files over time causing disk issues
- **Threat Scenarios:**
  1. Credential passed to a skill inadvertently captured in log
  2. Log file grows unbounded and causes disk exhaustion

---

### 📊 Monitoring & Logs Skills

---

#### `session-logs`

- **Function:** Access and review agent session transcripts
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Sessions may contain sensitive information (credentials, personal data, private conversations)
  - Large session logs could overwhelm context
  - Logs shared across sessions could leak context between users
- **Threat Scenarios:**
  1. Session containing credentials reviewed and exposed
  2. Large session log loaded into context causing token exhaustion

---

#### `model-usage`

- **Function:** Track AI model token usage and costs
- **Risk Level:** 🟢 Low
- **Attack Surface:**
  - Read-only usage stats — no external writes, no sensitive data
- **Threat Scenarios:**
  1. None significant

---

### 🛠️ Utilities Skills

---

#### `summarize`

- **Function:** Summarize or extract text/transcripts from URLs, podcasts, and local files
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Fetched URL content could contain prompt injection
  - Large files loaded into context could cause token exhaustion
  - Content sent to AI model — privacy concern for sensitive docs
- **Threat Scenarios:**
  1. Malicious URL injects instructions via summarized content
  2. Confidential document summarized and content leaked via session logs

---

#### `weather`

- **Function:** Get current weather and forecasts via wttr.in or Open-Meteo
- **Risk Level:** 🟢 Low
- **Attack Surface:**
  - Location queries reveal approximate user location
  - No API key required — minimal credential risk
- **Threat Scenarios:**
  1. User location inferred from repeated location-specific queries

---

#### `nano-pdf`

- **Function:** PDF creation, parsing, or manipulation
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - Large PDFs could overwhelm context
  - PDF content may contain sensitive data
  - Generated PDFs could embed system metadata
- **Threat Scenarios:**
  1. Large PDF loaded into context causing token exhaustion
  2. Metadata in generated PDF leaks system or user information

---

#### `ordercli`

- **Function:** Food delivery ordering via Foodora CLI (browse menus, place orders, track delivery)
- **Risk Level:** 🟠 High
- **Attack Surface:**
  - Places real orders with real financial transactions
  - Orders cannot always be cancelled once confirmed
  - Payment method details in config
  - Accidental repeat orders
- **Threat Scenarios:**
  1. Large or duplicate order placed accidentally
  2. Order placed to wrong delivery address
  3. Payment credentials exposed in config or logs

---

#### `mcporter`

- **Function:** MCP (Model Context Protocol) client — call MCP tools, manage server config, run auth flows
- **Risk Level:** 🟡 Medium
- **Attack Surface:**
  - MCP tool calls can write or modify data on connected servers
  - `--stdio` flag spawns subprocess — arbitrary code execution risk
  - Auth flows could expand token scope beyond intended access
  - Config changes persist across sessions
- **Threat Scenarios:**
  1. MCP tool call writes or deletes data on a connected server
  2. `--stdio` used to execute an arbitrary subprocess
  3. Auth flow grants broader permissions than intended

---

## Risk Matrix Summary

| Skill | Risk Level |
|---|---|
| voice-call | 🔴 Critical |
| peekaboo | 🔴 Critical |
| gog | 🔴 Critical |
| 1password | 🔴 Critical |
| safe | 🔴 Critical |
| gh-issues | 🔴 Critical |
| imsg | 🟠 High |
| himalaya | 🟠 High |
| discord | 🟠 High |
| slack | 🟠 High |
| wacli | 🟠 High |
| bluebubbles | 🟠 High |
| coding-agent | 🟠 High |
| github | 🟠 High |
| tmux | 🟠 High |
| camsnap | 🟠 High |
| clawhub | 🟠 High |
| xurl | 🟠 High |
| ordercli | 🟠 High |
| canvas | 🟡 Medium |
| notion | 🟡 Medium |
| obsidian | 🟡 Medium |
| bear-notes | 🟡 Medium |
| apple-notes | 🟡 Medium |
| trello | 🟡 Medium |
| oracle | 🟡 Medium |
| goplaces | 🟡 Medium |
| gemini | 🟡 Medium |
| openai-image-gen | 🟡 Medium |
| openai-whisper | 🟡 Medium |
| openai-whisper-api | 🟡 Medium |
| video-frames | 🟡 Medium |
| blucli | 🟡 Medium |
| sonoscli | 🟡 Medium |
| eightctl | 🟡 Medium |
| sag | 🟡 Medium |
| nano-banana-pro | 🟡 Medium |
| skill-creator | 🟡 Medium |
| skill-logger | 🟡 Medium |
| session-logs | 🟡 Medium |
| nano-pdf | 🟡 Medium |
| summarize | 🟡 Medium |
| mcporter | 🟡 Medium |
| apple-reminders | 🟢 Low |
| things-mac | 🟢 Low |
| blogwatcher | 🟢 Low |
| gifgrep | 🟢 Low |
| songsee | 🟢 Low |
| spotify-player | 🟢 Low |
| sherpa-onnx-tts | 🟢 Low |
| openhue | 🟢 Low |
| healthcheck | 🟢 Low |
| safety-confirm | 🟢 Low |
| weather | 🟢 Low |
| model-usage | 🟢 Low |

---

*Report generated by Stan (OpenClaw AI Assistant) — 2026-03-19*  
*Corrected 2026-03-23: reclassifications from post-deep-review applied (gh-issues ↑, ordercli ↓, xurl ↑, sonoscli ↑, oracle ↓, nano-banana-pro confirmed, mcporter confirmed, canvas confirmed)*
