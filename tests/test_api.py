import io
import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_list_images_empty(monkeypatch):
    class FakeRepo:
        def list_images(self, **kwargs):
            return []

    app.dependency_overrides = {}
    from app.api.routes import get_repo

    app.dependency_overrides[get_repo] = lambda: FakeRepo()

    resp = client.get("/api/images")
    assert resp.status_code == 200
    assert resp.json() == []


def test_upload_and_download(monkeypatch):
    stored = {}

    class FakeS3:
        def put_object(self, key, content, content_type):
            stored[key] = (content, content_type)
            return f"s3://bucket/{key}"

        def get_object(self, key):
            return stored[key][0]

        def delete_object(self, key):
            stored.pop(key, None)

    class FakeRepo:
        def __init__(self):
            self.docs = {}

        def insert_image(self, doc):
            self.docs[doc["s3_key"]] = doc
            return "1"

        def get_image_by_key(self, key):
            return self.docs.get(key)

        def delete_by_key(self, key):
            return self.docs.pop(key, None) is not None

    from app.api.routes import get_repo, get_s3

    app.dependency_overrides[get_repo] = lambda: FakeRepo()
    app.dependency_overrides[get_s3] = lambda: FakeS3()

    file_content = b"hello-image"
    files = {"file": ("pic.png", io.BytesIO(file_content), "image/png")}

    resp = client.post("/api/images", params={"user_id": "u1"}, files=files)
    assert resp.status_code == 201
    body = resp.json()
    assert body["filename"] == "pic.png"
    assert body["size"] == len(file_content)

    # Download
    key_part = body["s3_key"].split("/", 1)[1]
    resp2 = client.get(f"/api/images/u1/{key_part}")
    assert resp2.status_code == 200
    assert resp2.content == file_content

    # Delete
    resp3 = client.delete(f"/api/images/u1/{key_part}")
    assert resp3.status_code == 204


