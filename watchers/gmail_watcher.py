"""
Gmail Watcher - monitors unread/important Gmail and creates action files.

Setup:
1. Google Cloud Console -> New project -> Enable Gmail API
2. Create OAuth2 credentials -> Download as credentials.json -> place in D:/PIAIC/hackathon-0/
3. First run opens browser for auth, then saves token.json automatically

Run: uv run python watchers/gmail_watcher.py
"""
import os
import sys
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Add watchers/ to path so base_watcher import works
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailWatcher(BaseWatcher):
    def __init__(self):
        vault_path = os.getenv('VAULT_PATH', r'D:\PIAIC\hackathon-0\obsidian_vault')
        super().__init__(vault_path, check_interval=120)

        creds_path = Path(os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json'))
        token_path = Path(os.getenv('GMAIL_TOKEN_PATH', 'token.json'))

        self.service = self._authenticate(creds_path, token_path)
        self.processed_ids: set = set()

    def _authenticate(self, creds_path: Path, token_path: Path):
        creds = None
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
                creds = flow.run_local_server(port=0)
            token_path.write_text(creds.to_json())
        return build('gmail', 'v1', credentials=creds)

    def check_for_updates(self) -> list:
        results = self.service.users().messages().list(
            userId='me',
            q='is:unread is:important newer_than:1d',
            maxResults=10
        ).execute()
        messages = results.get('messages', [])
        return [m for m in messages if m['id'] not in self.processed_ids]

    def create_action_file(self, message: dict) -> Path:
        msg = self.service.users().messages().get(
            userId='me', id=message['id']
        ).execute()

        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        filepath = self.needs_action / f'EMAIL_{message["id"]}.md'
        filepath.write_text(f"""---
type: email
from: {headers.get('From', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: high
status: pending
---

## Email Snippet

{msg.get('snippet', '')}

## Suggested Actions

- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
""", encoding='utf-8')
        self.processed_ids.add(message['id'])
        return filepath


if __name__ == '__main__':
    GmailWatcher().run()
