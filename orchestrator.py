"""
Orchestrator - the master process that coordinates the AI Employee.

Watches /Needs_Action/ and triggers Claude Code to process items,
creating Plan.md files and routing sensitive actions to /Pending_Approval/.

Run: uv run python orchestrator.py
pm2 start orchestrator.py --interpreter python --name orchestrator
"""
import os
import subprocess
import time
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Orchestrator')

VAULT_PATH = Path(os.getenv('VAULT_PATH', r'D:\PIAIC\hackathon-0\obsidian_vault'))
NEEDS_ACTION = VAULT_PATH / 'Needs_Action'
PLANS = VAULT_PATH / 'Plans'
PENDING_APPROVAL = VAULT_PATH / 'Pending_Approval'
DONE = VAULT_PATH / 'Done'
CHECK_INTERVAL = 30  # seconds


def get_frontmatter_value(content: str, key: str) -> str:
    for line in content.splitlines():
        if line.startswith(f'{key}:'):
            return line.split(':', 1)[1].strip()
    return ''


def get_pending_items() -> list[Path]:
    return [
        f for f in NEEDS_ACTION.glob('*.md')
        if get_frontmatter_value(f.read_text(encoding='utf-8'), 'status') == 'pending'
    ]


def trigger_claude(item_path: Path):
    """Trigger Claude Code to process a specific item and create a Plan."""
    content = item_path.read_text(encoding='utf-8')
    item_type = get_frontmatter_value(content, 'type')
    sender = get_frontmatter_value(content, 'from')

    prompt = f"""Read the file at obsidian_vault/Needs_Action/{item_path.name}

Based on Company_Handbook.md rules:
1. Create a PLAN file in obsidian_vault/Plans/ named PLAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{item_path.stem}.md
   - Include checkbox steps to handle this {item_type} item
   - Flag any steps requiring external action (email, payment, post) as needing approval

2. If action requires sending email/message/payment:
   - Create an approval file in obsidian_vault/Pending_Approval/
   - Do NOT send anything directly

3. Update obsidian_vault/Dashboard.md with this new activity

4. Move obsidian_vault/Needs_Action/{item_path.name} to obsidian_vault/Done/

Item type: {item_type}
From: {sender}
"""
    try:
        logger.info(f'Triggering Claude for: {item_path.name}')
        result = subprocess.run(
            ['claude', '--print', prompt],
            cwd=str(VAULT_PATH.parent),
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            logger.info(f'Claude processed: {item_path.name}')
        else:
            logger.error(f'Claude error: {result.stderr[:200]}')
    except subprocess.TimeoutExpired:
        logger.error(f'Claude timed out for: {item_path.name}')
    except FileNotFoundError:
        logger.error('Claude Code not found in PATH. Make sure claude is installed.')


def run():
    logger.info('Orchestrator started')
    logger.info(f'Watching: {NEEDS_ACTION}')
    logger.info(f'Check interval: {CHECK_INTERVAL}s')

    while True:
        pending = get_pending_items()
        if pending:
            logger.info(f'Found {len(pending)} pending item(s)')
            for item in pending:
                trigger_claude(item)
                time.sleep(5)  # brief pause between items
        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    run()
