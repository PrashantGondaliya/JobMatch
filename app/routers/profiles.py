from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.dependencies.auth import get_current_user
from app.models.db_models import UserDB
from app.repositories import profiles as profile_repository
from app.schemas.profile import CandidateProfile, CandidateProfileCreate
from app.services.ownership import get_owned_profile_or_404, get_user_id


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
        user_id=get_user_id(current_user),
    )


@router.get("", response_model=list[CandidateProfile])
def get_profiles(
    session: Session = Depends(get_session),
    current_user: UserDB = Depends(get_current_user),
):
    return profile_repository.get_all_profiles_by_user_id(
        session=session,
        user_id=get_user_id(current_user),
    )


@router.get("/{profile_id}", response_model=CandidateProfile)
def get_profile(
    profile_id: int,
    session: Session = Depends(get_session),
    current_user: UserDB = Depends(get_current_user),
):
    return get_owned_profile_or_404(
        session=session,
        profile_id=profile_id,
        current_user=current_user,
    )