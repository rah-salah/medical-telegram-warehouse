from fastapi import FastAPI, Query, HTTPException
from sqlalchemy import text
from api.database import engine
from api import schemas
from typing import List
import os

app = FastAPI(title="Medical Telegram Analytics API", version="1.0.0")


@app.get("/")
def root():
    return {"message": "Medical Telegram Analytics API", "version": "1.0.0", "status": "running"}


@app.get("/api/reports/top-products", response_model=List[schemas.TopProduct])
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


@app.get("/api/channels/{channel_name}/activity", response_model=schemas.ChannelActivity)
def channel_activity(channel_name: str):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT channel_name, total_messages, messages_with_images, "                 "ROUND(avg_views::numeric,1), first_message_date, last_message_date "                 "FROM dim_channels WHERE LOWER(channel_name) = LOWER(:ch)"),
            {"ch": channel_name}
        ).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail=f"Channel {channel_name} not found")
        return {"channel": result[0], "total_messages": result[1],
                "messages_with_images": result[2], "avg_views": float(result[3]),
                "first_message": str(result[4]), "last_message": str(result[5])}


@app.get("/api/search/messages", response_model=List[schemas.MessageResult])
def search_messages(
    q: str = Query(..., min_length=2, description="Search term"),
    limit: int = Query(default=10, le=50)
):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT message_id, channel_name, message_date, message_text "                 "FROM fct_messages WHERE LOWER(message_text) LIKE :q "                 "ORDER BY message_date DESC LIMIT :limit"),
            {"q": f"%{q.lower()}%", "limit": limit}
        )
        rows = result.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="No messages found")
        return [{"message_id": r[0], "channel": r[1], "date": str(r[2]), "text": r[3][:300]} for r in rows]


@app.get("/api/reports/visual-content", response_model=List[schemas.VisualContentReport])
def visual_content_report():
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT f.channel_name, COUNT(*) as total_images, "            "d.detected_class, COUNT(d.id) as detection_count "            "FROM fct_image_detections d "            "JOIN fct_messages f ON d.message_id = f.message_id "            "GROUP BY f.channel_name, d.detected_class "            "ORDER BY f.channel_name, detection_count DESC"
        ))
        rows = result.fetchall()
        seen = {}
        for r in rows:
            if r[0] not in seen:
                seen[r[0]] = {"channel": r[0], "total_images": r[1],
                               "top_detected_class": r[2], "detection_count": r[3]}
        return list(seen.values())


@app.get("/api/trends/daily", response_model=List[schemas.DailyTrend])
def daily_trends():
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT message_day, COUNT(*) as message_count "            "FROM fct_messages GROUP BY message_day "            "ORDER BY message_day DESC LIMIT 30"
        ))
        return [{"date": str(r[0]), "message_count": r[1]} for r in result]


@app.get("/api/images/detections", response_model=List[schemas.ImageDetection])
def image_detections(limit: int = Query(default=10, le=50)):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT detected_class, COUNT(*) as count, "                 "ROUND(AVG(confidence)::numeric,2) as avg_confidence "                 "FROM fct_image_detections "                 "GROUP BY detected_class ORDER BY count DESC LIMIT :limit"),
            {"limit": limit}
        )
        rows = result.fetchall()
        def categorize(cls):
            if cls in ["bottle", "cup", "bowl"]: return "product_display"
            elif cls in ["person"]: return "lifestyle"
            elif cls in ["laptop", "book", "stop sign"]: return "promotional"
            else: return "other"
        return [{"detected_class": r[0], "count": r[1],
                 "avg_confidence": float(r[2]), "image_category": categorize(r[0])} for r in rows]
