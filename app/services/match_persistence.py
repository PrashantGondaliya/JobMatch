from datetime import datetime, timezone

from sqlmodel import Session

from app.models.db_models import CandidateProfileDB, UserDB
from app.repositories import job_matches as job_match_repository
from app.repositories import jobs as job_repository
from app.schemas.job import Job
from app.schemas.match import (
    JobMatch,
    MatchRefreshSummary,
    StoredJobMatch,
    StoredJobMatchListResponse,
)
from app.schemas.profile import CandidateProfile
from app.services.matching import generate_job_matches
from app.services.ownership import get_owned_profile_or_404


def get_current_time() -> datetime:
    return datetime.now(timezone.utc)


def convert_profile_db_to_schema(
    profile_db: CandidateProfileDB,
) -> CandidateProfile:
    return CandidateProfile.model_validate(profile_db)


def get_all_jobs_as_schemas(session: Session) -> list[Job]:
    jobs_db = job_repository.get_all_jobs(session=session)

    return [
        Job.model_validate(job_db)
        for job_db in jobs_db
    ]


def filter_matches_by_min_score(
    matches: list[JobMatch],
    min_score: float | None,
) -> list[JobMatch]:
    if min_score is None:
        return matches

    return [
        match
        for match in matches
        if match.match_percentage >= min_score
    ]


def paginate_matches(
    matches: list[JobMatch],
    limit: int,
    offset: int,
) -> list[JobMatch]:
    return matches[offset: offset + limit]


def generate_live_matches_for_user_profile(
    session: Session,
    profile_id: int,
    current_user: UserDB,
    limit: int,
    offset: int,
    min_score: float | None = None,
) -> list[JobMatch]:
    profile_db = get_owned_profile_or_404(
        session=session,
        profile_id=profile_id,
        current_user=current_user,
    )

    profile = convert_profile_db_to_schema(profile_db)
    jobs = get_all_jobs_as_schemas(session=session)

    live_matches = generate_job_matches(
        profile=profile,
        jobs=jobs,
    )

    filtered_matches = filter_matches_by_min_score(
        matches=live_matches,
        min_score=min_score,
    )

    return paginate_matches(
        matches=filtered_matches,
        limit=limit,
        offset=offset,
    )


def save_matches_for_profile(
    session: Session,
    profile_id: int,
    live_matches: list[JobMatch],
) -> list[StoredJobMatch]:
    saved_matches = []

    now = get_current_time()

    for match in live_matches:
        saved_match = job_match_repository.create_or_update_job_match(
            session=session,
            profile_id=profile_id,
            match=match,
            updated_at=now,
        )

        saved_matches.append(
            StoredJobMatch.model_validate(saved_match)
        )

    saved_matches.sort(
        key=lambda match: match.match_percentage,
        reverse=True,
    )

    return saved_matches


def refresh_matches_for_user_profile(
    session: Session,
    profile_id: int,
    current_user: UserDB,
) -> MatchRefreshSummary:
    profile_db = get_owned_profile_or_404(
        session=session,
        profile_id=profile_id,
        current_user=current_user,
    )

    profile = convert_profile_db_to_schema(profile_db)
    jobs = get_all_jobs_as_schemas(session=session)

    live_matches = generate_job_matches(
        profile=profile,
        jobs=jobs,
    )

    saved_matches = save_matches_for_profile(
        session=session,
        profile_id=profile_id,
        live_matches=live_matches,
    )

    return MatchRefreshSummary(
        profile_id=profile_id,
        total_jobs_checked=len(jobs),
        matches_saved=len(saved_matches),
        top_matches=saved_matches[:10],
    )


def get_saved_matches_for_user_profile(
    session: Session,
    profile_id: int,
    current_user: UserDB,
    limit: int = 50,
    offset: int = 0,
    min_score: float | None = None,
) -> StoredJobMatchListResponse:
    get_owned_profile_or_404(
        session=session,
        profile_id=profile_id,
        current_user=current_user,
    )

    matches_db, total_count = job_match_repository.get_filtered_matches_by_profile_id(
        session=session,
        profile_id=profile_id,
        limit=limit,
        offset=offset,
        min_score=min_score,
    )

    items = [
        StoredJobMatch.model_validate(match_db)
        for match_db in matches_db
    ]

    return StoredJobMatchListResponse(
        items=items,
        total_count=total_count,
        returned_count=len(items),
        limit=limit,
        offset=offset,
        min_score=min_score,
    )