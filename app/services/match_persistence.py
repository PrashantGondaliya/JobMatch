from datetime import datetime, timezone

from sqlmodel import Session

from app.repositories import job_matches as job_match_repository
from app.repositories import jobs as job_repository
from app.repositories import profiles as profile_repository
from app.schemas.job import Job
from app.schemas.match import MatchRefreshSummary, StoredJobMatch
from app.schemas.profile import CandidateProfile
from app.services.matching import generate_job_matches


def get_current_time() -> datetime:
    return datetime.now(timezone.utc)


def refresh_matches_for_profile(
    session: Session,
    profile_id: int,
) -> MatchRefreshSummary | None:
    profile_db = profile_repository.get_profile_by_id(
        session=session,
        profile_id=profile_id,
    )

    if profile_db is None:
        return None

    jobs_db = job_repository.get_all_jobs(session=session)

    profile = CandidateProfile.model_validate(profile_db)

    jobs = [
        Job.model_validate(job_db)
        for job_db in jobs_db
    ]

    live_matches = generate_job_matches(
        profile=profile,
        jobs=jobs,
    )

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

    return MatchRefreshSummary(
        profile_id=profile_id,
        total_jobs_checked=len(jobs),
        matches_saved=len(saved_matches),
        top_matches=saved_matches[:10],
    )


def get_saved_matches_for_profile(
    session: Session,
    profile_id: int,
    limit: int = 50,
) -> list[StoredJobMatch]:
    matches_db = job_match_repository.get_matches_by_profile_id(
        session=session,
        profile_id=profile_id,
        limit=limit,
    )

    return [
        StoredJobMatch.model_validate(match_db)
        for match_db in matches_db
    ]