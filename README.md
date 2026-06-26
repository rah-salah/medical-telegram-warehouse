# Medical Telegram Warehouse

An end-to-end ELT pipeline for Ethiopian medical businesses using Telegram data.

## Stack
- Scraping: Telethon
- Warehouse: PostgreSQL
- Transformation: dbt
- Enrichment: YOLOv8
- API: FastAPI
- Orchestration: Dagster

## Data Sources
- CheMed: https://t.me/CheMed123
- Lobelia Cosmetics: https://t.me/lobelia4cosmetics
- Tikvah Pharma: https://t.me/tikvahpharma

## Setup
1. Clone the repo
2. Fill in .env credentials
3. Run pip install -r requirements.txt
