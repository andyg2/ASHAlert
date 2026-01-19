"""
Daily README.md monitor for awesome-selfhosted.
"""

import os
import re
import asyncio
import difflib
import logging
import requests
from pathlib import Path
from typing import Optional, Dict
from dotenv import load_dotenv
from telegram import Bot

# -----------------------------------------------------------------------------
# Setup & Environment
# -----------------------------------------------------------------------------
load_dotenv()

# Logging setup to help you see what's happening
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

OWNER = os.environ.get("GITHUB_OWNER", "awesome-selfhosted")
REPO = os.environ.get("GITHUB_REPO", "awesome-selfhosted")
BRANCH = os.environ.get("GITHUB_BRANCH", "master")

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# Ensure Chat ID is an integer
CHAT_ID = int(os.environ.get("TELEGRAM_CHAT_ID", 0))

STATE_DIR = Path(os.environ.get("STATE_DIR", "./state"))
STATE_DIR.mkdir(parents=True, exist_ok=True)
README_PATH = STATE_DIR / "README.md"

RAW_URL = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}/README.md"

# Initialize Bot
telegram = Bot(token=TOKEN)

# -----------------------------------------------------------------------------
# Core Logic
# -----------------------------------------------------------------------------

def fetch_readme() -> str:
    resp = requests.get(RAW_URL, timeout=30)
    resp.raise_for_status()
    return resp.text

def load_previous() -> str:
    if README_PATH.exists():
        return README_PATH.read_text(encoding="utf-8")
    return ""

def save_current(text: str):
    README_PATH.write_text(text, encoding="utf-8")

def get_added_lines(old: str, new: str):
    diff = difflib.unified_diff(
        old.splitlines(),
        new.splitlines(),
        lineterm=""
    )
    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            yield line[1:]

# -----------------------------------------------------------------------------
# Markdown Parsing
# -----------------------------------------------------------------------------

def extract_link(text: str, label: str) -> Optional[str]:
    match = re.search(rf"\[{label}\]\(([^)]+)\)", text)
    return match.group(1) if match else None

def parse_markdown_entry(line: str) -> Optional[Dict]:
    line = line.strip()
    if not line.startswith("-"):
        return None

    # Standard Awesome-List pattern: - [Name](URL) - Description
    pattern = r"-\s*\[([^\]]+)\]\(([^)]+)\)\s*-\s*(.+)"
    match = re.match(pattern, line)
    if not match:
        return None

    name, url, rest = match.groups()
    description = re.split(r"\s*\(", rest)[0].strip()

    return {
        "name": name,
        "url": url,
        "description": description,
        "demo_url": extract_link(rest, "Demo"),
        "source_url": extract_link(rest, "Source Code"),
        "license": (re.findall(r"`([^`]+)`", rest) + [None])[0],
        "deployment": (re.findall(r"`([^`]+)`", rest) + [None, None])[1],
    }

# -----------------------------------------------------------------------------
# Telegram (Async)
# -----------------------------------------------------------------------------

async def send_telegram(project: Dict):
    msg = (
        "🆕 *New Software Added*\n\n"
        f"*{project['name']}*\n"
        f"🔗 {project['url']}\n\n"
        f"📝 {project['description']}"
    )

    if project.get("demo_url"):
        msg += f"\n\n🎮 Demo: {project['demo_url']}"
    if project.get("source_url"):
        msg += f"\n💻 Source: {project['source_url']}"
    if project.get("license"):
        msg += f"\n📜 License: `{project['license']}`"
    if project.get("deployment"):
        msg += f"\n🚀 Deployment: `{project['deployment']}`"

    try:
        # NOTE: We MUST await this call in v20+
        await telegram.send_message(
            chat_id=CHAT_ID,
            text=msg,
            parse_mode="Markdown",
            disable_web_page_preview=False
        )
    except Exception as e:
        logger.error(f"Failed to send telegram message: {e}")

# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------

async def main():
    if not TOKEN or not CHAT_ID:
        logger.error("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set in .env")
        return

    logger.info("📥 Fetching latest README.md...")
    try:
        current_content = fetch_readme()
    except Exception as e:
        logger.error(f"Failed to fetch README: {e}")
        return

    previous_content = load_previous()

    # If there's no previous file, we don't want to send 1000 messages.
    # We just save the current file and wait for the next update.
    if not previous_content:
        logger.info("💾 First run detected. Saving state without sending notifications.")
        save_current(current_content)
        return

    added_lines = list(get_added_lines(previous_content, current_content))
    logger.info(f"🔍 Lines added: {len(added_lines)}")

    count = 0
    for line in added_lines:
        project = parse_markdown_entry(line)
        if project:
            await send_telegram(project)
            logger.info(f"✅ Notified: {project['name']}")
            count += 1
            # Brief sleep to avoid hitting Telegram rate limits if many items added
            await asyncio.sleep(1)

    save_current(current_content)
    logger.info(f"🏁 Done. Sent {count} notifications.")

if __name__ == "__main__":
    # Start the async event loop
    asyncio.run(main())
