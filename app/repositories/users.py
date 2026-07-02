from datetime import datetime, timezone

from sqlmodel import Session, select

from app.core.security import hash_password
from app.models.db_models import UserDB
from app.schemas.auth import UserCreate


def get_current_time() -> datetime:
    return datetime.now(timezone.utc)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def create_user(
    session: Session,
    user_data: UserCreate,
) -> UserDB:
    user = UserDB(
        email=normalize_email(user_data.email),
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def get_user_by_email(
    session: Session,
    email: str,
) -> UserDB | None:
    statement = select(UserDB).where(
        UserDB.email == normalize_email(email)
    )

    return session.exec(statement).first()


def get_user_by_id(
    session: Session,
    user_id: int,
) -> UserDB | None:
    return session.get(UserDB, user_id)


def update_user_last_modified(
    session: Session,
    user: UserDB,
) -> UserDB:
    user.updated_at = get_current_time()

    session.add(user)
    session.commit()
    session.refresh(user)

    return user