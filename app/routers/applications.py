from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.repositories import applications as application_repository
from app.repositories import jobs as job_repository
from app.repositories import profiles as profile_repository
from app.schemas.application import (
    ApplicationCreate,
    ApplicationStatus,
    ApplicationStatusUpdate,
    JobApplication,
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
):
    profile = profile_repository.get_profile_by_id(
        session=session,
        profile_id=application_data.profile_id,
    )

    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    job = job_repository.get_job_by_id(
        session=session,
        job_id=application_data.job_id,
    )

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    existing_application = application_repository.get_application_by_profile_and_job(
        session=session,
        profile_id=application_data.profile_id,
        job_id=application_data.job_id,
    )

    if existing_application is not None:
        raise HTTPException(
            status_code=400,
            detail="Application already exists for this profile and job",
        )

    applied_at = None

    if application_data.status == ApplicationStatus.APPLIED:
        applied_at = get_current_time()

    return application_repository.create_application(
        session=session,
        application_data=application_data,
        applied_at=applied_at,
    )


@router.get("", response_model=list[JobApplication])
def get_applications(session: Session = Depends(get_session)):
    return application_repository.get_all_applications(session=session)


@router.get("/profile/{profile_id}", response_model=list[JobApplication])
def get_applications_for_profile(
    profile_id: int,
    session: Session = Depends(get_session),
):
    profile = profile_repository.get_profile_by_id(
        session=session,
        profile_id=profile_id,
    )

    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return application_repository.get_applications_by_profile_id(
        session=session,
        profile_id=profile_id,
    )


@router.get("/{application_id}", response_model=JobApplication)
def get_application(
    application_id: int,
    session: Session = Depends(get_session),
):
    application = application_repository.get_application_by_id(
        session=session,
        application_id=application_id,
    )

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    return application


@router.patch("/{application_id}/status", response_model=JobApplication)
def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    session: Session = Depends(get_session),
):
    application = application_repository.get_application_by_id(
        session=session,
        application_id=application_id,
    )

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

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