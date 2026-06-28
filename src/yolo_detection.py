import os
import json
import logging
import psycopg2
from dotenv import load_dotenv
from ultralytics import YOLO

load_dotenv()
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/yolo.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MODEL_NAME = "yolov8n.pt"
IMAGES_DIR = "data/raw/images"
CONFIDENCE = 0.25


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        dbname=os.getenv("POSTGRES_DB", "medical_warehouse"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres123")
    )


def create_detections_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fct_image_detections (
            id SERIAL PRIMARY KEY,
            message_id INTEGER,
            channel_name VARCHAR(100),
            image_path TEXT,
            detected_class VARCHAR(100),
            confidence FLOAT,
            bbox_x1 FLOAT,
            bbox_y1 FLOAT,
            bbox_x2 FLOAT,
            bbox_y2 FLOAT,
            detected_at TIMESTAMP DEFAULT NOW()
        )
    """)


def run_yolo_on_images():
    print(f"Loading YOLO model: {MODEL_NAME}")
    model = YOLO(MODEL_NAME)
    conn = get_connection()
    cur = conn.cursor()
    create_detections_table(cur)
    conn.commit()

    total_detections = 0
    total_images = 0

    for channel in os.listdir(IMAGES_DIR):
        channel_dir = os.path.join(IMAGES_DIR, channel)
        if not os.path.isdir(channel_dir):
            continue
        images = [f for f in os.listdir(channel_dir) if f.endswith(".jpg")]
        print(f"Processing {len(images)} images from {channel}...")

        for img_file in images:
            img_path = os.path.join(channel_dir, img_file)
            message_id = int(img_file.replace(".jpg", ""))
            try:
                results = model(img_path, conf=CONFIDENCE, verbose=False)
                for result in results:
                    for box in result.boxes:
                        cls_name = model.names[int(box.cls[0])]
                        conf = float(box.conf[0])
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        cur.execute("""
                            INSERT INTO fct_image_detections
                            (message_id, channel_name, image_path, detected_class,
                             confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """, (message_id, channel, img_path, cls_name,
                               conf, x1, y1, x2, y2))
                        total_detections += 1
                total_images += 1
            except Exception as e:
                logger.error(f"Failed to process {img_path}: {e}")
                continue

    conn.commit()
    conn.close()
    print(f"Done! Processed {total_images} images, found {total_detections} detections")
    logger.info(f"Processed {total_images} images, {total_detections} detections")


if __name__ == "__main__":
    run_yolo_on_images()
