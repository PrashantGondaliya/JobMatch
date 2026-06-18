from datetime import datetime

from sqlmodel import Session, select

from app.models.db_models import JobApplicationDB
from app.schemas.application import ApplicationCreate, ApplicationStatus


def create_application(
    session: Session,
    application_data: ApplicationCreate,
    applied_at: datetime | None = None,
) -> JobApplicationDB:
    new_application = JobApplicationDB(
        profile_id=application_data.profile_id,
        job_id=application_data.job_id,
        status=application_data.status.value,
        notes=application_data.notes,
        applied_at=applied_at,
    )

    session.add(new_application)
    session.commit()
    session.refresh(new_application)

    return new_application


def get_all_applications(session: Session) -> list[JobApplicationDB]:
    statement = select(JobApplicationDB)
    return list(session.exec(statement).all())


def get_application_by_id(
    session: Session,
    application_id: int,
) -> JobApplicationDB | None:
    return session.get(JobApplicationDB, application_id)


def get_applications_by_profile_id(
    session: Session,
    profile_id: int,
) -> list[JobApplicationDB]:
    statement = select(JobApplicationDB).where(
        JobApplicationDB.profile_id == profile_id
    )

    return list(session.exec(statement).all())


def get_application_by_profile_and_job(
    session: Session,
    profile_id: int,
    job_id: int,
) -> JobApplicationDB | None:
    statement = select(JobApplicationDB).where(
        JobApplicationDB.profile_id == profile_id,
        JobApplicationDB.job_id == job_id,
    )

    return session.exec(statement).first()


def update_application_status(
    session: Session,
    application: JobApplicationDB,
    new_status: ApplicationStatus,
    notes: str | None,
    updated_at: datetime,
    applied_at: datetime | None,
) -> JobApplicationDB:
    application.status = new_status.value
    application.notes = notes
    application.updated_at = updated_at
    application.applied_at = applied_at

    session.add(application)
    session.commit()
    session.refresh(application)

    return application