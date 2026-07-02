from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.database import get_session
from app.dependencies.auth import get_current_user
from app.models.db_models import UserDB
from app.schemas.auth import Token, UserCreate, UserPublic
from app.services import auth as auth_service


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserCreate,
    session: Session = Depends(get_session),
):
    user = auth_service.register_user(
        session=session,
        user_data=user_data,
    )

    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Email is already registered",
        )

    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = auth_service.authenticate_user(
        session=session,
        email=form_data.username,
        password=form_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return auth_service.create_user_token(user=user)


@router.get("/me", response_model=UserPublic)
def get_me(
    current_user: UserDB = Depends(get_current_user),
):
    return current_user