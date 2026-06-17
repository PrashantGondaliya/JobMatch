from fastapi import APIRouter, HTTPException, status

from app.data.in_memory_db import jobs
from app.schemas.job import Job, JobCreate


router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("", response_model=Job, status_code=status.HTTP_201_CREATED)
def create_job(job_data: JobCreate):
    new_job = Job(
        id=len(jobs) + 1,
        **job_data.model_dump()
    )

    jobs.append(new_job)

    return new_job


@router.get("", response_model=list[Job])
def get_jobs():
    return jobs


@router.get("/{job_id}", response_model=Job)
def get_job(job_id: int):
    for job in jobs:
        if job.id == job_id:
            return job

    raise HTTPException(status_code=404, detail="Job not found")