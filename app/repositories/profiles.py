from sqlmodel import Session, select

from app.models.db_models import CandidateProfileDB
from app.schemas.profile import CandidateProfileCreate


def create_profile(
    session: Session,
    profile_data: CandidateProfileCreate,
) -> CandidateProfileDB:
    new_profile = CandidateProfileDB(**profile_data.model_dump())

    session.add(new_profile)
    session.commit()
    session.refresh(new_profile)

    return new_profile


def get_all_profiles(session: Session) -> list[CandidateProfileDB]:
    statement = select(CandidateProfileDB)
    return list(session.exec(statement).all())


def get_profile_by_id(
    session: Session,
    profile_id: int,
) -> CandidateProfileDB | None:
    return session.get(CandidateProfileDB, profile_id)