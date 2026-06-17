from app.schemas.job import Job
from app.schemas.match import JobMatch
from app.schemas.profile import CandidateProfile


def normalize_skill(skill: str) -> str:
    """
    Convert a skill into a clean lowercase format.

    Example:
    " Python " -> "python"
    "FastAPI" -> "fastapi"
    """
    return skill.strip().lower()


def build_match_explanation(
    match_percentage: float,
    matched_skills: list[str],
    missing_skills: list[str],
) -> str:
    """
    Create a simple human-readable explanation for the match score.
    """
    if match_percentage >= 80:
        match_level = "Strong match"
    elif match_percentage >= 50:
        match_level = "Moderate match"
    elif match_percentage > 0:
        match_level = "Weak match"
    else:
        match_level = "No direct skill match"

    return (
        f"{match_level}. "
        f"Matched {len(matched_skills)} required skill(s). "
        f"Missing {len(missing_skills)} required skill(s)."
    )


def calculate_job_match(profile: CandidateProfile, job: Job) -> JobMatch:
    """
    Compare one candidate profile with one job.
    """

    candidate_skills = {normalize_skill(skill) for skill in profile.skills}

    required_skill_map = {
        normalize_skill(skill): skill
        for skill in job.required_skills
    }

    required_skill_names = set(required_skill_map.keys())

    if not required_skill_names:
        match_percentage = 0.0
        matched_skills = []
        missing_skills = []
    else:
        matched_skill_names = candidate_skills.intersection(required_skill_names)
        missing_skill_names = required_skill_names.difference(candidate_skills)

        matched_skills = [
            required_skill_map[skill_name]
            for skill_name in matched_skill_names
        ]

        missing_skills = [
            required_skill_map[skill_name]
            for skill_name in missing_skill_names
        ]

        match_percentage = round(
            (len(matched_skills) / len(required_skill_names)) * 100,
            2
        )

    explanation = build_match_explanation(
        match_percentage=match_percentage,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
    )

    return JobMatch(
        job_id=job.id,
        title=job.title,
        company=job.company,
        location=job.location,
        apply_url=job.apply_url,
        match_percentage=match_percentage,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        required_skills=job.required_skills,
        explanation=explanation,
    )


def generate_job_matches(
    profile: CandidateProfile,
    jobs: list[Job],
) -> list[JobMatch]:
    """
    Compare one profile against many jobs.
    Return the best matches first.
    """

    matches = [
        calculate_job_match(profile=profile, job=job)
        for job in jobs
    ]

    matches.sort(
        key=lambda match: match.match_percentage,
        reverse=True
    )

    return matches