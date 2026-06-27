from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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


class StoredJobMatch(BaseModel):
    id: int
    profile_id: int
    job_id: int

    job_title: str
    company: str
    location: str
    apply_url: str

    match_percentage: float = Field(ge=0, le=100)

    skill_score: float = Field(ge=0, le=100)
    location_score: float = Field(ge=0, le=100)
    remote_score: float = Field(ge=0, le=100)
    salary_score: float = Field(ge=0, le=100)

    matched_skills: list[str]
    missing_skills: list[str]
    required_skills: list[str]

    match_reasons: list[str]
    concerns: list[str]
    explanation: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MatchRefreshSummary(BaseModel):
    profile_id: int
    total_jobs_checked: int
    matches_saved: int
    top_matches: list[StoredJobMatch]