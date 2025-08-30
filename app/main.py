# from fastapi import FastAPI, UploadFile, File, HTTPException, Query
# from fastapi.responses import StreamingResponse
# import csv, io, pandas as pd
# from app import db, metrics, llm, models
# from dotenv import load_dotenv
# import os
#
# load_dotenv()  # читает .env
#
# USE_LLM = os.getenv("USE_LLM", "0") == "1"
#
# db.init_db()
# app = FastAPI(title="Ad Reporting API")
#
#
# # POST /ingest
# @app.post("/ingest")
# async def ingest(file: UploadFile = File(...)):
#     content = await file.read()
#     try:
#         df = pd.read_csv(io.BytesIO(content))
#         records = df.to_dict(orient="records")
#         for r in records:
#             # Валидация
#             if any(x is None for x in [r.get("date"), r.get("channel"), r.get("campaign_id"),
#                                        r.get("impressions"), r.get("clicks"), r.get("cost")]):
#                 raise HTTPException(status_code=400, detail="Пропущенные значения")
#         db.insert_events(records)
#         return {"status": "ok", "ingested": len(records)}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
#
#
# # GET /report
# @app.get("/report")
# def report(campaign_id: str = None, date_from: str = None, date_to: str = None):
#     events = db.query_events(campaign_id, date_from, date_to)
#     if not events:
#         raise HTTPException(status_code=204, detail="Недостаточно данных")
#         # return {"status": "no_data"}
#     impressions = sum(e["impressions"] for e in events)
#     clicks = sum(e["clicks"] for e in events)
#     cost = sum(e["cost"] for e in events)
#     res = metrics.compute_metrics(impressions, clicks, cost)
#     return {"impressions": impressions, "clicks": clicks, "cost": cost, **res}
#
#
# # GET /export.csv
# @app.get("/export.csv")
# def export_csv(campaign_id: str = None, date_from: str = None, date_to: str = None):
#     events = db.query_events(campaign_id, date_from, date_to)
#     if not events:
#         raise HTTPException(status_code=204, detail="Недостаточно данных")
#     output = io.StringIO()
#     writer = csv.DictWriter(output, fieldnames=events[0].keys())
#     writer.writeheader()
#     writer.writerows(events)
#     output.seek(0)
#     return StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type="text/csv",
#                              headers={"Content-Disposition": "attachment; filename=report.csv"})
#
#
# # GET /health
# @app.get("/health")
# def health():
#     try:
#         db.query_events()
#         return {"status": "ok"}
#     except:
#         return {"status": "error"}
#
#
# # GET /summary
# @app.get("/summary")
# def summary(campaign_id: str = None, date_from: str = None, date_to: str = None):
#     events = db.query_events(campaign_id, date_from, date_to)
#     if not events:
#         raise HTTPException(status_code=204, detail="Недостаточно данных")
#
#     impressions = sum(e["impressions"] for e in events)
#     clicks = sum(e["clicks"] for e in events)
#     cost = sum(e["cost"] for e in events)
#     res = metrics.compute_metrics(impressions, clicks, cost)
#
#     if USE_LLM:
#         # правильно передаём весь словарь
#         summary_text = llm.explain_summary(res)
#     else:
#         summary_text = f"CTR={res['ctr'] * 100:.2f}%, CPC={res['cpc']:.2f}; данных достаточно."
#
#     return {"summary": summary_text}
















from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse
import csv, io, pandas as pd
from app import db, metrics, llm, models
from dotenv import load_dotenv
import os
import logging
import uuid  # <- добавляем здесь


load_dotenv()  # читает .env

USE_LLM = os.getenv("USE_LLM", "0") == "1"

db.init_db()
app = FastAPI(title="Ad Reporting API")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def log_request(action: str):
    request_id = str(uuid.uuid4())
    logger.info(f"{action} | request_id={request_id}")


def validate_row(row: dict):
    try:
        datetime.strptime(row["date"], "%Y-%m-%d")
        impressions = int(row["impressions"])
        clicks = int(row["clicks"])
        cost = float(row["cost"])
        if impressions < 0 or clicks < 0 or cost < 0:
            raise ValueError("Отрицательное значение")
        if not row["channel"] or not row["campaign_id"]:
            raise ValueError("Пустые обязательные поля")
    except Exception as e:
        raise ValueError(f"Ошибка в строке: {row}. Причина: {e}")


@app.post("/ingest")
async def ingest(file: UploadFile):
    log_request("POST /ingest")
    content = await file.read()
    decoded = content.decode("utf-8").splitlines()
    reader = csv.DictReader(decoded)
    valid_rows = []
    errors = []

    for row in reader:
        try:
            validate_row(row)
            valid_rows.append(row)
        except ValueError as e:
            errors.append(str(e))

    if errors:
        raise HTTPException(status_code=400, detail=errors)

    # Сохраняем валидные строки в базу
    for row in valid_rows:
        db.insert_event(row)  # твоя функция вставки в SQLite

    return {"status": "ok", "ingested": len(valid_rows), "errors": errors}


# GET /report
@app.get("/report")
def report(campaign_id: str = None, date_from: str = None, date_to: str = None):
    log_request("GET /report")
    events = db.query_events(campaign_id, date_from, date_to)
    if not events:
        raise HTTPException(status_code=204, detail="Недостаточно данных")
        # return {"status": "no_data"}
    impressions = sum(e["impressions"] for e in events)
    clicks = sum(e["clicks"] for e in events)
    cost = sum(e["cost"] for e in events)
    res = metrics.compute_metrics(impressions, clicks, cost)
    return {"impressions": impressions, "clicks": clicks, "cost": cost, **res}


# GET /export.csv
@app.get("/export.csv")
def export_csv(campaign_id: str = None, date_from: str = None, date_to: str = None):
    log_request("GET /export.csv")
    events = db.query_events(campaign_id, date_from, date_to)
    if not events:
        raise HTTPException(status_code=204, detail="Недостаточно данных")
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=events[0].keys())
    writer.writeheader()
    writer.writerows(events)
    output.seek(0)
    return StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=report.csv"})


# GET /health
@app.get("/health")
def health():
    log_request("GET /health")
    try:
        db.query_events()
        return {"status": "ok"}
    except:
        return {"status": "error"}


# GET /summary
@app.get("/summary")
def summary(campaign_id: str = None, date_from: str = None, date_to: str = None):
    log_request("GET /summary")
    events = db.query_events(campaign_id, date_from, date_to)
    if not events:
        raise HTTPException(status_code=204, detail="Недостаточно данных")

    impressions = sum(e["impressions"] for e in events)
    clicks = sum(e["clicks"] for e in events)
    cost = sum(e["cost"] for e in events)
    res = metrics.compute_metrics(impressions, clicks, cost)

    if USE_LLM:
        # правильно передаём весь словарь
        summary_text = llm.explain_summary(res)
    else:
        summary_text = f"CTR={res['ctr'] * 100:.2f}%, CPC={res['cpc']:.2f}; данных достаточно."

    return {"summary": summary_text}


@app.get("/aggregates")
def aggregates(channel: str = None, campaign_id: str = None, date_from: str = None, date_to: str = None):
    events = db.query_aggregated(channel, campaign_id, date_from, date_to)
    if not events:
        raise HTTPException(status_code=204, detail="Недостаточно данных")

    response = []
    for e in events:
        res = metrics.compute_metrics(e["impressions"], e["clicks"], e["cost"])
        response.append({**e, **res})
    return {"aggregates": response}
