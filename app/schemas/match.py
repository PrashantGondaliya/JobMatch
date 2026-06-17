from pydantic import BaseModel, Field


class JobMatch(BaseModel):
    job_id: int
    title: str
    company: str
    location: str
    apply_url: str

    match_percentage: float = Field(ge=0, le=100)

    matched_skills: list[str]
    missing_skills: list[str]
    required_skills: list[str]

    explanation: str