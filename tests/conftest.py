import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.database import get_session
from app.main import app
from app.models import db_models  # noqa: F401


@pytest.fixture(name="session")
def session_fixture():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(test_engine)

    with Session(test_engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_test_session():
        yield session

    app.dependency_overrides[get_session] = get_test_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_payload():
    return {
        "email": "prashant@example.com",
        "full_name": "Prashant Gondaliya",
        "password": "StrongPassword123",
    }


@pytest.fixture
def auth_headers(client: TestClient, test_user_payload: dict):
    client.post("/auth/register", json=test_user_payload)

    login_response = client.post(
        "/auth/login",
        data={
            "username": test_user_payload["email"],
            "password": test_user_payload["password"],
        },
    )

    access_token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}"
    }