from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.repositories import jobs as job_repository
from app.schemas.job import Job, JobCreate


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