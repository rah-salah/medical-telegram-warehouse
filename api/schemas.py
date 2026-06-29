from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class ChannelActivity(BaseModel):
    channel: str
    total_messages: int
    messages_with_images: int
    avg_views: float
    first_message: str
    last_message: str


class TopProduct(BaseModel):
    keyword: str
    mention_count: int


class MessageResult(BaseModel):
    message_id: int
    channel: str
    date: str
    text: str


class DailyTrend(BaseModel):
    date: str
    message_count: int


class ImageDetection(BaseModel):
    detected_class: str
    count: int
    avg_confidence: float
    image_category: str


class VisualContentReport(BaseModel):
    channel: str
    total_images: int
    top_detected_class: str
    detection_count: int
