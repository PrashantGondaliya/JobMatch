from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.db_models import CandidateProfileDB, JobApplicationDB, JobDB
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
    profile = session.get(CandidateProfileDB, application_data.profile_id)

    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    job = session.get(JobDB, application_data.job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    duplicate_statement = select(JobApplicationDB).where(
        JobApplicationDB.profile_id == application_data.profile_id,
        JobApplicationDB.job_id == application_data.job_id,
    )

    existing_application = session.exec(duplicate_statement).first()

    if existing_application is not None:
        raise HTTPException(
            status_code=400,
            detail="Application already exists for this profile and job",
        )

    now = get_current_time()

    applied_at = None

    if application_data.status == ApplicationStatus.APPLIED:
        applied_at = now

    new_application = JobApplicationDB(
        profile_id=application_data.profile_id,
        job_id=application_data.job_id,
        status=application_data.status.value,
        notes=application_data.notes,
        created_at=now,
        updated_at=now,
        applied_at=applied_at,
    )

    session.add(new_application)
    session.commit()
    session.refresh(new_application)

    return new_application


@router.get("", response_model=list[JobApplication])
def get_applications(session: Session = Depends(get_session)):
    statement = select(JobApplicationDB)
    applications = session.exec(statement).all()

    return applications


@router.get("/profile/{profile_id}", response_model=list[JobApplication])
def get_applications_for_profile(
    profile_id: int,
    session: Session = Depends(get_session),
):
    profile = session.get(CandidateProfileDB, profile_id)

    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    statement = select(JobApplicationDB).where(
        JobApplicationDB.profile_id == profile_id
    )

    applications = session.exec(statement).all()

    return applications


@router.get("/{application_id}", response_model=JobApplication)
def get_application(
    application_id: int,
    session: Session = Depends(get_session),
):
    application = session.get(JobApplicationDB, application_id)

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    return application


@router.patch("/{application_id}/status", response_model=JobApplication)
def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    session: Session = Depends(get_session),
):
    application = session.get(JobApplicationDB, application_id)

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    now = get_current_time()

    application.status = status_update.status.value
    application.notes = status_update.notes
    application.updated_at = now

    if (
        status_update.status == ApplicationStatus.APPLIED
        and application.applied_at is None
    ):
        application.applied_at = now

    session.add(application)
    session.commit()
    session.refresh(application)

    return application