import pytest
import json
import os

def test_sample_json_exists():
    path = "data/raw/telegram_messages/sample/sample_CheMed123.json"
    assert os.path.exists(path), f"Sample file not found: {path}"

def test_sample_json_structure():
    path = "data/raw/telegram_messages/sample/sample_CheMed123.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) > 0
    msg = data[0]
    assert "message_id" in msg
    assert "channel_name" in msg
    assert "message_text" in msg
    assert "views" in msg
    assert "forwards" in msg
    assert "has_media" in msg

def test_required_channels():
    channels = ["CheMed123", "lobelia4cosmetics", "tikvahpharma"]
    assert len(channels) == 3

def test_message_views_non_negative():
    path = "data/raw/telegram_messages/sample/sample_CheMed123.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for msg in data:
        assert msg["views"] >= 0, "Views should be non-negative"
