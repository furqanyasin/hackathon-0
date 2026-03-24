"""
Process Inbox Skill — reads Needs_Action/, creates Plans, updates Dashboard.
Invoked by Claude Code as an Agent Skill via /process-inbox
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

VAULT = Path(os.getenv('VAULT_PATH', r'D:\PIAIC\hackathon-0\obsidian_vault'))
NEEDS_ACTION = VAULT / 'Needs_Action'
PLANS = VAULT / 'Plans'
DONE = VAULT / 'Done'
PENDING_APPROVAL = VAULT / 'Pending_Approval'
DASHBOARD = VAULT / 'Dashboard.md'

# Actions that always require human approval
SENSITIVE_TYPES = ['email', 'payment', 'social_post']


def get_frontmatter_value(content: str, key: str) -> str:
    for line in content.splitlines():
        if line.startswith(f'{key}:'):
            return line.split(':', 1)[1].strip()
    return ''


def create_plan(item_path: Path, content: str) -> Path:
    item_type = get_frontmatter_value(content, 'type')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plan_path = PLANS / f'PLAN_{timestamp}_{item_path.stem}.md'

    requires_approval = item_type in SENSITIVE_TYPES
    approval_note = '⚠️ REQUIRES HUMAN APPROVAL — see /Pending_Approval/' if requires_approval else 'Auto-processing'

    plan_path.write_text(f"""---
created: {datetime.now().isoformat()}
source: {item_path.name}
type: {item_type}
status: {'pending_approval' if requires_approval else 'in_progress'}
---

## Objective

Process item: `{item_path.name}`

## Steps

- [x] Read and understood item
- [ ] Determine required action
- [ ] {'Create approval request' if requires_approval else 'Execute action'}
- [ ] Update Dashboard.md
- [ ] Move to /Done

## Notes

{approval_note}

## Source Content Summary

{content[:500]}{'...' if len(content) > 500 else ''}
""", encoding='utf-8')
    return plan_path


def create_approval_request(item_path: Path, content: str) -> Path:
    item_type = get_frontmatter_value(content, 'type')
    approval_path = PENDING_APPROVAL / f'APPROVAL_{item_path.stem}.md'
    approval_path.write_text(f"""---
type: approval_request
action: {item_type}
source: {item_path.name}
created: {datetime.now().isoformat()}
status: pending
---

## Action Required

Review this item and decide:

**To Approve:** Move this file to `/Approved/`
**To Reject:** Move this file to `/Rejected/`

## Item Content

{content}
""", encoding='utf-8')
    return approval_path


def update_dashboard(processed: list[dict]):
    if not DASHBOARD.exists():
        return

    dashboard = DASHBOARD.read_text(encoding='utf-8')
    timestamp = datetime.now().isoformat()

    activity_lines = '\n'.join(
        f'- {timestamp}: Processed `{item["name"]}` → {item["action"]}'
        for item in processed
    )

    # Append to Recent Activity section
    dashboard = dashboard.replace(
        '- 2026-03-24: System initialized',
        f'{activity_lines}\n- 2026-03-24: System initialized'
    )
    DASHBOARD.write_text(dashboard, encoding='utf-8')


def main():
    PLANS.mkdir(exist_ok=True)
    DONE.mkdir(exist_ok=True)
    PENDING_APPROVAL.mkdir(exist_ok=True)

    pending = [f for f in NEEDS_ACTION.glob('*.md')
               if get_frontmatter_value(f.read_text(encoding='utf-8'), 'status') == 'pending']

    if not pending:
        print('No pending items in Needs_Action/')
        return

    print(f'Found {len(pending)} pending item(s)')
    processed = []

    for item_path in pending:
        content = item_path.read_text(encoding='utf-8')
        item_type = get_frontmatter_value(content, 'type')
        print(f'Processing: {item_path.name} (type: {item_type})')

        plan_path = create_plan(item_path, content)
        print(f'  Created plan: {plan_path.name}')

        if item_type in SENSITIVE_TYPES:
            approval_path = create_approval_request(item_path, content)
            print(f'  Requires approval: {approval_path.name}')
            action = f'plan created, approval requested'
        else:
            action = f'plan created, auto-processing'

        # Move to Done
        done_path = DONE / item_path.name
        item_path.rename(done_path)
        print(f'  Moved to Done/')

        processed.append({'name': item_path.name, 'action': action})

    update_dashboard(processed)
    print(f'\nDone. Processed {len(processed)} item(s). Dashboard updated.')


if __name__ == '__main__':
    main()
