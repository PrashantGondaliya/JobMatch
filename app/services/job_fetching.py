from datetime import datetime, timezone

from sqlmodel import Session

from app.connectors.greenhouse import fetch_greenhouse_jobs
from app.models.db_models import JobSourceDB
from app.repositories import job_sources as job_source_repository
from app.repositories import jobs as job_repository
from app.schemas.job import Job
from app.schemas.job_source import JobFetchSummary, JobSourceType


class UnsupportedJobSourceError(Exception):
    pass


def get_current_time() -> datetime:
    return datetime.now(timezone.utc)


def fetch_greenhouse_jobs_into_database(
    session: Session,
    company_slug: str,
) -> JobFetchSummary:
    fetched_jobs = fetch_greenhouse_jobs(company_slug=company_slug)

    created_jobs = []
    skipped_count = 0

    for job_data in fetched_jobs:
        job, was_created = job_repository.create_job_if_not_exists(
            session=session,
            job_data=job_data,
        )

        if was_created:
            created_jobs.append(Job.model_validate(job))
        else:
            skipped_count += 1

    return JobFetchSummary(
        source_type=JobSourceType.GREENHOUSE,
        company_slug=company_slug,
        fetched_count=len(fetched_jobs),
        created_count=len(created_jobs),
        skipped_count=skipped_count,
        created_jobs=created_jobs,
    )


def fetch_jobs_for_source(
    session: Session,
    job_source: JobSourceDB,
) -> JobFetchSummary:
    if job_source.source_type != JobSourceType.GREENHOUSE.value:
        raise UnsupportedJobSourceError(
            f"Unsupported job source type: {job_source.source_type}"
        )

    summary = fetch_greenhouse_jobs_into_database(
        session=session,
        company_slug=job_source.company_slug,
    )

    job_source_repository.update_last_fetched_at(
        session=session,
        job_source=job_source,
        fetched_at=get_current_time(),
    )

    return summary