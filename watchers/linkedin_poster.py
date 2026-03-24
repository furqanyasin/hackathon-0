"""
LinkedIn Auto-Poster - generates and posts business updates to LinkedIn.
Uses LinkedIn API v2 (OAuth2).

Setup:
1. Go to linkedin.com/developers -> Create app
2. Add 'Share on LinkedIn' and 'OpenID Connect' products
3. Get Access Token from OAuth 2.0 tools
4. Add LINKEDIN_ACCESS_TOKEN to .env

Run: uv run python watchers/linkedin_poster.py
"""
import os
import sys
import json
import logging
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LinkedInPoster')

VAULT_PATH = Path(os.getenv('VAULT_PATH', r'D:\PIAIC\hackathon-0\obsidian_vault'))
PENDING_APPROVAL = VAULT_PATH / 'Pending_Approval'
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'
ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN', '')


def get_profile_urn() -> str:
    """Get the LinkedIn user URN needed for posting."""
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
    resp = requests.get('https://api.linkedin.com/v2/userinfo', headers=headers)
    resp.raise_for_status()
    sub = resp.json().get('sub', '')
    return f'urn:li:person:{sub}'


def create_approval_request(post_content: str, source: str = 'scheduled'):
    """Write post to Pending_Approval instead of posting directly."""
    PENDING_APPROVAL.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    approval_path = PENDING_APPROVAL / f'LINKEDIN_POST_{timestamp}.md'
    approval_path.write_text(f"""---
type: social_post
platform: linkedin
action: post
created: {datetime.now().isoformat()}
source: {source}
status: pending
---

## Post Content

{post_content}

## To Approve
Move this file to `/Approved/`

## To Reject
Move this file to `/Rejected/`
""", encoding='utf-8')
    logger.info(f'LinkedIn approval request created: {approval_path.name}')
    return approval_path


def post_to_linkedin(content: str) -> bool:
    """Actually post to LinkedIn (only called after human approval)."""
    if DRY_RUN:
        logger.info(f'[DRY RUN] Would post to LinkedIn: {content[:100]}...')
        return True

    if not ACCESS_TOKEN:
        logger.error('LINKEDIN_ACCESS_TOKEN not set in .env')
        return False

    try:
        urn = get_profile_urn()
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        payload = {
            'author': urn,
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {'text': content},
                    'shareMediaCategory': 'NONE'
                }
            },
            'visibility': {'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'}
        }
        resp = requests.post(
            'https://api.linkedin.com/v2/ugcPosts',
            headers=headers,
            json=payload
        )
        resp.raise_for_status()
        logger.info(f'Posted to LinkedIn: {resp.status_code}')
        return True
    except Exception as e:
        logger.error(f'LinkedIn post failed: {e}')
        return False


def generate_post_from_goals() -> str:
    """Generate a LinkedIn post based on Business_Goals.md."""
    goals_path = VAULT_PATH / 'Business_Goals.md'
    goals = goals_path.read_text(encoding='utf-8') if goals_path.exists() else ''

    # Claude will generate this via the Agent Skill
    # For now return a template
    return f"""Building my Personal AI Employee with Claude Code!

Key capabilities:
- 24/7 email and WhatsApp monitoring
- Autonomous task planning with human-in-the-loop safety
- Local-first architecture with Obsidian as the dashboard

The future of work is AI-augmented. Excited to share progress soon!

#AI #Automation #ClaudeCode #PersonalProductivity #PIAIC
"""


if __name__ == '__main__':
    post = generate_post_from_goals()
    if '--post-direct' in sys.argv:
        # Called after approval — post directly
        post_to_linkedin(post)
    else:
        # Default: create approval request
        create_approval_request(post, source='manual')
        print('Approval request created in /Pending_Approval/')
        print('Move the file to /Approved/ to post to LinkedIn')
