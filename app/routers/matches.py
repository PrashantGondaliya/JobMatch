from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.repositories import jobs as job_repository
from app.repositories import profiles as profile_repository
from app.schemas.job import Job
from app.schemas.match import JobMatch
from app.schemas.profile import CandidateProfile
from app.services.matching import generate_job_matches


router = APIRouter(prefix="/matches", tags=["Matches"])


@router.get("/profile/{profile_id}", response_model=list[JobMatch])
def get_matches_for_profile(
    profile_id: int,
    session: Session = Depends(get_session),
):
    profile_db = profile_repository.get_profile_by_id(
        session=session,
        profile_id=profile_id,
    )

    if profile_db is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    jobs_db = job_repository.get_all_jobs(session=session)

    profile = CandidateProfile.model_validate(profile_db)

    jobs = [
        Job.model_validate(job_db)
        for job_db in jobs_db
    ]

    return generate_job_matches(profile=profile, jobs=jobs)