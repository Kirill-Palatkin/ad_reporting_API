import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import db
import io
import csv

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Инициализация базы и очистка таблицы перед каждым тестом
    db.init_db()
    conn = db.sqlite3.connect(db.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events")
    conn.commit()
    conn.close()


def test_ingest_valid_csv():
    csv_content = "date,channel,campaign_id,impressions,clicks,cost\n"
    csv_content += "2025-08-01,Google,CAMPAIGN_1,1000,50,25.0\n"
    csv_file = io.BytesIO(csv_content.encode("utf-8"))

    response = client.post("/ingest", files={"file": ("sample.csv", csv_file, "text/csv")})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["ingested"] == 1


def test_ingest_invalid_csv():
    # Некорректные данные: отрицательные значения
    csv_content = "date,channel,campaign_id,impressions,clicks,cost\n"
    csv_content += "2025-08-01,Google,CAMPAIGN_1,-1000,50,25.0\n"
    csv_file = io.BytesIO(csv_content.encode("utf-8"))

    response = client.post("/ingest", files={"file": ("sample.csv", csv_file, "text/csv")})
    assert response.status_code == 400
    data = response.json()
    assert "Отрицательное значение" in data["detail"][0]
