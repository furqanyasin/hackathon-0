# Hackathon 0 — Personal AI Employee

**Tier: Gold** | **Deadline: 27 March 2026**

A local-first autonomous AI agent that manages personal and business affairs 24/7 using Claude Code as the reasoning engine and Obsidian as the memory/dashboard.

---

## Architecture

```
Perception (Watchers) → Reasoning (Claude Code) → Action (MCP Servers)
```

- **Brain**: Claude Code
- **Memory/GUI**: Obsidian vault (local Markdown)
- **Watchers**: Python scripts monitoring Gmail, WhatsApp, filesystem
- **Hands**: MCP servers for external actions
- **Orchestration**: PM2 process manager

## Setup

### Prerequisites
- Python 3.13+
- Node.js v22+
- Claude Code
- Obsidian v1.10.6+
- PM2: `npm install -g pm2`

### Installation

```bash
# Clone the repo
git clone https://github.com/furqanyasin/hackathon-0.git
cd hackathon-0

# Install Python dependencies
uv sync

# Install Playwright browser
uv run playwright install chromium

# Copy and fill in your credentials
cp .env.example .env
```

### Gmail Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → Enable Gmail API
3. Create OAuth2 credentials (Desktop app) → Download as `credentials.json`
4. Place `credentials.json` in the project root

### Open Vault in Obsidian
Open Obsidian → "Open folder as vault" → select `obsidian_vault/`

### Run Watchers

```bash
# Start both watchers via PM2 (keeps them alive 24/7)
pm2 start watchers/gmail_watcher.py --interpreter python --name gmail-watcher
pm2 start watchers/filesystem_watcher.py --interpreter python --name file-watcher
pm2 save
pm2 startup
```

### Drop files manually
Drop any `.md` or `.txt` file into `obsidian_vault/Inbox/` to trigger processing.

---

## Vault Structure

```
obsidian_vault/
├── Dashboard.md          # Real-time status overview
├── Company_Handbook.md   # AI rules of engagement
├── Business_Goals.md     # Targets and metrics
├── Inbox/                # Manual file drop folder
├── Needs_Action/         # Watchers write here
├── Plans/                # Claude writes PLAN_*.md here
├── Pending_Approval/     # HITL approval queue
├── Approved/             # Move files here to approve
├── Rejected/             # Move files here to reject
├── Done/                 # Completed tasks
├── Logs/                 # Audit logs (JSON)
├── Briefings/            # Monday CEO briefings
└── Accounting/           # Financial records
```

---

## Security

- Credentials stored in `.env` (never committed)
- `credentials.json` and `token.json` are gitignored
- All sensitive actions require human approval via HITL workflow
- `DRY_RUN=true` in `.env` during development

---

## Tier: Gold

Implements all Bronze + Silver + Gold requirements:
- Gmail + WhatsApp + filesystem watchers
- LinkedIn, Facebook, Instagram, Twitter integration
- Odoo Community ERP via MCP (JSON-RPC)
- Weekly Monday Morning CEO Briefing
- Ralph Wiggum autonomous loop
- Full audit logging
- Error recovery & graceful degradation
