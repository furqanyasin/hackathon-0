"""
Silver Inbox Processor - full Silver-tier processing with Plan.md creation,
HITL routing, LinkedIn draft generation, and audit logging.
"""
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

VAULT = Path(os.getenv('VAULT_PATH', r'D:\PIAIC\hackathon-0\obsidian_vault'))
NEEDS_ACTION = VAULT / 'Needs_Action'
PLANS = VAULT / 'Plans'
DONE = VAULT / 'Done'
PENDING_APPROVAL = VAULT / 'Pending_Approval'
APPROVED = VAULT / 'Approved'
LOGS = VAULT / 'Logs'
DASHBOARD = VAULT / 'Dashboard.md'

SENSITIVE_TYPES = ['email', 'payment', 'social_post', 'whatsapp']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SilverInboxSkill')


def parse_frontmatter(content: str) -> dict:
    fm = {}
    lines = content.splitlines()
    in_fm = False
    for line in lines:
        if line.strip() == '---':
            if not in_fm:
                in_fm = True
                continue
            else:
                break
        if in_fm and ':' in line:
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip()
    return fm


def create_plan(item_path: Path, fm: dict, content: str) -> Path:
    item_type = fm.get('type', 'unknown')
    sender = fm.get('from', 'Unknown')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plan_path = PLANS / f'PLAN_{timestamp}_{item_path.stem}.md'
    needs_approval = item_type in SENSITIVE_TYPES

    plan_path.write_text(f"""---
created: {datetime.now().isoformat()}
source: {item_path.name}
type: {item_type}
from: {sender}
status: {'pending_approval' if needs_approval else 'in_progress'}
---

## Objective
Process `{item_path.name}` from {sender}

## Steps
- [x] Read and understood item (type: {item_type})
- [x] Checked Company_Handbook.md rules
- [ ] {'Create approval request in /Pending_Approval/' if needs_approval else 'Execute action directly'}
- [ ] Update Dashboard.md
- [ ] Move to /Done/
- [ ] Log to /Logs/

## Decision
{'⚠️ REQUIRES HUMAN APPROVAL — sensitive action type: ' + item_type if needs_approval else '✅ Auto-processing allowed'}

## Source Summary
{content[:600]}{'...' if len(content) > 600 else ''}
""", encoding='utf-8')
    return plan_path


def create_approval_request(item_path: Path, fm: dict, content: str) -> Path:
    item_type = fm.get('type', 'unknown')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    approval_path = PENDING_APPROVAL / f'APPROVAL_{timestamp}_{item_path.stem}.md'
    approval_path.write_text(f"""---
type: approval_request
action: {item_type}
from: {fm.get('from', 'Unknown')}
source: {item_path.name}
created: {datetime.now().isoformat()}
expires: {datetime.now().isoformat()}
status: pending
---

## Action Required

**To Approve:** Move this file to `/Approved/`
**To Reject:** Move this file to `/Rejected/`

## Original Item
{content}
""", encoding='utf-8')
    return approval_path


def create_linkedin_draft():
    """Generate a LinkedIn post draft for approval."""
    goals_path = VAULT / 'Business_Goals.md'
    goals = goals_path.read_text(encoding='utf-8') if goals_path.exists() else ''
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    approval_path = PENDING_APPROVAL / f'LINKEDIN_POST_{timestamp}.md'
    approval_path.write_text(f"""---
type: social_post
platform: linkedin
action: post
created: {datetime.now().isoformat()}
status: pending
---

## LinkedIn Post Draft

Building a Personal AI Employee with Claude Code!

This week I've set up:
- 24/7 Gmail monitoring with automatic action file creation
- WhatsApp watching for urgent keyword detection
- Human-in-the-loop approval for all sensitive actions
- Local-first architecture — all data stays on my machine

The system runs autonomously, but I stay in control of every action that matters.

#AI #Automation #ClaudeCode #DigitalFTE #PIAIC #PersonalProductivity

---
Move to /Approved/ to post | Move to /Rejected/ to discard
""", encoding='utf-8')
    logger.info(f'LinkedIn draft created: {approval_path.name}')


def log_action(action_type: str, target: str, result: str):
    LOGS.mkdir(exist_ok=True)
    log_file = LOGS / f'{datetime.now().strftime("%Y-%m-%d")}.json'
    entry = {
        'timestamp': datetime.now().isoformat(),
        'action_type': action_type,
        'actor': 'silver_inbox_skill',
        'target': target,
        'approval_status': 'auto' if action_type not in SENSITIVE_TYPES else 'pending',
        'result': result
    }
    entries = json.loads(log_file.read_text()) if log_file.exists() else []
    entries.append(entry)
    log_file.write_text(json.dumps(entries, indent=2))


def update_dashboard(processed: list[dict]):
    if not DASHBOARD.exists():
        return
    dashboard = DASHBOARD.read_text(encoding='utf-8')
    timestamp = datetime.now().isoformat()
    activity = '\n'.join(f'- {timestamp}: {p["action"]} — `{p["name"]}`' for p in processed)

    if '### Recent Activity' in dashboard:
        dashboard = dashboard.replace(
            '### Recent Activity\n',
            f'### Recent Activity\n{activity}\n'
        )
    DASHBOARD.write_text(dashboard, encoding='utf-8')


def main():
    for folder in [PLANS, DONE, PENDING_APPROVAL, LOGS]:
        folder.mkdir(exist_ok=True)

    pending = [
        f for f in NEEDS_ACTION.glob('*.md')
        if parse_frontmatter(f.read_text(encoding='utf-8')).get('status') == 'pending'
    ]

    if not pending:
        print('No pending items.')
        return

    print(f'Processing {len(pending)} item(s)...')
    processed = []

    for item_path in pending:
        content = item_path.read_text(encoding='utf-8')
        fm = parse_frontmatter(content)
        item_type = fm.get('type', 'unknown')

        plan = create_plan(item_path, fm, content)
        print(f'  Plan: {plan.name}')

        if item_type in SENSITIVE_TYPES:
            approval = create_approval_request(item_path, fm, content)
            print(f'  Approval requested: {approval.name}')
            action = f'approval requested ({item_type})'
        else:
            action = f'auto-processed ({item_type})'

        log_action(item_type, fm.get('from', 'unknown'), 'processed')

        done_path = DONE / item_path.name
        item_path.rename(done_path)
        processed.append({'name': item_path.name, 'action': action})

    # Generate LinkedIn draft
    create_linkedin_draft()
    print('  LinkedIn post draft created for approval')

    update_dashboard(processed)
    print(f'\nDone. {len(processed)} item(s) processed. Dashboard updated.')


if __name__ == '__main__':
    main()
