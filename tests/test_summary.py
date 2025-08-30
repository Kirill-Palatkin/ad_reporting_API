import pytest
from fastapi.testclient import TestClient
import sqlite3
from app.main import app
from app import db, llm


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    db.init_db()
    # Очистка таблицы
    with sqlite3.connect(db.DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM events")
        conn.commit()

    db.insert_events([
        {"date": "2025-08-01", "channel": "Google", "campaign_id": "CAMPAIGN_1", "impressions": 1000, "clicks": 50, "cost": 25.0},
        {"date": "2025-08-02", "channel": "Google", "campaign_id": "CAMPAIGN_1", "impressions": 1100, "clicks": 55, "cost": 27.0},
    ])


def test_summary_template_mode(monkeypatch):
    # Принудительно выключаем LLM
    monkeypatch.setattr(llm, "USE_LLM", False)
    response = client.get("/summary", params={"campaign_id": "CAMPAIGN_1", "date_from": "2025-08-01", "date_to": "2025-08-02"})
    assert response.status_code == 200
    summary = response.json()["summary"]
    assert "CTR=" in summary and "CPC=" in summary


def test_summary_llm_mode(monkeypatch):
    # Включаем LLM
    monkeypatch.setattr(llm, "USE_LLM", True)
    response = client.get("/summary", params={"campaign_id": "CAMPAIGN_1", "date_from": "2025-08-01", "date_to": "2025-08-02"})
    assert response.status_code == 200
    summary = response.json()["summary"]
    assert "CTR показывает долю кликов" in summary


def test_summary_no_data():
    response = client.get("/summary", params={"campaign_id": "UNKNOWN"})
    assert response.status_code == 204  # Недостаточно данных
