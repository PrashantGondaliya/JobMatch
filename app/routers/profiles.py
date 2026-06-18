from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.repositories import profiles as profile_repository
from app.schemas.profile import CandidateProfile, CandidateProfileCreate


router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.post("", response_model=CandidateProfile)
def create_profile(
    profile_data: CandidateProfileCreate,
    session: Session = Depends(get_session),
):
    return profile_repository.create_profile(
        session=session,
        profile_data=profile_data,
    )


@router.get("", response_model=list[CandidateProfile])
def get_profiles(session: Session = Depends(get_session)):
    return profile_repository.get_all_profiles(session=session)


@router.get("/{profile_id}", response_model=CandidateProfile)
def get_profile(
    profile_id: int,
    session: Session = Depends(get_session),
):
    profile = profile_repository.get_profile_by_id(
        session=session,
        profile_id=profile_id,
    )

    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile