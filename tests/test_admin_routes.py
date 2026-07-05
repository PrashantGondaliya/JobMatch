from fastapi.testclient import TestClient
from sqlmodel import Session

from app.repositories import users as user_repository


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


def test_normal_user_cannot_create_job(
    client: TestClient,
    auth_headers: dict,
):
    response = client.post(
        "/jobs",
        json=build_job_payload(),
        headers=auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_admin_user_can_create_job(
    client: TestClient,
    session: Session,
):
    email = "admin@example.com"

    admin_headers = register_and_login(
        client=client,
        email=email,
        full_name="Admin User",
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

    data = response.json()

    assert data["title"] == "Junior Python Backend Developer"
    assert data["company"] == "Example Tech"


def test_normal_user_cannot_create_job_source(
    client: TestClient,
    auth_headers: dict,
):
    response = client.post(
        "/job-sources",
        json={
            "source_type": "greenhouse",
            "company_slug": "greenhouse",
            "display_name": "Greenhouse Careers",
            "is_active": True,
        },
        headers=auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_admin_user_can_create_job_source(
    client: TestClient,
    session: Session,
):
    email = "jobsourceadmin@example.com"

    admin_headers = register_and_login(
        client=client,
        email=email,
        full_name="Job Source Admin",
    )

    make_user_admin(
        session=session,
        email=email,
    )

    response = client.post(
        "/job-sources",
        json={
            "source_type": "greenhouse",
            "company_slug": "greenhouse",
            "display_name": "Greenhouse Careers",
            "is_active": True,
        },
        headers=admin_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["company_slug"] == "greenhouse"
    assert data["display_name"] == "Greenhouse Careers"