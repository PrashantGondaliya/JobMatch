from sqlmodel import Session

from app.core.errors import internal_server_error, not_found
from app.models.db_models import CandidateProfileDB, JobApplicationDB, UserDB
from app.repositories import applications as application_repository
from app.repositories import profiles as profile_repository


def get_user_id(current_user: UserDB) -> int:
    if current_user.id is None:
        raise internal_server_error("Authenticated user has no ID")

    return current_user.id


def get_owned_profile_or_404(
    session: Session,
    profile_id: int,
    current_user: UserDB,
) -> CandidateProfileDB:
    user_id = get_user_id(current_user)

    profile = profile_repository.get_profile_by_id_and_user_id(
        session=session,
        profile_id=profile_id,
        user_id=user_id,
    )

    if profile is None:
        raise not_found("Profile")

    return profile


def get_current_user_profile_ids(
    session: Session,
    current_user: UserDB,
) -> list[int]:
    user_id = get_user_id(current_user)

    profiles = profile_repository.get_all_profiles_by_user_id(
        session=session,
        user_id=user_id,
    )

    return [
        profile.id
        for profile in profiles
        if profile.id is not None
    ]


def get_owned_application_or_404(
    session: Session,
    application_id: int,
    current_user: UserDB,
) -> JobApplicationDB:
    application = application_repository.get_application_by_id(
        session=session,
        application_id=application_id,
    )

    if application is None:
        raise not_found("Application")

    profile_ids = get_current_user_profile_ids(
        session=session,
        current_user=current_user,
    )

    if application.profile_id not in profile_ids:
        raise not_found("Application")

    return application