from fastapi import APIRouter, HTTPException

from app.data.in_memory_db import jobs, profiles
from app.schemas.match import JobMatch
from app.services.matching import generate_job_matches


router = APIRouter(prefix="/matches", tags=["Matches"])


def find_profile_by_id(profile_id: int):
    for profile in profiles:
        if profile.id == profile_id:
            return profile

    return None


@router.get("/profile/{profile_id}", response_model=list[JobMatch])
def get_matches_for_profile(profile_id: int):
    profile = find_profile_by_id(profile_id=profile_id)

    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return generate_job_matches(profile=profile, jobs=jobs)