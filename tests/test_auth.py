from tests.conftest import register, login, DEFAULT_PASSWORD


def test_signup_success(client):
    response = register(client)
    assert response.status_code == 201


def test_signup_duplicate_username_or_email(client):
    register(client)
    response = register(client, username="alice", email="other@example.com")
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_signup_rejects_short_password(client):
    response = register(client, password="short")
    assert response.status_code == 422


def test_signup_rejects_invalid_email(client):
    response = client.post(
        "/auth/signup",
        json={"username": "bob", "email": "not-an-email", "password": DEFAULT_PASSWORD},
    )
    assert response.status_code == 422


def test_login_success_returns_bearer_token(client):
    register(client)
    response = login(client)
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password(client):
    register(client)
    response = login(client, password="wrongpassword123")
    assert response.status_code == 401


def test_login_unknown_user(client):
    response = login(client, username="ghost")
    assert response.status_code == 401
