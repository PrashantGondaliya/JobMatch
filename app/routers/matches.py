from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.database import get_session
from app.repositories import jobs as job_repository
from app.repositories import profiles as profile_repository
from app.schemas.job import Job
from app.schemas.match import JobMatch, MatchRefreshSummary, StoredJobMatch
from app.schemas.profile import CandidateProfile
from app.services.match_persistence import (
    get_saved_matches_for_profile,
    refresh_matches_for_profile,
)
from app.services.matching import generate_job_matches


router = APIRouter(prefix="/matches", tags=["Matches"])


@router.post(
    "/profile/{profile_id}/refresh",
    response_model=MatchRefreshSummary,
)
def refresh_profile_matches(
    profile_id: int,
    session: Session = Depends(get_session),
):
    summary = refresh_matches_for_profile(
        session=session,
        profile_id=profile_id,
    )

    if summary is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return summary


@router.get(
    "/profile/{profile_id}/saved",
    response_model=list[StoredJobMatch],
)
def get_saved_profile_matches(
    profile_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    profile_db = profile_repository.get_profile_by_id(
        session=session,
        profile_id=profile_id,
    )

    if profile_db is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return get_saved_matches_for_profile(
        session=session,
        profile_id=profile_id,
        limit=limit,
    )


@router.get("/profile/{profile_id}", response_model=list[JobMatch])
def get_live_matches_for_profile(
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