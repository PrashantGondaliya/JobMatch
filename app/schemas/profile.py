from pydantic import BaseModel, Field


class CandidateProfileCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    target_role: str = Field(min_length=2, max_length=100)
    years_of_experience: float = Field(ge=0, le=50)
    skills: list[str] = Field(min_length=1)
    preferred_locations: list[str] = Field(default_factory=list)
    remote_preference: str = Field(default="remote", min_length=2, max_length=30)
    expected_salary_min: int | None = Field(default=None, ge=0)
    expected_salary_max: int | None = Field(default=None, ge=0)


class CandidateProfile(CandidateProfileCreate):
    id: int