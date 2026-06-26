import psycopg2
import json
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(filename="logs/loader.log", level=logging.INFO)
logger = logging.getLogger(__name__)

def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5432),
        dbname=os.getenv("POSTGRES_DB", "medical_warehouse"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres123")
    )

def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw_telegram_messages (
            message_id INTEGER,
            channel_name VARCHAR(100),
            message_date TIMESTAMP,
            message_text TEXT,
            has_media BOOLEAN,
            image_path TEXT,
            views INTEGER,
            forwards INTEGER,
            scraped_at TIMESTAMP DEFAULT NOW()
        )
    """)

def load_json_to_db(folder):
    conn = get_connection()
    cur = conn.cursor()
    create_table(cur)
    total = 0
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            with open(os.path.join(folder, filename), encoding="utf-8") as f:
                messages = json.load(f)
            for msg in messages:
                cur.execute("""
                    INSERT INTO raw_telegram_messages
                    (message_id, channel_name, message_date, message_text, has_media, image_path, views, forwards)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    msg["message_id"], msg["channel_name"], msg["message_date"],
                    msg["message_text"], msg["has_media"], msg["image_path"],
                    msg["views"], msg["forwards"]
                ))
                total += 1
    conn.commit()
    logger.info(f"Loaded {total} messages")
    print(f"Loaded {total} messages into PostgreSQL")
    conn.close()

if __name__ == "__main__":
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    folder = f"data/raw/telegram_messages/{today}"
    load_json_to_db(folder)
