from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.connectors.greenhouse import GreenhouseConnectorError
from app.database import get_session
from app.repositories import jobs as job_repository
from app.schemas.job import Job, JobCreate
from app.schemas.job_source import JobFetchSummary
from app.services.job_fetching import fetch_greenhouse_jobs_into_database


router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("", response_model=Job, status_code=status.HTTP_201_CREATED)
def create_job(
    job_data: JobCreate,
    session: Session = Depends(get_session),
):
    return job_repository.create_job(
        session=session,
        job_data=job_data,
    )


@router.post(
    "/fetch/greenhouse/{company_slug}",
    response_model=JobFetchSummary,
)
def fetch_jobs_from_greenhouse(
    company_slug: str,
    session: Session = Depends(get_session),
):
    try:
        return fetch_greenhouse_jobs_into_database(
            session=session,
            company_slug=company_slug,
        )

    except GreenhouseConnectorError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error


@router.get("", response_model=list[Job])
def get_jobs(session: Session = Depends(get_session)):
    return job_repository.get_all_jobs(session=session)


@router.get("/{job_id}", response_model=Job)
def get_job(
    job_id: int,
    session: Session = Depends(get_session),
):
    job = job_repository.get_job_by_id(
        session=session,
        job_id=job_id,
    )

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return job