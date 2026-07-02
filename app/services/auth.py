from datetime import timedelta

from sqlmodel import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models.db_models import UserDB
from app.repositories import users as user_repository
from app.schemas.auth import Token, UserCreate


def register_user(
    session: Session,
    user_data: UserCreate,
) -> UserDB | None:
    existing_user = user_repository.get_user_by_email(
        session=session,
        email=user_data.email,
    )

    if existing_user is not None:
        return None

    return user_repository.create_user(
        session=session,
        user_data=user_data,
    )


def authenticate_user(
    session: Session,
    email: str,
    password: str,
) -> UserDB | None:
    user = user_repository.get_user_by_email(
        session=session,
        email=email,
    )

    if user is None:
        return None

    if not user.is_active:
        return None

    if not verify_password(
        plain_password=password,
        hashed_password=user.hashed_password,
    ):
        return None

    return user


def create_user_token(user: UserDB) -> Token:
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=expires_delta,
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
    )