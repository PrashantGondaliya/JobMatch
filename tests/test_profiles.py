from fastapi.testclient import TestClient


def build_profile_payload():
    return {
        "full_name": "Prashant Gondaliya",
        "target_role": "Python Backend Developer",
        "years_of_experience": 0,
        "skills": ["Python", "FastAPI", "SQL", "Git"],
        "preferred_locations": ["London", "Remote"],
        "remote_preference": "remote",
        "expected_salary_min": 30000,
        "expected_salary_max": 45000,
    }


def register_and_login(
    client: TestClient,
    email: str,
    full_name: str = "Test User",
):
    password = "StrongPassword123"

    client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": full_name,
            "password": password,
        },
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    access_token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}"
    }


def test_profiles_require_authentication(client: TestClient):
    response = client.get("/profiles")

    assert response.status_code == 401


def test_authenticated_user_can_create_profile(
    client: TestClient,
    auth_headers: dict,
):
    response = client.post(
        "/profiles",
        json=build_profile_payload(),
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["full_name"] == "Prashant Gondaliya"
    assert data["target_role"] == "Python Backend Developer"
    assert "user_id" not in data


def test_authenticated_user_can_view_own_profiles(
    client: TestClient,
    auth_headers: dict,
):
    client.post(
        "/profiles",
        json=build_profile_payload(),
        headers=auth_headers,
    )

    response = client.get(
        "/profiles",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["full_name"] == "Prashant Gondaliya"


def test_user_cannot_access_another_users_profile(client: TestClient):
    user_one_headers = register_and_login(
        client=client,
        email="userone@example.com",
        full_name="User One",
    )

    create_profile_response = client.post(
        "/profiles",
        json=build_profile_payload(),
        headers=user_one_headers,
    )

    profile_id = create_profile_response.json()["id"]

    user_two_headers = register_and_login(
        client=client,
        email="usertwo@example.com",
        full_name="User Two",
    )

    response = client.get(
        f"/profiles/{profile_id}",
        headers=user_two_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"