from sqlmodel import Session, select

from app.models.db_models import JobDB
from app.schemas.job import JobCreate


def normalize_text(value: str) -> str:
    return value.strip().lower()


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


def job_matches_filters(
    job: JobDB,
    location: str | None = None,
    skill: str | None = None,
    remote_type: str | None = None,
    source: str | None = None,
    company: str | None = None,
    title: str | None = None,
) -> bool:
    if location is not None:
        location_filter = normalize_text(location)
        job_location = normalize_text(job.location)

        if location_filter not in job_location:
            return False

    if skill is not None:
        skill_filter = normalize_text(skill)

        normalized_required_skills = [
            normalize_text(required_skill)
            for required_skill in job.required_skills
        ]

        has_matching_skill = any(
            skill_filter in required_skill
            or required_skill in skill_filter
            for required_skill in normalized_required_skills
        )

        if not has_matching_skill:
            return False

    if remote_type is not None:
        remote_filter = normalize_text(remote_type)
        job_remote_type = normalize_text(job.remote_type)

        if remote_filter != job_remote_type:
            return False

    if source is not None:
        source_filter = normalize_text(source)
        job_source = normalize_text(job.source)

        if source_filter not in job_source:
            return False

    if company is not None:
        company_filter = normalize_text(company)
        job_company = normalize_text(job.company)

        if company_filter not in job_company:
            return False

    if title is not None:
        title_filter = normalize_text(title)
        job_title = normalize_text(job.title)

        if title_filter not in job_title:
            return False

    return True


def get_filtered_jobs(
    session: Session,
    limit: int,
    offset: int,
    location: str | None = None,
    skill: str | None = None,
    remote_type: str | None = None,
    source: str | None = None,
    company: str | None = None,
    title: str | None = None,
) -> tuple[list[JobDB], int]:
    all_jobs = get_all_jobs(session=session)

    filtered_jobs = [
        job
        for job in all_jobs
        if job_matches_filters(
            job=job,
            location=location,
            skill=skill,
            remote_type=remote_type,
            source=source,
            company=company,
            title=title,
        )
    ]

    total_count = len(filtered_jobs)

    paginated_jobs = filtered_jobs[offset: offset + limit]

    return paginated_jobs, total_count