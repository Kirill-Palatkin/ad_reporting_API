import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import db
import sqlite3

client = TestClient(app)


# Загружаем тестовые данные в SQLite перед тестами
# @pytest.fixture(scope="module", autouse=True)
# def setup_db():
#     # Можно использовать data/sample_events.csv или ручное добавление
#     db.init_db()
#     db.insert_event({
#         "date": "2025-08-01",
#         "channel": "Google",
#         "campaign_id": "CAMPAIGN_1",
#         "impressions": 1000,
#         "clicks": 50,
#         "cost": 25.0
#     })
#     db.insert_event({
#         "date": "2025-08-02",
#         "channel": "Facebook",
#         "campaign_id": "CAMPAIGN_2",
#         "impressions": 500,
#         "clicks": 20,
#         "cost": 10.0
#     })

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    db.init_db()
    conn = sqlite3.connect(db.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events")
    conn.commit()
    conn.close()

    test_events = [
        {"date": "2025-08-01", "channel": "Google", "campaign_id": "CAMPAIGN_1", "impressions": 1000, "clicks": 50,
         "cost": 25.0},
        {"date": "2025-08-01", "channel": "Facebook", "campaign_id": "CAMPAIGN_2", "impressions": 500, "clicks": 20,
         "cost": 10.0},
    ]

    db.insert_events(test_events)


def test_aggregates_all():
    response = client.get("/aggregates")
    assert response.status_code == 200
    data = response.json()
    assert "aggregates" in data
    assert len(data["aggregates"]) >= 2


def test_aggregates_campaign():
    response = client.get("/aggregates?campaign_id=CAMPAIGN_1")
    assert response.status_code == 200
    data = response.json()
    agg = data["aggregates"][0]
    assert agg["campaign_id"] == "CAMPAIGN_1"
    assert agg["impressions"] == 1000
    assert agg["clicks"] == 50


def test_aggregates_channel():
    response = client.get("/aggregates?channel=Facebook")
    assert response.status_code == 200
    data = response.json()
    agg = data["aggregates"][0]
    assert agg["channel"] == "Facebook"
    assert agg["impressions"] == 500
    assert agg["clicks"] == 20


def test_aggregates_no_data():
    response = client.get("/aggregates?campaign_id=UNKNOWN")
    assert response.status_code == 204
