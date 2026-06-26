import asyncio
import json
import os
import logging
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")

CHANNELS = [
    "CheMed123",
    "lobelia4cosmetics",
    "tikvahpharma",
]

logging.basicConfig(
    filename="logs/scraper.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


async def scrape_channel(client, channel_name, limit=200):
    logger.info(f"Scraping {channel_name}")
    print(f"Scraping {channel_name}...")
    messages = []
    try:
        entity = await client.get_entity(channel_name)
        async for msg in client.iter_messages(entity, limit=limit):
            has_media = msg.media is not None
            image_path = None
            if isinstance(msg.media, MessageMediaPhoto):
                folder = f"data/raw/images/{channel_name}"
                os.makedirs(folder, exist_ok=True)
                image_path = f"{folder}/{msg.id}.jpg"
                await client.download_media(msg.media, file=image_path)
            messages.append({
                "message_id": msg.id,
                "channel_name": channel_name,
                "message_date": str(msg.date),
                "message_text": msg.text or "",
                "has_media": has_media,
                "image_path": image_path,
                "views": msg.views or 0,
                "forwards": msg.forwards or 0,
            })
    except Exception as e:
        logger.error(f"Error scraping {channel_name}: {e}")
        print(f"Error: {e}")
    return messages


async def main():
    os.makedirs("logs", exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    async with TelegramClient("session", API_ID, API_HASH) as client:
        await client.start(phone=PHONE)
        for channel in CHANNELS:
            messages = await scrape_channel(client, channel)
            if messages:
                folder = f"data/raw/telegram_messages/{today}"
                os.makedirs(folder, exist_ok=True)
                path = f"{folder}/{channel}.json"
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(messages, f, ensure_ascii=False, indent=2)
                print(f"Saved {len(messages)} messages from {channel} to {path}")
                logger.info(f"Saved {len(messages)} messages from {channel}")


if __name__ == "__main__":
    asyncio.run(main())
