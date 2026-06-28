from fastapi import FastAPI, Query
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres123")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "medical_warehouse")
DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DB_URL)
app = FastAPI(title="Medical Telegram Analytics API", version="1.0.0")


@app.get("/")
def root():
    return {"message": "Medical Telegram Analytics API", "version": "1.0.0", "status": "running"}


@app.get("/api/channels/activity")
def channel_activity():
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT channel_name, total_messages, messages_with_images, "            "ROUND(avg_views::numeric, 1) as avg_views, "            "first_message_date, last_message_date "            "FROM dim_channels ORDER BY total_messages DESC"
        ))
        return [
            {"channel": r[0], "total_messages": r[1],
             "messages_with_images": r[2], "avg_views": float(r[3]),
             "first_message": str(r[4]), "last_message": str(r[5])}
            for r in result
        ]


@app.get("/api/top-products")
def top_products(limit: int = Query(default=10, le=50)):
    keywords = ["cream", "lotion", "tablet", "capsule", "syrup",
                "injection", "vitamin", "gel", "soap", "oil",
                "mask", "serum", "medicine", "drug", "pill",
                "skin", "hair", "body", "face", "health"]
    results = []
    with engine.connect() as conn:
        for kw in keywords:
            row = conn.execute(
                text("SELECT COUNT(*) FROM fct_messages WHERE LOWER(message_text) LIKE :kw"),
                {"kw": f"%{kw}%"}
            ).fetchone()
            if row[0] > 0:
                results.append({"keyword": kw, "mention_count": row[0]})
    results.sort(key=lambda x: x["mention_count"], reverse=True)
    return results[:limit]


@app.get("/api/messages/search")
def search_messages(
    q: str = Query(..., min_length=2, description="Search term"),
    limit: int = Query(default=10, le=50)
):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT message_id, channel_name, message_date, message_text "                 "FROM fct_messages WHERE LOWER(message_text) LIKE :q "                 "ORDER BY message_date DESC LIMIT :limit"),
            {"q": f"%{q.lower()}%", "limit": limit}
        )
        return [
            {"message_id": r[0], "channel": r[1],
             "date": str(r[2]), "text": r[3][:300]}
            for r in result
        ]


@app.get("/api/trends/daily")
def daily_trends():
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT message_day, COUNT(*) as message_count "            "FROM fct_messages GROUP BY message_day "            "ORDER BY message_day DESC LIMIT 30"
        ))
        return [{"date": str(r[0]), "message_count": r[1]} for r in result]


@app.get("/api/images/detections")
def image_detections(limit: int = Query(default=10, le=50)):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT detected_class, COUNT(*) as count, "                 "ROUND(AVG(confidence)::numeric, 2) as avg_confidence "                 "FROM fct_image_detections "                 "GROUP BY detected_class ORDER BY count DESC LIMIT :limit"),
            {"limit": limit}
        )
        return [
            {"class": r[0], "count": r[1], "avg_confidence": float(r[2])}
            for r in result
        ]
