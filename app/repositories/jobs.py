from sqlmodel import Session, select

from app.models.db_models import JobDB
from app.schemas.job import JobCreate


def create_job(
    session: Session,
    job_data: JobCreate,
) -> JobDB:
    new_job = JobDB(**job_data.model_dump())

    session.add(new_job)
    session.commit()
    session.refresh(new_job)

    return new_job


def get_all_jobs(session: Session) -> list[JobDB]:
    statement = select(JobDB)
    return list(session.exec(statement).all())


def get_job_by_id(
    session: Session,
    job_id: int,
) -> JobDB | None:
    return session.get(JobDB, job_id)