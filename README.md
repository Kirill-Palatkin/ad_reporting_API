# Ad Reporting API

## Мини-API отчётности по кампаниям.

# Как поднять?
## 1. Создать виртуальное окружение
python -m venv .venv

## 2. Активировать виртуальное окружение
source .venv/bin/activate (.venv\Scripts\activate)

## 3. Установить зависимости
pip install -r requirements.txt

## 4. Создать файл .env (если еще не создан) на основе .env.example
USE_LLM=1

MODEL_NAME=stub

DB_URL=sqlite:///./app.db

## 5. Запуск сервера
uvicorn app.main:app --reload

# Примеры curl
### POST /ingest
curl -X POST "http://127.0.0.1:8000/ingest" -F "file=@data/sample_events.csv"

### GET /report
curl "http://127.0.0.1:8000/report?campaign_id=CAMPAIGN_1&date_from=2025-08-01&date_to=2025-08-07"

### GET /export.csv
curl "http://127.0.0.1:8000/export.csv?campaign_id=CAMPAIGN_1&date_from=2025-08-01&date_to=2025-08-07" -o report.csv

### GET /health
curl "http://127.0.0.1:8000/health"

### GET /summary
curl "http://127.0.0.1:8000/summary?campaign_id=CAMPAIGN_1&date_from=2025-08-01&date_to=2025-08-07"

### GET /aggregates
- По всем каналам: curl "http://127.0.0.1:8000/aggregates"
- По конкретной кампании: curl "http://127.0.0.1:8000/aggregates?campaign_id=CAMPAIGN_1"
- По конкретному каналу: curl "http://127.0.0.1:8000/aggregates?channel=Google"
- По комбинации: curl "http://127.0.0.1:8000/aggregates?channel=Google&campaign_id=CAMPAIGN_1"

# Пример data/sample_events.csv
date,channel,campaign_id,impressions,clicks,cost

2025-08-01,Google,CAMPAIGN_1,1000,50,25

2025-08-01,Facebook,CAMPAIGN_2,500,20,10

2025-08-02,Google,CAMPAIGN_1,1100,55,27

# Запуск тестов

### /summary
python -m pytest -q tests/test_summary.py 

### /report
python -m pytest -q tests/test_report.py 

### /ingest
python -m pytest -q tests/test_ingest.py 

### /aggregates
python -m pytest -q tests/test_aggregates.py 