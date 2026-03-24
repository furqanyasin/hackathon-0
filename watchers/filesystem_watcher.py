"""
Filesystem Watcher - monitors a dedicated DROP folder for new files.

Watches: obsidian_vault/Inbox/  (NOT Needs_Action - that would cause infinite loops)
Writes:  obsidian_vault/Needs_Action/

Run: uv run python watchers/filesystem_watcher.py
Drop any .md or .txt file into obsidian_vault/Inbox/ to trigger processing.
"""
import os
import time
import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FileSystemWatcher')

VAULT_PATH = Path(os.getenv('VAULT_PATH', r'D:\PIAIC\hackathon-0\obsidian_vault'))
DROP_FOLDER = VAULT_PATH / 'Inbox'        # watch here
NEEDS_ACTION = VAULT_PATH / 'Needs_Action'  # write here


class DropFolderHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or str(event.src_path).endswith('.tmp'):
            return

        file_path = Path(event.src_path)
        if file_path.suffix not in ['.md', '.txt']:
            return

        time.sleep(0.5)  # let file finish writing
        logger.info(f'New file dropped: {file_path.name}')
        self._create_action_file(file_path)

    def _create_action_file(self, file_path: Path):
        try:
            content = file_path.read_text(encoding='utf-8')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            action_path = NEEDS_ACTION / f'FILE_{timestamp}_{file_path.stem}.md'
            action_path.write_text(f"""---
type: file_drop
original_name: {file_path.name}
received: {datetime.now().isoformat()}
status: pending
---

## File Content

{content}

## Suggested Actions

- [ ] Review and process
- [ ] Move to /Done when complete
""", encoding='utf-8')
            logger.info(f'Action file created: {action_path.name}')
        except Exception as e:
            logger.error(f'Error processing {file_path.name}: {e}')


def main():
    DROP_FOLDER.mkdir(parents=True, exist_ok=True)
    NEEDS_ACTION.mkdir(parents=True, exist_ok=True)

    logger.info(f'Watching DROP folder: {DROP_FOLDER}')
    logger.info(f'Writing action files to: {NEEDS_ACTION}')
    logger.info('Drop .md or .txt files into Inbox/ to trigger Claude processing')

    observer = Observer()
    observer.schedule(DropFolderHandler(), str(DROP_FOLDER), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()
