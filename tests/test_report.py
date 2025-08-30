import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Фикстура для загрузки тестовых данных
@pytest.fixture(scope="module", autouse=True)
def ingest_sample_data():
    # Загружаем CSV через эндпоинт /ingest
    with open("data/sample_events.csv", "rb") as f:
        response = client.post("/ingest", files={"file": f})
        assert response.status_code == 200
        assert response.json().get("status") == "ok"
    yield
    # Можно добавить очистку базы после тестов при необходимости


def test_report_valid_campaign():
    response = client.get("/report", params={"campaign_id": "CAMPAIGN_1"})
    assert response.status_code == 200
    data = response.json()
    assert "impressions" in data
    assert "clicks" in data
    assert "cost" in data
    assert "ctr" in data
    assert "cpc" in data
    assert data["status"] == "ok"
    # Проверка расчетов
    assert data["impressions"] > 0
    assert 0 <= data["ctr"] <= 1
    assert data["cpc"] > 0


def test_report_no_data():
    # Кампания, которой нет
    response = client.get("/report", params={"campaign_id": "UNKNOWN"})
    assert response.status_code == 204  # "Нет данных" возвращает 204


def test_summary_valid_campaign():
    response = client.get("/summary", params={
        "campaign_id": "CAMPAIGN_1",
        "date_from": "2025-08-01",
        "date_to": "2025-08-07"
    })
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert isinstance(data["summary"], str)
    # Проверка на присутствие CTR и CPC в тексте
    assert "CTR" in data["summary"]
    assert "CPC" in data["summary"]


def test_summary_no_data():
    response = client.get("/summary", params={
        "campaign_id": "UNKNOWN",
        "date_from": "2025-08-01",
        "date_to": "2025-08-07"
    })
    assert response.status_code == 204
