import io

import pytest
from PIL import Image

from db.models import ImageTask, Users
from tests.conftest import TestingSessionLocal, register, login


def make_image_bytes(fmt="PNG"):
    buffer = io.BytesIO()
    Image.new("RGB", (16, 16), color="red").save(buffer, format=fmt)
    buffer.seek(0)
    return buffer


@pytest.fixture
def temp_upload_dir(tmp_path, monkeypatch):
    import api.routes as routes
    monkeypatch.setattr(routes, "UPLOAD_DIR", str(tmp_path))
    return tmp_path


def test_upload_requires_auth(client):
    response = client.post(
        "/classify/",
        files={"file": ("img.png", make_image_bytes(), "image/png")},
    )
    assert response.status_code == 401


def test_upload_success_enqueues_task(client, auth_headers, delay_calls, temp_upload_dir):
    response = client.post(
        "/classify/",
        headers=auth_headers,
        files={"file": ("img.png", make_image_bytes(), "image/png")},
    )
    assert response.status_code == 202
    body = response.json()
    assert body["task_id"] == 1
    assert body["status_url"] == "/classify/status/1"

    assert len(delay_calls) == 1
    assert delay_calls[0][0] == (1,)

    assert any(temp_upload_dir.iterdir())


def test_upload_rejects_non_image(client, auth_headers, temp_upload_dir):
    response = client.post(
        "/classify/",
        headers=auth_headers,
        files={"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 400


def test_upload_rejects_filename_without_extension(client, auth_headers, temp_upload_dir):
    response = client.post(
        "/classify/",
        headers=auth_headers,
        files={"file": ("noextension", make_image_bytes(), "image/png")},
    )
    assert response.status_code == 400


def _current_user_id(client, headers):
    return client.get("/user/me", headers=headers).json()["id"]


def test_status_returns_task_for_owner(client, auth_headers):
    user_id = _current_user_id(client, auth_headers)

    db = TestingSessionLocal()
    task = ImageTask(
        user_id=user_id,
        filename="uploads/x.png",
        status="completed",
        prediction_label="tabby cat",
        confidence_score=92.5,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    db.close()

    response = client.get(f"/classify/status/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["prediction"] == "tabby cat"
    assert body["confidence"] == 92.5


def test_status_not_found(client, auth_headers):
    response = client.get("/classify/status/9999", headers=auth_headers)
    assert response.status_code == 404


def test_status_forbidden_for_other_user(client, auth_headers):

    register(client, username="bob", email="bob@example.com")
    bob_headers = {
        "Authorization": f"Bearer {login(client, username='bob').json()['access_token']}"
    }
    bob_id = _current_user_id(client, bob_headers)

    db = TestingSessionLocal()
    task = ImageTask(user_id=bob_id, filename="uploads/bob.png", status="pending")
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    db.close()

    response = client.get(f"/classify/status/{task_id}", headers=auth_headers)
    assert response.status_code == 403
