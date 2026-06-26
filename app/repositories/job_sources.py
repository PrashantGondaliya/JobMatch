from datetime import datetime

from sqlmodel import Session, select

from app.models.db_models import JobSourceDB
from app.schemas.job_source import JobSourceCreate, JobSourceUpdate


def normalize_company_slug(company_slug: str) -> str:
    return company_slug.strip().lower()


def build_display_name(company_slug: str) -> str:
    return company_slug.replace("-", " ").replace("_", " ").title()


def create_job_source(
    session: Session,
    source_data: JobSourceCreate,
) -> JobSourceDB:
    company_slug = normalize_company_slug(source_data.company_slug)

    display_name = source_data.display_name

    if display_name is None:
        display_name = build_display_name(company_slug)

    new_source = JobSourceDB(
        source_type=source_data.source_type.value,
        company_slug=company_slug,
        display_name=display_name,
        is_active=source_data.is_active,
    )

    session.add(new_source)
    session.commit()
    session.refresh(new_source)

    return new_source


def get_all_job_sources(session: Session) -> list[JobSourceDB]:
    statement = select(JobSourceDB)
    return list(session.exec(statement).all())


def get_active_job_sources(session: Session) -> list[JobSourceDB]:
    statement = select(JobSourceDB).where(JobSourceDB.is_active == True)  # noqa: E712
    return list(session.exec(statement).all())


def get_job_source_by_id(
    session: Session,
    source_id: int,
) -> JobSourceDB | None:
    return session.get(JobSourceDB, source_id)


def get_job_source_by_type_and_slug(
    session: Session,
    source_type: str,
    company_slug: str,
) -> JobSourceDB | None:
    normalized_slug = normalize_company_slug(company_slug)

    statement = select(JobSourceDB).where(
        JobSourceDB.source_type == source_type,
        JobSourceDB.company_slug == normalized_slug,
    )

    return session.exec(statement).first()


def update_job_source(
    session: Session,
    job_source: JobSourceDB,
    source_update: JobSourceUpdate,
    updated_at: datetime,
) -> JobSourceDB:
    if source_update.display_name is not None:
        job_source.display_name = source_update.display_name

    if source_update.is_active is not None:
        job_source.is_active = source_update.is_active

    job_source.updated_at = updated_at

    session.add(job_source)
    session.commit()
    session.refresh(job_source)

    return job_source


def update_last_fetched_at(
    session: Session,
    job_source: JobSourceDB,
    fetched_at: datetime,
) -> JobSourceDB:
    job_source.last_fetched_at = fetched_at
    job_source.updated_at = fetched_at

    session.add(job_source)
    session.commit()
    session.refresh(job_source)

    return job_source