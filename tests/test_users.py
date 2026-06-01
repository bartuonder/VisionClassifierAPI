from tests.conftest import DEFAULT_PASSWORD, login


def test_get_me_requires_auth(client):
    response = client.get("/user/me")
    assert response.status_code == 401


def test_get_me_returns_profile(client, auth_headers):
    response = client.get("/user/me", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "alice"
    assert body["email"] == "alice@example.com"
    assert "id" in body
    assert "hashed_password" not in body


def test_get_me_rejects_invalid_token(client):
    response = client.get("/user/me", headers={"Authorization": "Bearer not-a-token"})
    assert response.status_code == 401


def test_change_password_success(client, auth_headers):
    new_password = "brandnewpass456"
    response = client.put(
        "/user/change_password",
        headers=auth_headers,
        json={"password": DEFAULT_PASSWORD, "new_password": new_password},
    )
    assert response.status_code == 204
    assert login(client, password=DEFAULT_PASSWORD).status_code == 401
    assert login(client, password=new_password).status_code == 200


def test_change_password_wrong_old_password(client, auth_headers):
    response = client.put(
        "/user/change_password",
        headers=auth_headers,
        json={"password": "incorrectpass", "new_password": "brandnewpass456"},
    )
    assert response.status_code == 401


def test_change_password_validates_new_password_length(client, auth_headers):
    response = client.put(
        "/user/change_password",
        headers=auth_headers,
        json={"password": DEFAULT_PASSWORD, "new_password": "short"},
    )
    assert response.status_code == 422
