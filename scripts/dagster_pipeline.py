import dagster as dg
import subprocess
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


@dg.asset(description="Scrape messages and images from Telegram channels")
def telegram_raw_data(context):
    context.log.info("Starting Telegram scraping...")
    result = subprocess.run(
        [sys.executable, "src/scraper.py"],
        capture_output=True, text=True, cwd=os.getcwd()
    )
    if result.returncode != 0:
        raise Exception(f"Scraper failed: {result.stderr}")
    context.log.info(result.stdout)
    today = datetime.now().strftime("%Y-%m-%d")
    return dg.MaterializeResult(
        metadata={"date": today, "output": result.stdout[:500]}
    )


@dg.asset(
    description="Load raw JSON files into PostgreSQL",
    deps=[telegram_raw_data]
)
def postgres_raw_data(context):
    context.log.info("Loading data into PostgreSQL...")
    result = subprocess.run(
        [sys.executable, "src/loader.py"],
        capture_output=True, text=True, cwd=os.getcwd()
    )
    if result.returncode != 0:
        raise Exception(f"Loader failed: {result.stderr}")
    context.log.info(result.stdout)
    return dg.MaterializeResult(
        metadata={"output": result.stdout[:500]}
    )


@dg.asset(
    description="Run dbt models to build star schema",
    deps=[postgres_raw_data]
)
def dbt_models(context):
    context.log.info("Running dbt models...")
    result = subprocess.run(
        ["dbt", "run", "--project-dir", "medical_warehouse",
         "--profiles-dir", "medical_warehouse"],
        capture_output=True, text=True, cwd=os.getcwd()
    )
    context.log.info(result.stdout)
    if result.returncode != 0:
        raise Exception(f"dbt run failed: {result.stderr}")
    test_result = subprocess.run(
        ["dbt", "test", "--project-dir", "medical_warehouse",
         "--profiles-dir", "medical_warehouse"],
        capture_output=True, text=True, cwd=os.getcwd()
    )
    context.log.info(test_result.stdout)
    return dg.MaterializeResult(
        metadata={"dbt_output": result.stdout[:500]}
    )


@dg.asset(
    description="Run YOLOv8 detection on downloaded images",
    deps=[dbt_models]
)
def yolo_detections(context):
    context.log.info("Running YOLO object detection...")
    result = subprocess.run(
        [sys.executable, "src/yolo_detection.py"],
        capture_output=True, text=True, cwd=os.getcwd()
    )
    if result.returncode != 0:
        raise Exception(f"YOLO failed: {result.stderr}")
    context.log.info(result.stdout)
    return dg.MaterializeResult(
        metadata={"output": result.stdout[:500]}
    )


defs = dg.Definitions(
    assets=[telegram_raw_data, postgres_raw_data, dbt_models, yolo_detections],
    schedules=[
        dg.ScheduleDefinition(
            job=dg.define_asset_job("daily_pipeline", selection=dg.AssetSelection.all()),
            cron_schedule="0 6 * * *",
        )
    ]
)
