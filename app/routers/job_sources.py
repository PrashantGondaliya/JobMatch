from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.connectors.greenhouse import GreenhouseConnectorError
from app.database import get_session
from app.repositories import job_sources as job_source_repository
from app.schemas.job_source import (
    JobFetchSummary,
    JobSource,
    JobSourceCreate,
    JobSourceUpdate,
)
from app.services.job_fetching import (
    UnsupportedJobSourceError,
    fetch_jobs_for_source,
)


from app.dependencies.auth import require_admin_user

router = APIRouter(
    prefix="/job-sources",
    tags=["Job Sources"],
    dependencies=[Depends(require_admin_user)],
)


def get_current_time() -> datetime:
    return datetime.now(timezone.utc)


@router.post("", response_model=JobSource, status_code=status.HTTP_201_CREATED)
def create_job_source(
    source_data: JobSourceCreate,
    session: Session = Depends(get_session),
):
    existing_source = job_source_repository.get_job_source_by_type_and_slug(
        session=session,
        source_type=source_data.source_type.value,
        company_slug=source_data.company_slug,
    )

    if existing_source is not None:
        raise HTTPException(
            status_code=400,
            detail="Job source already exists",
        )

    return job_source_repository.create_job_source(
        session=session,
        source_data=source_data,
    )


@router.post("/fetch-active")
def fetch_all_active_job_sources(
    session: Session = Depends(get_session),
):
    active_sources = job_source_repository.get_active_job_sources(
        session=session,
    )

    results = []
    errors = []

    for job_source in active_sources:
        try:
            summary = fetch_jobs_for_source(
                session=session,
                job_source=job_source,
            )

            results.append(summary)

        except (GreenhouseConnectorError, UnsupportedJobSourceError) as error:
            errors.append(
                {
                    "source_id": job_source.id,
                    "source_type": job_source.source_type,
                    "company_slug": job_source.company_slug,
                    "error": str(error),
                }
            )

    return {
        "total_active_sources": len(active_sources),
        "successful_sources": len(results),
        "failed_sources": len(errors),
        "results": results,
        "errors": errors,
    }


@router.get("", response_model=list[JobSource])
def get_job_sources(session: Session = Depends(get_session)):
    return job_source_repository.get_all_job_sources(session=session)


@router.get("/{source_id}", response_model=JobSource)
def get_job_source(
    source_id: int,
    session: Session = Depends(get_session),
):
    job_source = job_source_repository.get_job_source_by_id(
        session=session,
        source_id=source_id,
    )

    if job_source is None:
        raise HTTPException(status_code=404, detail="Job source not found")

    return job_source


@router.patch("/{source_id}", response_model=JobSource)
def update_job_source(
    source_id: int,
    source_update: JobSourceUpdate,
    session: Session = Depends(get_session),
):
    job_source = job_source_repository.get_job_source_by_id(
        session=session,
        source_id=source_id,
    )

    if job_source is None:
        raise HTTPException(status_code=404, detail="Job source not found")

    return job_source_repository.update_job_source(
        session=session,
        job_source=job_source,
        source_update=source_update,
        updated_at=get_current_time(),
    )


@router.post("/{source_id}/fetch", response_model=JobFetchSummary)
def fetch_single_job_source(
    source_id: int,
    session: Session = Depends(get_session),
):
    job_source = job_source_repository.get_job_source_by_id(
        session=session,
        source_id=source_id,
    )

    if job_source is None:
        raise HTTPException(status_code=404, detail="Job source not found")

    try:
        return fetch_jobs_for_source(
            session=session,
            job_source=job_source,
        )

    except UnsupportedJobSourceError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    except GreenhouseConnectorError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error