from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.dependencies.auth import get_current_user
from app.models.db_models import UserDB
from app.repositories import profiles as profile_repository
from app.schemas.profile import CandidateProfile, CandidateProfileCreate


router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.post("", response_model=CandidateProfile)
def create_profile(
    profile_data: CandidateProfileCreate,
    session: Session = Depends(get_session),
    current_user: UserDB = Depends(get_current_user),
):
    return profile_repository.create_profile(
        session=session,
        profile_data=profile_data,
        user_id=current_user.id,
    )


@router.get("", response_model=list[CandidateProfile])
def get_profiles(
    session: Session = Depends(get_session),
    current_user: UserDB = Depends(get_current_user),
):
    return profile_repository.get_all_profiles_by_user_id(
        session=session,
        user_id=current_user.id,
    )


@router.get("/{profile_id}", response_model=CandidateProfile)
def get_profile(
    profile_id: int,
    session: Session = Depends(get_session),
    current_user: UserDB = Depends(get_current_user),
):
    profile = profile_repository.get_profile_by_id_and_user_id(
        session=session,
        profile_id=profile_id,
        user_id=current_user.id,
    )

    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile