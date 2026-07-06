from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.errors import bad_request, not_found
from app.database import get_session
from app.dependencies.auth import get_current_user
from app.models.db_models import UserDB
from app.repositories import applications as application_repository
from app.repositories import jobs as job_repository
from app.schemas.application import (
    ApplicationCreate,
    ApplicationStatus,
    ApplicationStatusUpdate,
    JobApplication,
)
from app.services.ownership import (
    get_current_user_profile_ids,
    get_owned_application_or_404,
    get_owned_profile_or_404,
)


router = APIRouter(prefix="/applications", tags=["Applications"])


def get_current_time() -> datetime:
    return datetime.now(timezone.utc)


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
    get_owned_profile_or_404(
        session=session,
        profile_id=application_data.profile_id,
        current_user=current_user,
    )

    job = job_repository.get_job_by_id(
        session=session,
        job_id=application_data.job_id,
    )

    if job is None:
        raise not_found("Job")

    existing_application = application_repository.get_application_by_profile_and_job(
        session=session,
        profile_id=application_data.profile_id,
        job_id=application_data.job_id,
    )

    if existing_application is not None:
        raise bad_request("Application already exists for this profile and job")

    applied_at = None

    if application_data.status == ApplicationStatus.APPLIED:
        applied_at = get_current_time()

    return application_repository.create_application(
        session=session,
        application_data=application_data,
        applied_at=applied_at,
    )


@router.get("", response_model=list[JobApplication])
def get_applications(
    session: Session = Depends(get_session),
    current_user: UserDB = Depends(get_current_user),
):
    profile_ids = get_current_user_profile_ids(
        session=session,
        current_user=current_user,
    )

    return application_repository.get_applications_by_profile_ids(
        session=session,
        profile_ids=profile_ids,
    )


@router.get("/profile/{profile_id}", response_model=list[JobApplication])
def get_applications_for_profile(
    profile_id: int,
    session: Session = Depends(get_session),
    current_user: UserDB = Depends(get_current_user),
):
    get_owned_profile_or_404(
        session=session,
        profile_id=profile_id,
        current_user=current_user,
    )

    return application_repository.get_applications_by_profile_id(
        session=session,
        profile_id=profile_id,
    )


@router.get("/{application_id}", response_model=JobApplication)
def get_application(
    application_id: int,
    session: Session = Depends(get_session),
    current_user: UserDB = Depends(get_current_user),
):
    return get_owned_application_or_404(
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
    application = get_owned_application_or_404(
        session=session,
        application_id=application_id,
        current_user=current_user,
    )

    now = get_current_time()

    applied_at = application.applied_at

    if (
        status_update.status == ApplicationStatus.APPLIED
        and applied_at is None
    ):
        applied_at = now

    return application_repository.update_application_status(
        session=session,
        application=application,
        new_status=status_update.status,
        notes=status_update.notes,
        updated_at=now,
        applied_at=applied_at,
    )