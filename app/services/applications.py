from datetime import datetime, timezone

from sqlmodel import Session

from app.core.errors import bad_request, not_found
from app.models.db_models import JobApplicationDB, UserDB
from app.repositories import applications as application_repository
from app.repositories import jobs as job_repository
from app.schemas.application import (
    ApplicationCreate,
    ApplicationStatus,
    ApplicationStatusUpdate,
)
from app.services.ownership import (
    get_current_user_profile_ids,
    get_owned_application_or_404,
    get_owned_profile_or_404,
)


def get_current_time() -> datetime:
    return datetime.now(timezone.utc)


def create_application_for_user(
    session: Session,
    application_data: ApplicationCreate,
    current_user: UserDB,
) -> JobApplicationDB:
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


def get_applications_for_user(
    session: Session,
    current_user: UserDB,
) -> list[JobApplicationDB]:
    profile_ids = get_current_user_profile_ids(
        session=session,
        current_user=current_user,
    )

    return application_repository.get_applications_by_profile_ids(
        session=session,
        profile_ids=profile_ids,
    )


def get_applications_for_user_profile(
    session: Session,
    profile_id: int,
    current_user: UserDB,
) -> list[JobApplicationDB]:
    get_owned_profile_or_404(
        session=session,
        profile_id=profile_id,
        current_user=current_user,
    )

    return application_repository.get_applications_by_profile_id(
        session=session,
        profile_id=profile_id,
    )


def get_application_for_user(
    session: Session,
    application_id: int,
    current_user: UserDB,
) -> JobApplicationDB:
    return get_owned_application_or_404(
        session=session,
        application_id=application_id,
        current_user=current_user,
    )


def update_application_status_for_user(
    session: Session,
    application_id: int,
    status_update: ApplicationStatusUpdate,
    current_user: UserDB,
) -> JobApplicationDB:
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