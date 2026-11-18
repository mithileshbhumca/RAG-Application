from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_end_to_end_text_ingestion(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    fixture_path = Path(__file__).parent / "fixtures" / "sample.txt"
    with fixture_path.open("rb") as fixture:
        upload = client.post(
            "/api/v1/documents/upload",
            files={"file": ("sample.txt", fixture.read(), "text/plain")},
        )

    assert upload.status_code == 200
    document_id = upload.json()["document"]["document_id"]

    ingest = client.post(f"/api/v1/documents/{document_id}/ingest")
    assert ingest.status_code == 200
    assert ingest.json()["status"]["state"] == "completed"

    chunks = client.get(f"/api/v1/documents/{document_id}/chunks")
    assert chunks.status_code == 200
    assert chunks.json()["chunks"]

    metadata = client.get(f"/api/v1/documents/{document_id}/metadata")
    assert metadata.status_code == 200
    assert metadata.json()["document"]["checksum_sha256"]

    status = client.get(f"/api/v1/documents/{document_id}/status")
    assert status.status_code == 200
    assert status.json()["status"]["document_id"] == document_id


def test_duplicate_reprocessing_is_idempotent(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    content = b"idempotent validation content"

    first = client.post(
        "/api/v1/documents/upload",
        files={"file": ("first.txt", content, "text/plain")},
    )
    second = client.post(
        "/api/v1/documents/upload",
        files={"file": ("second.txt", content, "text/plain")},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["document"]["document_id"] == second.json()["document"]["document_id"]
