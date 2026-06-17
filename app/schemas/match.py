from pydantic import BaseModel, Field


class MatchScoreBreakdown(BaseModel):
    skill_score: float = Field(ge=0, le=100)
    location_score: float = Field(ge=0, le=100)
    remote_score: float = Field(ge=0, le=100)
    salary_score: float = Field(ge=0, le=100)


class JobMatch(BaseModel):
    job_id: int
    title: str
    company: str
    location: str
    apply_url: str

    match_percentage: float = Field(ge=0, le=100)
    score_breakdown: MatchScoreBreakdown

    matched_skills: list[str]
    missing_skills: list[str]
    required_skills: list[str]

    match_reasons: list[str]
    concerns: list[str]
    explanation: str