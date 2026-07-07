from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.database import get_session
from app.dependencies.auth import get_current_user
from app.models.db_models import UserDB
from app.schemas.application import (
    ApplicationCreate,
    ApplicationStatusUpdate,
    JobApplication,
)
from app.services import applications as application_service


router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post(
    "",
    response_model=JobApplication,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    application_data: ApplicationCreate,
    session: Session = Depends(get_session),
    current_user: UserDB = Depends(get_current_user),
):
    return application_service.create_application_for_user(
        session=session,
        application_data=application_data,
        current_user=current_user,
    )


@router.get("", response_model=list[JobApplication])
def get_applications(
    session: Session = Depends(get_session),
    current_user: UserDB = Depends(get_current_user),
):
    return application_service.get_applications_for_user(
        session=session,
        current_user=current_user,
    )


@router.get("/profile/{profile_id}", response_model=list[JobApplication])
def get_applications_for_profile(
    profile_id: int,
    session: Session = Depends(get_session),
    current_user: UserDB = Depends(get_current_user),
):
    return application_service.get_applications_for_user_profile(
        session=session,
        profile_id=profile_id,
        current_user=current_user,
    )


@router.get("/{application_id}", response_model=JobApplication)
def get_application(
    application_id: int,
    session: Session = Depends(get_session),
    current_user: UserDB = Depends(get_current_user),
):
    return application_service.get_application_for_user(
        session=session,
        application_id=application_id,
        current_user=current_user,
    )


@router.patch("/{application_id}/status", response_model=JobApplication)
def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    session: Session = Depends(get_session),
    current_user: UserDB = Depends(get_current_user),
):
    return application_service.update_application_status_for_user(
        session=session,
        application_id=application_id,
        status_update=status_update,
        current_user=current_user,
    )