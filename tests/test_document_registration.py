from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_upload_duplicate_detection(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    first = client.post(
        "/api/v1/documents/upload",
        files={"file": ("note.txt", b"same content", "text/plain")},
    )
    second = client.post(
        "/api/v1/documents/upload",
        files={"file": ("copy.txt", b"same content", "text/plain")},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["duplicate"] is False
    assert second.json()["duplicate"] is True
