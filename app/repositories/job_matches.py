from datetime import datetime

from sqlmodel import Session, select

from app.models.db_models import JobMatchDB
from app.schemas.match import JobMatch


def get_match_by_profile_and_job(
    session: Session,
    profile_id: int,
    job_id: int,
) -> JobMatchDB | None:
    statement = select(JobMatchDB).where(
        JobMatchDB.profile_id == profile_id,
        JobMatchDB.job_id == job_id,
    )

    return session.exec(statement).first()


def create_or_update_job_match(
    session: Session,
    profile_id: int,
    match: JobMatch,
    updated_at: datetime,
) -> JobMatchDB:
    existing_match = get_match_by_profile_and_job(
        session=session,
        profile_id=profile_id,
        job_id=match.job_id,
    )

    if existing_match is None:
        new_match = JobMatchDB(
            profile_id=profile_id,
            job_id=match.job_id,
            job_title=match.title,
            company=match.company,
            location=match.location,
            apply_url=match.apply_url,
            match_percentage=match.match_percentage,
            skill_score=match.score_breakdown.skill_score,
            location_score=match.score_breakdown.location_score,
            remote_score=match.score_breakdown.remote_score,
            salary_score=match.score_breakdown.salary_score,
            matched_skills=match.matched_skills,
            missing_skills=match.missing_skills,
            required_skills=match.required_skills,
            match_reasons=match.match_reasons,
            concerns=match.concerns,
            explanation=match.explanation,
            updated_at=updated_at,
        )

        session.add(new_match)
        session.commit()
        session.refresh(new_match)

        return new_match

    existing_match.job_title = match.title
    existing_match.company = match.company
    existing_match.location = match.location
    existing_match.apply_url = match.apply_url

    existing_match.match_percentage = match.match_percentage

    existing_match.skill_score = match.score_breakdown.skill_score
    existing_match.location_score = match.score_breakdown.location_score
    existing_match.remote_score = match.score_breakdown.remote_score
    existing_match.salary_score = match.score_breakdown.salary_score

    existing_match.matched_skills = match.matched_skills
    existing_match.missing_skills = match.missing_skills
    existing_match.required_skills = match.required_skills

    existing_match.match_reasons = match.match_reasons
    existing_match.concerns = match.concerns
    existing_match.explanation = match.explanation

    existing_match.updated_at = updated_at

    session.add(existing_match)
    session.commit()
    session.refresh(existing_match)

    return existing_match


def get_matches_by_profile_id(
    session: Session,
    profile_id: int,
    limit: int = 50,
) -> list[JobMatchDB]:
    statement = (
        select(JobMatchDB)
        .where(JobMatchDB.profile_id == profile_id)
        .order_by(JobMatchDB.match_percentage.desc())
        .limit(limit)
    )

    return list(session.exec(statement).all())


def delete_matches_by_profile_id(
    session: Session,
    profile_id: int,
) -> int:
    matches = get_matches_by_profile_id(
        session=session,
        profile_id=profile_id,
        limit=100000,
    )

    deleted_count = len(matches)

    for match in matches:
        session.delete(match)

    session.commit()

    return deleted_count