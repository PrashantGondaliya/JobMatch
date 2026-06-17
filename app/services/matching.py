from app.schemas.job import Job
from app.schemas.match import JobMatch, MatchScoreBreakdown
from app.schemas.profile import CandidateProfile


SKILL_ALIASES = {
    "python": {"python", "python3"},
    "fastapi": {"fastapi", "fast api"},
    "sql": {"sql", "postgresql", "postgres", "mysql", "sqlite", "database"},
    "docker": {"docker", "containers", "containerization"},
    "git": {"git", "github", "version control"},
    "apis": {"api", "apis", "rest", "rest api", "rest apis"},
    "javascript": {"javascript", "js"},
    "typescript": {"typescript", "ts"},
    "react": {"react", "react.js", "reactjs"},
    "machine learning": {"machine learning", "ml"},
    "data analysis": {"data analysis", "analytics", "data analytics"},
    "excel": {"excel", "microsoft excel", "spreadsheets"},
    "aws": {"aws", "amazon web services"},
}


def normalize_text(value: str) -> str:
    """
    Convert text into a clean lowercase format.

    Example:
    " Python " -> "python"
    "FastAPI" -> "fastapi"
    """
    return value.strip().lower()


def canonicalize_skill(skill: str) -> str:
    """
    Convert similar skills into one common name.

    Example:
    "PostgreSQL" -> "sql"
    "GitHub" -> "git"
    "REST API" -> "apis"
    """
    normalized_skill = normalize_text(skill)

    for canonical_skill, aliases in SKILL_ALIASES.items():
        if normalized_skill in aliases:
            return canonical_skill

    return normalized_skill


def calculate_skill_score(
    profile: CandidateProfile,
    job: Job,
) -> tuple[float, list[str], list[str]]:
    """
    Compare candidate skills with job required skills.

    Returns:
    - skill score
    - matched skills
    - missing skills
    """

    candidate_skills = {
        canonicalize_skill(skill)
        for skill in profile.skills
    }

    required_skill_map = {
        canonicalize_skill(skill): skill
        for skill in job.required_skills
    }

    required_skills = set(required_skill_map.keys())

    if not required_skills:
        return 0.0, [], []

    matched_skill_names = candidate_skills.intersection(required_skills)
    missing_skill_names = required_skills.difference(candidate_skills)

    matched_skills = [
        required_skill_map[skill_name]
        for skill_name in matched_skill_names
    ]

    missing_skills = [
        required_skill_map[skill_name]
        for skill_name in missing_skill_names
    ]

    skill_score = round(
        (len(matched_skills) / len(required_skills)) * 100,
        2
    )

    return skill_score, matched_skills, missing_skills


def calculate_location_score(profile: CandidateProfile, job: Job) -> float:
    """
    Score how well the job location matches the user's preferred locations.
    """

    if not profile.preferred_locations:
        return 100.0

    job_location = normalize_text(job.location)

    if job_location in {"not specified", "unknown", ""}:
        return 50.0

    preferred_locations = [
        normalize_text(location)
        for location in profile.preferred_locations
    ]

    for preferred_location in preferred_locations:
        if preferred_location in job_location or job_location in preferred_location:
            return 100.0

    if "remote" in preferred_locations and "remote" in job_location:
        return 100.0

    return 0.0


def calculate_remote_score(profile: CandidateProfile, job: Job) -> float:
    """
    Score how well the job remote type matches the user's remote preference.
    """

    user_preference = normalize_text(profile.remote_preference)
    job_remote_type = normalize_text(job.remote_type)

    flexible_preferences = {"any", "flexible", "no preference", "not specified"}

    if user_preference in flexible_preferences:
        return 100.0

    if user_preference == job_remote_type:
        return 100.0

    if user_preference == "remote" and job_remote_type == "hybrid":
        return 70.0

    if user_preference == "hybrid" and job_remote_type == "remote":
        return 80.0

    if job_remote_type in {"not specified", "unknown", ""}:
        return 50.0

    return 0.0


def calculate_salary_score(profile: CandidateProfile, job: Job) -> float:
    """
    Score how well the job salary range matches the user's expected salary.
    """

    user_min = profile.expected_salary_min
    user_max = profile.expected_salary_max
    job_min = job.salary_min
    job_max = job.salary_max

    if user_min is None and user_max is None:
        return 100.0

    if job_min is None and job_max is None:
        return 50.0

    if user_min is not None and job_max is not None and job_max < user_min:
        return 0.0

    if user_max is not None and job_min is not None and job_min > user_max:
        return 80.0

    return 100.0


def calculate_final_score(
    skill_score: float,
    location_score: float,
    remote_score: float,
    salary_score: float,
) -> float:
    """
    Calculate weighted final score.

    Skills are most important, so they get the highest weight.
    """

    final_score = (
        skill_score * 0.60
        + location_score * 0.15
        + remote_score * 0.15
        + salary_score * 0.10
    )

    return round(final_score, 2)


def build_match_reasons(
    matched_skills: list[str],
    location_score: float,
    remote_score: float,
    salary_score: float,
) -> list[str]:
    """
    Build positive reasons for the match.
    """

    reasons = []

    if matched_skills:
        reasons.append(
            f"Matched skills: {', '.join(matched_skills)}."
        )

    if location_score >= 80:
        reasons.append("Location matches your preferences.")

    if remote_score >= 80:
        reasons.append("Remote preference is a good match.")

    if salary_score >= 80:
        reasons.append("Salary range appears suitable.")

    if not reasons:
        reasons.append("This job has limited direct overlap with your profile.")

    return reasons


def build_concerns(
    missing_skills: list[str],
    location_score: float,
    remote_score: float,
    salary_score: float,
) -> list[str]:
    """
    Build concerns or gaps for the match.
    """

    concerns = []

    if missing_skills:
        concerns.append(
            f"Missing skills: {', '.join(missing_skills)}."
        )

    if location_score == 0:
        concerns.append("Location may not match your preferences.")

    if remote_score == 0:
        concerns.append("Remote type may not match your preference.")

    if salary_score == 0:
        concerns.append("Salary range may be below your expectation.")

    return concerns


def build_match_explanation(
    final_score: float,
    matched_skills: list[str],
    missing_skills: list[str],
) -> str:
    """
    Create a simple human-readable explanation.
    """

    if final_score >= 80:
        match_level = "Strong match"
    elif final_score >= 60:
        match_level = "Good match"
    elif final_score >= 40:
        match_level = "Moderate match"
    elif final_score > 0:
        match_level = "Weak match"
    else:
        match_level = "No meaningful match"

    return (
        f"{match_level}. "
        f"Matched {len(matched_skills)} skill(s), "
        f"missing {len(missing_skills)} skill(s)."
    )


def calculate_job_match(profile: CandidateProfile, job: Job) -> JobMatch:
    """
    Compare one candidate profile with one job.
    """

    skill_score, matched_skills, missing_skills = calculate_skill_score(
        profile=profile,
        job=job,
    )

    location_score = calculate_location_score(profile=profile, job=job)
    remote_score = calculate_remote_score(profile=profile, job=job)
    salary_score = calculate_salary_score(profile=profile, job=job)

    final_score = calculate_final_score(
        skill_score=skill_score,
        location_score=location_score,
        remote_score=remote_score,
        salary_score=salary_score,
    )

    match_reasons = build_match_reasons(
        matched_skills=matched_skills,
        location_score=location_score,
        remote_score=remote_score,
        salary_score=salary_score,
    )

    concerns = build_concerns(
        missing_skills=missing_skills,
        location_score=location_score,
        remote_score=remote_score,
        salary_score=salary_score,
    )

    explanation = build_match_explanation(
        final_score=final_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
    )

    return JobMatch(
        job_id=job.id,
        title=job.title,
        company=job.company,
        location=job.location,
        apply_url=job.apply_url,
        match_percentage=final_score,
        score_breakdown=MatchScoreBreakdown(
            skill_score=skill_score,
            location_score=location_score,
            remote_score=remote_score,
            salary_score=salary_score,
        ),
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        required_skills=job.required_skills,
        match_reasons=match_reasons,
        concerns=concerns,
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
        reverse=True,
    )

    return matches