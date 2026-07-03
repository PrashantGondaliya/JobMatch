from sqlmodel import Session, select

from app.models.db_models import CandidateProfileDB
from app.schemas.profile import CandidateProfileCreate


def create_profile(
    session: Session,
    profile_data: CandidateProfileCreate,
    user_id: int,
) -> CandidateProfileDB:
    new_profile = CandidateProfileDB(
        user_id=user_id,
        **profile_data.model_dump(),
    )

    session.add(new_profile)
    session.commit()
    session.refresh(new_profile)

    return new_profile


def get_all_profiles(session: Session) -> list[CandidateProfileDB]:
    statement = select(CandidateProfileDB)
    return list(session.exec(statement).all())


def get_all_profiles_by_user_id(
    session: Session,
    user_id: int,
) -> list[CandidateProfileDB]:
    statement = select(CandidateProfileDB).where(
        CandidateProfileDB.user_id == user_id
    )

    return list(session.exec(statement).all())


def get_profile_by_id(
    session: Session,
    profile_id: int,
) -> CandidateProfileDB | None:
    return session.get(CandidateProfileDB, profile_id)


def get_profile_by_id_and_user_id(
    session: Session,
    profile_id: int,
    user_id: int,
) -> CandidateProfileDB | None:
    statement = select(CandidateProfileDB).where(
        CandidateProfileDB.id == profile_id,
        CandidateProfileDB.user_id == user_id,
    )

    return session.exec(statement).first()