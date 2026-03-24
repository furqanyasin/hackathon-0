"""
Email MCP Server - sends emails via Gmail API on behalf of Claude.

This MCP server exposes email actions that Claude can invoke.
It reads approved actions from /Approved/ and sends emails.

Run: uv run python mcps/email_mcp.py
"""
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EmailMCP')

VAULT_PATH = Path(os.getenv('VAULT_PATH', r'D:\PIAIC\hackathon-0\obsidian_vault'))
APPROVED = VAULT_PATH / 'Approved'
DONE = VAULT_PATH / 'Done'
LOGS = VAULT_PATH / 'Logs'
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'


def get_gmail_service():
    """Get authenticated Gmail service."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    token_path = Path(os.getenv('GMAIL_TOKEN_PATH', 'token.json'))
    creds = Credentials.from_authorized_user_file(str(token_path))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('gmail', 'v1', credentials=creds)


def send_email(to: str, subject: str, body: str) -> bool:
    """Send an email via Gmail API."""
    if DRY_RUN:
        logger.info(f'[DRY RUN] Would send email to {to}: {subject}')
        return True

    try:
        import base64
        from email.mime.text import MIMEText
        service = get_gmail_service()
        msg = MIMEText(body)
        msg['to'] = to
        msg['subject'] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(userId='me', body={'raw': raw}).execute()
        logger.info(f'Email sent to {to}')
        return True
    except Exception as e:
        logger.error(f'Failed to send email: {e}')
        return False


def log_action(action_type: str, target: str, result: str, approval_file: str):
    """Log every action to /Logs/YYYY-MM-DD.json"""
    LOGS.mkdir(exist_ok=True)
    log_file = LOGS / f'{datetime.now().strftime("%Y-%m-%d")}.json'
    entry = {
        'timestamp': datetime.now().isoformat(),
        'action_type': action_type,
        'actor': 'email_mcp',
        'target': target,
        'approval_status': 'approved',
        'approved_by': 'human',
        'approval_file': approval_file,
        'result': result
    }
    entries = []
    if log_file.exists():
        try:
            entries = json.loads(log_file.read_text())
        except Exception:
            entries = []
    entries.append(entry)
    log_file.write_text(json.dumps(entries, indent=2))


def process_approved_emails():
    """Check /Approved/ for email approval files and send them."""
    APPROVED.mkdir(exist_ok=True)
    DONE.mkdir(exist_ok=True)

    approved_files = list(APPROVED.glob('*.md'))
    if not approved_files:
        return

    for filepath in approved_files:
        content = filepath.read_text(encoding='utf-8')

        # Parse frontmatter
        lines = content.splitlines()
        fm = {}
        in_fm = False
        for line in lines:
            if line == '---':
                in_fm = not in_fm
                continue
            if in_fm and ':' in line:
                k, v = line.split(':', 1)
                fm[k.strip()] = v.strip()

        action = fm.get('action', '')
        if action not in ('send_email', 'email'):
            continue

        to = fm.get('to', '')
        subject = fm.get('subject', 'Message from AI Employee')

        # Extract body from markdown content after frontmatter
        body_start = content.find('---', content.find('---') + 3) + 3
        body = content[body_start:].strip()

        if not to:
            logger.warning(f'No recipient in {filepath.name}, skipping')
            continue

        logger.info(f'Sending approved email to {to}')
        success = send_email(to, subject, body)
        result = 'success' if success else 'failed'

        log_action('email_send', to, result, filepath.name)

        # Move to Done
        done_path = DONE / filepath.name
        filepath.rename(done_path)
        logger.info(f'Moved to Done: {filepath.name}')


def watch_approved_folder(interval: int = 15):
    """Continuously watch /Approved/ and process email actions."""
    import time
    logger.info(f'Email MCP watching /Approved/ every {interval}s')
    logger.info(f'DRY_RUN={DRY_RUN}')
    while True:
        try:
            process_approved_emails()
        except Exception as e:
            logger.error(f'Error: {e}')
        time.sleep(interval)


if __name__ == '__main__':
    watch_approved_folder()
