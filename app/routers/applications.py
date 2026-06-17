from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from app.data.in_memory_db import applications, jobs, profiles
from app.schemas.application import (
    ApplicationCreate,
    ApplicationStatus,
    ApplicationStatusUpdate,
    JobApplication,
)


router = APIRouter(prefix="/applications", tags=["Applications"])


def get_current_time() -> datetime:
    return datetime.now(timezone.utc)


def find_profile_by_id(profile_id: int):
    for profile in profiles:
        if profile.id == profile_id:
            return profile

    return None


def find_job_by_id(job_id: int):
    for job in jobs:
        if job.id == job_id:
            return job

    return None


def find_application_by_id(application_id: int):
    for application in applications:
        if application.id == application_id:
            return application

    return None


def application_already_exists(profile_id: int, job_id: int) -> bool:
    for application in applications:
        if application.profile_id == profile_id and application.job_id == job_id:
            return True

    return False


@router.post(
    "",
    response_model=JobApplication,
    status_code=status.HTTP_201_CREATED,
)
def create_application(application_data: ApplicationCreate):
    profile = find_profile_by_id(application_data.profile_id)

    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    job = find_job_by_id(application_data.job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if application_already_exists(
        profile_id=application_data.profile_id,
        job_id=application_data.job_id,
    ):
        raise HTTPException(
            status_code=400,
            detail="Application already exists for this profile and job",
        )

    now = get_current_time()

    applied_at = None

    if application_data.status == ApplicationStatus.APPLIED:
        applied_at = now

    new_application = JobApplication(
        id=len(applications) + 1,
        profile_id=application_data.profile_id,
        job_id=application_data.job_id,
        status=application_data.status,
        notes=application_data.notes,
        created_at=now,
        updated_at=now,
        applied_at=applied_at,
    )

    applications.append(new_application)

    return new_application


@router.get("", response_model=list[JobApplication])
def get_applications():
    return applications


@router.get("/{application_id}", response_model=JobApplication)
def get_application(application_id: int):
    application = find_application_by_id(application_id)

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    return application


@router.get("/profile/{profile_id}", response_model=list[JobApplication])
def get_applications_for_profile(profile_id: int):
    profile = find_profile_by_id(profile_id)

    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return [
        application
        for application in applications
        if application.profile_id == profile_id
    ]


@router.patch("/{application_id}/status", response_model=JobApplication)
def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
):
    application = find_application_by_id(application_id)

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    now = get_current_time()

    applied_at = application.applied_at

    if (
        status_update.status == ApplicationStatus.APPLIED
        and applied_at is None
    ):
        applied_at = now

    updated_application = application.model_copy(
        update={
            "status": status_update.status,
            "notes": status_update.notes,
            "updated_at": now,
            "applied_at": applied_at,
        }
    )

    for index, existing_application in enumerate(applications):
        if existing_application.id == application_id:
            applications[index] = updated_application
            break

    return updated_application