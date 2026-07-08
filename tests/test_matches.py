from fastapi.testclient import TestClient
from sqlmodel import Session

from app.repositories import users as user_repository


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


def build_job_payload():
    return {
        "title": "Junior Python Backend Developer",
        "company": "Example Tech",
        "location": "London",
        "remote_type": "hybrid",
        "employment_type": "full_time",
        "description": (
            "We are looking for a junior Python backend developer "
            "with FastAPI, SQL and Git knowledge."
        ),
        "apply_url": "https://example.com/jobs/junior-python-backend",
        "source": "manual",
        "required_skills": ["Python", "FastAPI", "SQL", "Git"],
        "salary_min": 30000,
        "salary_max": 40000,
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


def make_user_admin(
    session: Session,
    email: str,
):
    user = user_repository.get_user_by_email(
        session=session,
        email=email,
    )

    user_repository.update_user_role(
        session=session,
        user=user,
        role="admin",
    )


def create_profile(
    client: TestClient,
    headers: dict,
) -> int:
    response = client.post(
        "/profiles",
        json=build_profile_payload(),
        headers=headers,
    )

    assert response.status_code == 200

    return response.json()["id"]


def create_job_as_admin(
    client: TestClient,
    session: Session,
) -> int:
    email = "matchadmin@example.com"

    admin_headers = register_and_login(
        client=client,
        email=email,
        full_name="Match Admin",
    )

    make_user_admin(
        session=session,
        email=email,
    )

    response = client.post(
        "/jobs",
        json=build_job_payload(),
        headers=admin_headers,
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_matches_require_authentication(client: TestClient):
    response = client.get("/matches/profile/1")

    assert response.status_code == 401


def test_user_can_get_live_matches_for_own_profile(
    client: TestClient,
    session: Session,
    auth_headers: dict,
):
    profile_id = create_profile(
        client=client,
        headers=auth_headers,
    )

    create_job_as_admin(
        client=client,
        session=session,
    )

    response = client.get(
        f"/matches/profile/{profile_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Junior Python Backend Developer"
    assert data[0]["match_percentage"] > 0
    assert "Python" in data[0]["matched_skills"]


def test_user_can_refresh_and_get_saved_matches(
    client: TestClient,
    session: Session,
    auth_headers: dict,
):
    profile_id = create_profile(
        client=client,
        headers=auth_headers,
    )

    create_job_as_admin(
        client=client,
        session=session,
    )

    refresh_response = client.post(
        f"/matches/profile/{profile_id}/refresh",
        headers=auth_headers,
    )

    assert refresh_response.status_code == 200

    refresh_data = refresh_response.json()

    assert refresh_data["profile_id"] == profile_id
    assert refresh_data["total_jobs_checked"] == 1
    assert refresh_data["matches_saved"] == 1
    assert len(refresh_data["top_matches"]) == 1

    saved_response = client.get(
        f"/matches/profile/{profile_id}/saved",
        headers=auth_headers,
    )

    assert saved_response.status_code == 200

    saved_data = saved_response.json()

    assert saved_data["total_count"] == 1
    assert saved_data["returned_count"] == 1
    assert saved_data["items"][0]["job_title"] == "Junior Python Backend Developer"


def test_saved_matches_support_min_score_filter(
    client: TestClient,
    session: Session,
    auth_headers: dict,
):
    profile_id = create_profile(
        client=client,
        headers=auth_headers,
    )

    create_job_as_admin(
        client=client,
        session=session,
    )

    client.post(
        f"/matches/profile/{profile_id}/refresh",
        headers=auth_headers,
    )

    response = client.get(
        f"/matches/profile/{profile_id}/saved?min_score=95",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["min_score"] == 95
    assert data["total_count"] in [0, 1]


def test_user_cannot_access_another_users_matches(
    client: TestClient,
    session: Session,
):
    user_one_headers = register_and_login(
        client=client,
        email="matchowner@example.com",
        full_name="Match Owner",
    )

    user_one_profile_id = create_profile(
        client=client,
        headers=user_one_headers,
    )

    create_job_as_admin(
        client=client,
        session=session,
    )

    user_two_headers = register_and_login(
        client=client,
        email="matchintruder@example.com",
        full_name="Match Intruder",
    )

    response = client.get(
        f"/matches/profile/{user_one_profile_id}",
        headers=user_two_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"


def test_user_cannot_refresh_another_users_matches(
    client: TestClient,
    session: Session,
):
    user_one_headers = register_and_login(
        client=client,
        email="refreshowner@example.com",
        full_name="Refresh Owner",
    )

    user_one_profile_id = create_profile(
        client=client,
        headers=user_one_headers,
    )

    create_job_as_admin(
        client=client,
        session=session,
    )

    user_two_headers = register_and_login(
        client=client,
        email="refreshintruder@example.com",
        full_name="Refresh Intruder",
    )

    response = client.post(
        f"/matches/profile/{user_one_profile_id}/refresh",
        headers=user_two_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"