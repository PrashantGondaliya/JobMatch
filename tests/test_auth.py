from fastapi.testclient import TestClient


def test_register_user(client: TestClient, test_user_payload: dict):
    response = client.post(
        "/auth/register",
        json=test_user_payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == test_user_payload["email"]
    assert data["full_name"] == test_user_payload["full_name"]
    assert data["is_active"] is True

    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email_fails(
    client: TestClient,
    test_user_payload: dict,
):
    client.post(
        "/auth/register",
        json=test_user_payload,
    )

    response = client.post(
        "/auth/register",
        json=test_user_payload,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email is already registered"


def test_login_returns_access_token(
    client: TestClient,
    test_user_payload: dict,
):
    client.post(
        "/auth/register",
        json=test_user_payload,
    )

    response = client.post(
        "/auth/login",
        data={
            "username": test_user_payload["email"],
            "password": test_user_payload["password"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_wrong_password_fails(
    client: TestClient,
    test_user_payload: dict,
):
    client.post(
        "/auth/register",
        json=test_user_payload,
    )

    response = client.post(
        "/auth/login",
        data={
            "username": test_user_payload["email"],
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_auth_me_requires_login(client: TestClient):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_auth_me_returns_current_user(
    client: TestClient,
    auth_headers: dict,
    test_user_payload: dict,
):
    response = client.get(
        "/auth/me",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == test_user_payload["email"]
    assert data["full_name"] == test_user_payload["full_name"]