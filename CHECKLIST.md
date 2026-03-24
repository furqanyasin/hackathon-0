# Hackathon 0 — Full Checklist (Bronze → Silver → Gold)
**Deadline: 27 March 2026 | No late submissions**
**Submit at: https://forms.gle/JR9T1SJq5rmQyGkGA**
**Last updated: 2026-03-24 | Current tier: BRONZE → SILVER next**

---

## PRE-SETUP

- [x] Install Claude Code — v2.1.81 ✅
- [x] Install Python 3.13+ — v3.13.7 ✅
- [x] Install Node.js — v22.18.0 ✅ (spec says v24, but v22 works fine)
- [x] Install PM2 — v6.0.14 ✅
- [x] Install uv — v0.9.26 ✅
- [x] Install Obsidian — v1.12.7 ✅
- [x] Set up UV Python project at `D:\PIAIC\hackathon-0` ✅
- [x] Install all Python deps (watchdog, playwright, google-auth, dotenv) ✅
- [x] Install Playwright Chromium browser ✅
- [x] Create `.env` file ✅
- [x] Add `.env` to `.gitignore` ✅
- [x] Open `obsidian_vault/` as a vault in Obsidian ✅
- [ ] Create a GitHub repository for submission

---

## BRONZE TIER — Foundation

### Vault Structure
- [x] Create `Dashboard.md` ✅
- [x] Create `Company_Handbook.md` ✅
- [x] Create `Business_Goals.md` ✅
- [x] Create folders: `/Needs_Action/`, `/Done/`, `/Plans/`, `/Pending_Approval/`, `/Approved/`, `/Rejected/`, `/Logs/`, `/Briefings/`, `/Invoices/`, `/Accounting/` ✅

### Watcher Script
- [x] `base_watcher.py` — BaseWatcher class implemented ✅
- [x] `filesystem_watcher.py` — watches `/Inbox/`, writes to `/Needs_Action/` ✅
- [x] `gmail_watcher.py` — working, credentials set up, token.json saved ✅
- [x] Both watchers running via PM2 ✅

### Claude Code Integration
- [x] Claude reads from vault (`/Needs_Action/`) ✅
- [x] Claude writes to vault (`Dashboard.md` updated with email summary) ✅
- [x] Full read → write cycle verified end-to-end ✅

### Agent Skills
- [x] `process-inbox-skill` created — reads Needs_Action, creates Plans, handles HITL ✅

---

## SILVER TIER — Functional Assistant

### Additional Watchers
- [x] `filesystem_watcher.py` ✅
- [x] `gmail_watcher.py` ✅
- [x] `whatsapp_watcher.py` ✅ (code done — needs QR scan to activate)
  - Run setup: `uv run python watchers/whatsapp_watcher.py --setup`
  - Then: `pm2 start watchers/whatsapp_watcher.py --interpreter python --name whatsapp-watcher`
- [ ] WhatsApp QR scan done and session saved

### LinkedIn Auto-Posting
- [x] `watchers/linkedin_poster.py` ✅ (code done — needs LinkedIn API token)
  - Go to linkedin.com/developers → Create app → Get Access Token
  - Add `LINKEDIN_ACCESS_TOKEN=` to `.env`
- [ ] LinkedIn access token added to `.env`

### Claude Reasoning Loop
- [x] `orchestrator.py` — watches Needs_Action, triggers Claude, creates PLAN_*.md ✅
- [x] Plan files include `status: pending_approval` for sensitive types ✅
- [x] Plans moved to `/Done/` on completion ✅
- [ ] Start orchestrator: `pm2 start orchestrator.py --interpreter python --name orchestrator`

### MCP Server
- [x] `mcps/email_mcp.py` — watches /Approved/, sends emails via Gmail API ✅
- [ ] Start email MCP: `pm2 start mcps/email_mcp.py --interpreter python --name email-mcp`
- [ ] Test: create an approval file in /Pending_Approval/, move to /Approved/, verify email sent (DRY_RUN=true first)

### Human-in-the-Loop (HITL)
- [x] Claude writes to `/Pending_Approval/` instead of acting directly ✅
- [x] Email MCP watches `/Approved/` and executes actions ✅
- [x] Files move to `/Done/` after completion ✅

### Scheduling (Windows Task Scheduler)
- [x] `setup_scheduler.ps1` created ✅
- [ ] Run as Admin: `powershell -ExecutionPolicy Bypass -File setup_scheduler.ps1`

### Agent Skills
- [x] `silver-inbox-skill` — full Silver processing with Plans, HITL, LinkedIn draft, audit logging ✅

---

## GOLD TIER — Autonomous Employee

> Complete everything in Silver first.

### Full Cross-Domain Integration
- [ ] Personal domain: Gmail + WhatsApp handled
- [ ] Business domain: Social media + accounting integrated

### Odoo Community ERP (Self-Hosted)
- [ ] Install Odoo Community Edition (local or VM)
- [ ] Set up basic accounting in Odoo
- [ ] Build MCP server using Odoo JSON-RPC API (Odoo 19+)
- [ ] Claude can create/read accounting entries via MCP
- [ ] Human approval required before posting invoices/payments

### Social Media Integration
- [ ] Facebook + Instagram: post messages and generate activity summary
- [ ] Twitter/X: post messages and generate activity summary
- [ ] All posts go through HITL approval before sending

### Multiple MCP Servers
- [ ] `email-mcp`
- [ ] `browser-mcp`
- [ ] `odoo-mcp`
- [ ] Social media MCP

### Weekly CEO Briefing
- [ ] Scheduled every Sunday night via Windows Task Scheduler
- [ ] Claude reads `Business_Goals.md`, `/Done/`, `/Accounting/`
- [ ] Generates `/Briefings/YYYY-MM-DD_Monday_Briefing.md` with revenue, bottlenecks, suggestions

### Error Recovery & Graceful Degradation
- [ ] `retry_handler.py` — exponential backoff
- [ ] `watchdog.py` — monitors and restarts failed processes
- [ ] `DRY_RUN` env flag working correctly

### Audit Logging
- [ ] Every action logged to `/Logs/YYYY-MM-DD.json`
- [ ] Log format: `timestamp`, `action_type`, `actor`, `target`, `parameters`, `approval_status`, `result`

### Ralph Wiggum Loop
- [ ] Stop hook implemented in `.claude/settings.json`
- [ ] Hook checks if task file is in `/Done/` — if not, re-injects prompt
- [ ] Max iterations guard (`--max-iterations 10`)

### Documentation
- [ ] `README.md` with setup instructions + architecture overview
- [ ] Architecture diagram included
- [ ] Lessons learned section

### Agent Skills
- [ ] All Gold features implemented as Agent Skills

---

## PRESENTATION PREP

### Demo Video (5–10 minutes)
- [ ] Show vault folder structure in Obsidian
- [ ] Trigger a Watcher → show `.md` file appearing in `/Needs_Action/`
- [ ] Show Claude reasoning → generating `PLAN_*.md`
- [ ] Show HITL: approval file created → move to `/Approved/` → MCP executes
- [ ] Show task moving to `/Done/` + `Dashboard.md` updating
- [ ] Show Monday Morning CEO Briefing generated (Gold)
- [ ] Show Ralph Wiggum loop running autonomously (Gold)

### Things to Explain
- [ ] Why local-first? — Privacy, data stays on your machine
- [ ] Why Claude Code? — Reasoning engine that reads/writes files natively
- [ ] Why Obsidian? — Human-readable Markdown, GUI + memory in one
- [ ] How HITL prevents accidents — `/Pending_Approval/` → `/Approved/` flow
- [ ] Ralph Wiggum loop — solves the "lazy agent" problem
- [ ] Security model — .env, no credentials in vault, audit logging
- [ ] Digital FTE value prop — 168 hrs/week vs 40 hrs, ~90% cost reduction

### GitHub Submission
- [ ] Public repo (or private with judge access)
- [ ] `README.md` with setup + architecture
- [ ] `.env.example` committed (never `.env`)
- [ ] Demo video linked or uploaded
- [ ] Security disclosure in README
- [ ] Tier declaration: **Gold**

---

## SUBMISSION
- [ ] Fill the form: **https://forms.gle/JR9T1SJq5rmQyGkGA**
- [ ] Declare tier: **Gold**
- [ ] Submit before: **27 March 2026**

---

## KEY RULES — NEVER FORGET

| Rule | Why |
|------|-----|
| Never commit `.env` | Credentials exposed = system compromised |
| Never auto-approve payments to new recipients | HITL is mandatory for money |
| Always use `DRY_RUN=true` during development | Prevents real emails/posts/payments |
| Single-writer rule for `Dashboard.md` | Local agent owns it — no race conditions |
| Claim-by-move for `/Needs_Action/` | Prevents duplicate task processing |
| PM2 for all watchers | Scripts die without a process manager |
| Log every action | Judges and ethics require full audit trail |
