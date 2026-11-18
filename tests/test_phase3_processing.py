from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_plain_text_ingestion(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    upload = client.post(
        "/api/v1/documents/upload",
        files={"file": ("sample.txt", b"A short document for ingestion.", "text/plain")},
    )
    assert upload.status_code == 200
    document_id = upload.json()["document"]["document_id"]

    ingest = client.post(f"/api/v1/documents/{document_id}/ingest")

    assert ingest.status_code == 200
    assert ingest.json()["status"]["state"] in {"completed", "partial_completed"}

    normalized = tmp_path / "data" / "processed" / document_id / "normalized.json"
    assert normalized.is_file()


def test_ingest_missing_document() -> None:
    response = client.post("/api/v1/documents/doc_missing/ingest")

    assert response.status_code == 404
