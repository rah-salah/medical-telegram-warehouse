import psycopg2
import json
import os
import logging
from dotenv import load_dotenv

load_dotenv()
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/loader.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def get_connection():
    try:
        return psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", 5432)),
            dbname=os.getenv("POSTGRES_DB", "medical_warehouse"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres123")
        )
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        raise


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
    if not os.path.exists(folder):
        raise FileNotFoundError(f"Data folder not found: {folder}")
    conn = get_connection()
    cur = conn.cursor()
    create_table(cur)
    total = 0
    for filename in os.listdir(folder):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(folder, filename)
        try:
            with open(filepath, encoding="utf-8") as f:
                messages = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Failed to parse {filepath}: {e}")
            continue
        for msg in messages:
            try:
                cur.execute("""
                    INSERT INTO raw_telegram_messages
                    (message_id, channel_name, message_date, message_text,
                     has_media, image_path, views, forwards)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT DO NOTHING
                """, (
                    msg.get("message_id"), msg.get("channel_name"),
                    msg.get("message_date"), msg.get("message_text"),
                    msg.get("has_media"), msg.get("image_path"),
                    msg.get("views", 0), msg.get("forwards", 0)
                ))
                total += 1
            except psycopg2.Error as e:
                logger.error(f"Insert failed for message {msg.get(chr(109)+chr(101)+chr(115)+chr(115)+chr(97)+chr(103)+chr(101)+chr(95)+chr(105)+chr(100))}: {e}")
                conn.rollback()
    conn.commit()
    logger.info(f"Loaded {total} messages")
    print(f"Loaded {total} messages into PostgreSQL")
    conn.close()


if __name__ == "__main__":
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    load_json_to_db(f"data/raw/telegram_messages/{today}")
