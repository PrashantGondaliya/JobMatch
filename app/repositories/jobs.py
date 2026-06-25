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


def get_job_by_source_and_apply_url(
    session: Session,
    source: str,
    apply_url: str,
) -> JobDB | None:
    statement = select(JobDB).where(
        JobDB.source == source,
        JobDB.apply_url == apply_url,
    )

    return session.exec(statement).first()


def create_job_if_not_exists(
    session: Session,
    job_data: JobCreate,
) -> tuple[JobDB, bool]:
    existing_job = get_job_by_source_and_apply_url(
        session=session,
        source=job_data.source,
        apply_url=job_data.apply_url,
    )

    if existing_job is not None:
        return existing_job, False

    created_job = create_job(
        session=session,
        job_data=job_data,
    )

    return created_job, True