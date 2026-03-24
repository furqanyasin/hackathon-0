"""
WhatsApp Watcher - monitors WhatsApp Web for urgent messages using Playwright.

First-time setup (run once to save session):
    uv run python watchers/whatsapp_watcher.py --setup

After setup, run normally:
    uv run python watchers/whatsapp_watcher.py
    pm2 start watchers/whatsapp_watcher.py --interpreter python --name whatsapp-watcher
"""
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'important', 'emergency']
SESSION_PATH = os.getenv('WHATSAPP_SESSION_PATH', r'D:\PIAIC\hackathon-0\session\whatsapp')


def setup_session():
    """One-time setup: open WhatsApp Web and save session after QR scan."""
    from playwright.sync_api import sync_playwright
    Path(SESSION_PATH).mkdir(parents=True, exist_ok=True)
    print('Opening WhatsApp Web — scan the QR code with your phone...')
    print('WhatsApp → Linked Devices → Link a Device')
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(SESSION_PATH, headless=False)
        page = browser.new_page()
        page.goto('https://web.whatsapp.com')
        print('\nWaiting for you to scan the QR code...')
        try:
            page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
            print('Logged in successfully! Session saved.')
        except Exception:
            print('Timeout — please try again')
        input('Press Enter to close browser and save session...')
        browser.close()


class WhatsAppWatcher(BaseWatcher):
    def __init__(self):
        vault_path = os.getenv('VAULT_PATH', r'D:\PIAIC\hackathon-0\obsidian_vault')
        super().__init__(vault_path, check_interval=30)
        self.session_path = SESSION_PATH
        self.processed_chats: set = set()

    def check_for_updates(self) -> list:
        from playwright.sync_api import sync_playwright
        messages = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    self.session_path, headless=True
                )
                page = browser.new_page()
                page.goto('https://web.whatsapp.com')
                page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                time.sleep(2)

                # Find unread chats
                unread_chats = page.query_selector_all('[data-testid="cell-frame-container"]')
                for chat in unread_chats:
                    try:
                        badge = chat.query_selector('[data-testid="icon-unread-count"]')
                        if not badge:
                            continue
                        name_el = chat.query_selector('[data-testid="cell-frame-title"]')
                        msg_el = chat.query_selector('[data-testid="last-msg-status"] + span, .x1iyjqo2')
                        name = name_el.inner_text() if name_el else 'Unknown'
                        text = msg_el.inner_text() if msg_el else ''

                        chat_id = f'{name}_{text[:20]}'
                        if chat_id in self.processed_chats:
                            continue

                        # Only process if contains keywords
                        if any(kw in text.lower() for kw in KEYWORDS):
                            messages.append({'name': name, 'text': text, 'id': chat_id})
                            self.processed_chats.add(chat_id)
                    except Exception:
                        continue
                browser.close()
        except Exception as e:
            self.logger.error(f'WhatsApp check failed: {e}')
        return messages

    def create_action_file(self, message: dict) -> Path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = self.needs_action / f'WHATSAPP_{timestamp}_{message["name"][:20]}.md'
        filepath.write_text(f"""---
type: whatsapp
from: {message['name']}
received: {datetime.now().isoformat()}
priority: high
status: pending
---

## Message

{message['text']}

## Suggested Actions

- [ ] Reply to sender
- [ ] Create task if action required
- [ ] Move to /Done when handled
""", encoding='utf-8')
        return filepath


if __name__ == '__main__':
    if '--setup' in sys.argv:
        setup_session()
    else:
        if not Path(SESSION_PATH).exists() or not any(Path(SESSION_PATH).iterdir()):
            print('No session found. Run with --setup first:')
            print('  uv run python watchers/whatsapp_watcher.py --setup')
            sys.exit(1)
        WhatsAppWatcher().run()
