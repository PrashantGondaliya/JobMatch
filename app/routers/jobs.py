from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.db_models import JobDB
from app.schemas.job import Job, JobCreate


router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("", response_model=Job, status_code=status.HTTP_201_CREATED)
def create_job(
    job_data: JobCreate,
    session: Session = Depends(get_session),
):
    new_job = JobDB(**job_data.model_dump())

    session.add(new_job)
    session.commit()
    session.refresh(new_job)

    return new_job


@router.get("", response_model=list[Job])
def get_jobs(session: Session = Depends(get_session)):
    statement = select(JobDB)
    jobs = session.exec(statement).all()

    return jobs


@router.get("/{job_id}", response_model=Job)
def get_job(
    job_id: int,
    session: Session = Depends(get_session),
):
    job = session.get(JobDB, job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return job