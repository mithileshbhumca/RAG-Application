from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_payload() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chunks_missing_document() -> None:
    response = client.get("/api/v1/documents/doc_missing/chunks")

    assert response.status_code == 404
