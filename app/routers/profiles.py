from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models.db_models import CandidateProfileDB
from app.schemas.profile import CandidateProfile, CandidateProfileCreate


router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.post("", response_model=CandidateProfile)
def create_profile(
    profile_data: CandidateProfileCreate,
    session: Session = Depends(get_session),
):
    new_profile = CandidateProfileDB(**profile_data.model_dump())

    session.add(new_profile)
    session.commit()
    session.refresh(new_profile)

    return new_profile


@router.get("", response_model=list[CandidateProfile])
def get_profiles(session: Session = Depends(get_session)):
    statement = select(CandidateProfileDB)
    profiles = session.exec(statement).all()

    return profiles


@router.get("/{profile_id}", response_model=CandidateProfile)
def get_profile(
    profile_id: int,
    session: Session = Depends(get_session),
):
    profile = session.get(CandidateProfileDB, profile_id)

    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile