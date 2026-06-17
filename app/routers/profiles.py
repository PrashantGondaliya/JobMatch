from fastapi import APIRouter, HTTPException

from app.data.in_memory_db import profiles
from app.schemas.profile import CandidateProfile, CandidateProfileCreate


router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.post("", response_model=CandidateProfile)
def create_profile(profile_data: CandidateProfileCreate):
    new_profile = CandidateProfile(
        id=len(profiles) + 1,
        **profile_data.model_dump()
    )

    profiles.append(new_profile)

    return new_profile


@router.get("", response_model=list[CandidateProfile])
def get_profiles():
    return profiles


@router.get("/{profile_id}", response_model=CandidateProfile)
def get_profile(profile_id: int):
    for profile in profiles:
        if profile.id == profile_id:
            return profile

    raise HTTPException(status_code=404, detail="Profile not found")