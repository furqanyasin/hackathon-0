# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **Hackathon 0: Personal AI Employee** — building an autonomous Digital FTE (Full-Time Equivalent) that manages personal and business affairs 24/7. The system is **local-first**, using Claude Code as the reasoning engine and Obsidian as the memory/dashboard.

## Tech Stack

- **Brain**: Claude Code (reasoning engine)
- **Memory/GUI**: Obsidian vault (`AI_Employee_Vault/`) with local Markdown files
- **Watchers**: Python scripts monitoring Gmail, WhatsApp, filesystem
- **Hands**: MCP servers (email, browser, calendar, etc.)
- **Orchestration**: `orchestrator.py` + `watchdog.py`
- **Python**: 3.13+, Node.js v24+ LTS

## Running the System

```bash
# Start a watcher (use PM2 to keep alive)
pm2 start gmail_watcher.py --interpreter python3
pm2 start filesystem_watcher.py --interpreter python3
pm2 save && pm2 startup

# Or run directly (fragile — exits on crash)
python gmail_watcher.py
python orchestrator.py

# Dry-run mode (no real external actions)
DRY_RUN=true python orchestrator.py

# Ralph Wiggum autonomous loop
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

## Vault Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time summary (bank balance, pending tasks)
├── Company_Handbook.md       # Rules of engagement for the AI
├── Business_Goals.md         # Targets, metrics, active projects
├── Needs_Action/             # Watchers drop .md files here for Claude to process
├── Plans/                    # Claude writes PLAN_*.md files here
├── Pending_Approval/         # Sensitive actions waiting for human review
├── Approved/                 # Move files here to approve actions
├── Rejected/                 # Move files here to reject actions
├── In_Progress/<agent>/      # Claim-by-move: first agent to claim owns the task
├── Done/                     # Completed tasks
├── Logs/YYYY-MM-DD.json      # Audit logs (retain 90 days minimum)
├── Accounting/               # Bank transactions, rates
├── Briefings/                # Monday Morning CEO Briefings
└── Invoices/                 # Generated invoice files
```

## Core Architecture: Perception → Reasoning → Action

### Perception (Watchers)
Python scripts extending `BaseWatcher` from `base_watcher.py`. Each watcher:
- Polls an external source (Gmail, WhatsApp Web via Playwright, filesystem)
- Creates `.md` files in `/Needs_Action/` with YAML frontmatter (`type`, `status: pending`, etc.)
- Runs continuously — must use PM2 or `watchdog.py` for resilience

### Reasoning (Claude Code)
Claude reads `/Needs_Action/`, reasons using `Company_Handbook.md` and `Business_Goals.md`, then:
- Writes `PLAN_*.md` files in `/Plans/`
- Creates approval request files in `/Pending_Approval/` for sensitive actions
- Moves processed files to `/Done/`

### Action (MCP Servers)
Configured in `~/.config/claude-code/mcp.json`. Key servers: `filesystem`, `email-mcp`, `browser-mcp`, `calendar-mcp`. For sensitive actions (payments, emails to new contacts), Claude writes an approval file — never acts directly.

## Key Patterns

**Human-in-the-Loop (HITL)**: All sensitive actions (payments > $50, emails to new contacts, social media replies) require an approval file in `/Pending_Approval/`. Claude polls `/Approved/` before executing.

**Ralph Wiggum Loop**: A Stop hook that re-injects the prompt if the task file hasn't moved to `/Done/`, keeping Claude iterating until completion. Reference: `github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum`

**Claim-by-move rule**: An agent claims a task by moving it from `/Needs_Action/` to `/In_Progress/<agent>/`. Other agents must skip claimed tasks.

**Single-writer rule**: Only Local agent writes to `Dashboard.md`. Cloud agent writes to `/Updates/` and Local merges.

## Security Rules

- **Never** store credentials in the vault or in plain text. Use `.env` (gitignored) or OS keychain.
- **Never** auto-approve payments to new recipients.
- All action scripts must support `DRY_RUN=true` to log without executing.
- Secrets never sync between Local and Cloud (`WhatsApp sessions`, `.env`, banking tokens).
- Log every action to `/Vault/Logs/YYYY-MM-DD.json` with `timestamp`, `action_type`, `approval_status`.

## Tier Deliverables

| Tier | Key Requirements |
|------|-----------------|
| **Bronze** | Obsidian vault + `Dashboard.md` + `Company_Handbook.md`, 1 Watcher, basic folder structure, all AI as Agent Skills |
| **Silver** | Bronze + 2+ Watchers, LinkedIn auto-posting, `Plan.md` generation, 1 MCP server, HITL workflow, cron scheduling |
| **Gold** | Silver + full cross-domain integration, Odoo Community ERP (self-hosted) via JSON-RPC MCP, Facebook/Instagram/Twitter, Weekly CEO Briefing, Ralph Wiggum loop, error recovery, audit logging |

## Submission Requirements

- GitHub repository with `README.md` (setup + architecture)
- Demo video (5–10 minutes)
- Security disclosure (how credentials are handled)
- Tier declaration (Bronze / Silver / Gold)
- Submit at: `https://forms.gle/JR9T1SJq5rmQyGkGA`
