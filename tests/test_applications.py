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
    email = "applicationadmin@example.com"

    admin_headers = register_and_login(
        client=client,
        email=email,
        full_name="Application Admin",
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


def test_applications_require_authentication(client: TestClient):
    response = client.get("/applications")

    assert response.status_code == 401


def test_user_can_create_application_for_own_profile(
    client: TestClient,
    session: Session,
    auth_headers: dict,
):
    profile_id = create_profile(
        client=client,
        headers=auth_headers,
    )

    job_id = create_job_as_admin(
        client=client,
        session=session,
    )

    response = client.post(
        "/applications",
        json={
            "profile_id": profile_id,
            "job_id": job_id,
            "status": "saved",
            "notes": "Looks suitable.",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["profile_id"] == profile_id
    assert data["job_id"] == job_id
    assert data["status"] == "saved"
    assert data["notes"] == "Looks suitable."


def test_duplicate_application_fails(
    client: TestClient,
    session: Session,
    auth_headers: dict,
):
    profile_id = create_profile(
        client=client,
        headers=auth_headers,
    )

    job_id = create_job_as_admin(
        client=client,
        session=session,
    )

    payload = {
        "profile_id": profile_id,
        "job_id": job_id,
        "status": "saved",
        "notes": "Looks suitable.",
    }

    first_response = client.post(
        "/applications",
        json=payload,
        headers=auth_headers,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/applications",
        json=payload,
        headers=auth_headers,
    )

    assert second_response.status_code == 400
    assert (
        second_response.json()["detail"]
        == "Application already exists for this profile and job"
    )


def test_user_can_update_own_application_status(
    client: TestClient,
    session: Session,
    auth_headers: dict,
):
    profile_id = create_profile(
        client=client,
        headers=auth_headers,
    )

    job_id = create_job_as_admin(
        client=client,
        session=session,
    )

    create_response = client.post(
        "/applications",
        json={
            "profile_id": profile_id,
            "job_id": job_id,
            "status": "saved",
            "notes": "Initial save.",
        },
        headers=auth_headers,
    )

    application_id = create_response.json()["id"]

    update_response = client.patch(
        f"/applications/{application_id}/status",
        json={
            "status": "applied",
            "notes": "Applied through company website.",
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["status"] == "applied"
    assert data["notes"] == "Applied through company website."
    assert data["applied_at"] is not None


def test_user_cannot_create_application_for_another_users_profile(
    client: TestClient,
    session: Session,
):
    user_one_headers = register_and_login(
        client=client,
        email="applicationuserone@example.com",
        full_name="Application User One",
    )

    user_one_profile_id = create_profile(
        client=client,
        headers=user_one_headers,
    )

    job_id = create_job_as_admin(
        client=client,
        session=session,
    )

    user_two_headers = register_and_login(
        client=client,
        email="applicationusertwo@example.com",
        full_name="Application User Two",
    )

    response = client.post(
        "/applications",
        json={
            "profile_id": user_one_profile_id,
            "job_id": job_id,
            "status": "saved",
            "notes": "Trying to access another user's profile.",
        },
        headers=user_two_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"


def test_user_cannot_access_another_users_application(
    client: TestClient,
    session: Session,
):
    user_one_headers = register_and_login(
        client=client,
        email="applicationowner@example.com",
        full_name="Application Owner",
    )

    profile_id = create_profile(
        client=client,
        headers=user_one_headers,
    )

    job_id = create_job_as_admin(
        client=client,
        session=session,
    )

    create_response = client.post(
        "/applications",
        json={
            "profile_id": profile_id,
            "job_id": job_id,
            "status": "saved",
            "notes": "Owner application.",
        },
        headers=user_one_headers,
    )

    application_id = create_response.json()["id"]

    user_two_headers = register_and_login(
        client=client,
        email="applicationintruder@example.com",
        full_name="Application Intruder",
    )

    response = client.get(
        f"/applications/{application_id}",
        headers=user_two_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"