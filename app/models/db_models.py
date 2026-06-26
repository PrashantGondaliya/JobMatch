from datetime import datetime, timezone

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


def get_current_time() -> datetime:
    return datetime.now(timezone.utc)


class CandidateProfileDB(SQLModel, table=True):
    __tablename__ = "candidate_profiles"

    id: int | None = Field(default=None, primary_key=True)

    full_name: str
    target_role: str
    years_of_experience: float

    skills: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    preferred_locations: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    remote_preference: str = "remote"
    expected_salary_min: int | None = None
    expected_salary_max: int | None = None


class JobDB(SQLModel, table=True):
    __tablename__ = "jobs"

    id: int | None = Field(default=None, primary_key=True)

    title: str
    company: str
    location: str = "Not specified"
    remote_type: str = "not_specified"
    employment_type: str = "full_time"
    description: str
    apply_url: str
    source: str = "manual"

    required_skills: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    salary_min: int | None = None
    salary_max: int | None = None


class JobApplicationDB(SQLModel, table=True):
    __tablename__ = "job_applications"

    id: int | None = Field(default=None, primary_key=True)

    profile_id: int = Field(foreign_key="candidate_profiles.id")
    job_id: int = Field(foreign_key="jobs.id")

    status: str = "saved"
    notes: str | None = None

    created_at: datetime = Field(default_factory=get_current_time)
    updated_at: datetime = Field(default_factory=get_current_time)
    applied_at: datetime | None = None


class JobSourceDB(SQLModel, table=True):
    __tablename__ = "job_sources"

    id: int | None = Field(default=None, primary_key=True)

    source_type: str = "greenhouse"
    company_slug: str
    display_name: str

    is_active: bool = True

    created_at: datetime = Field(default_factory=get_current_time)
    updated_at: datetime = Field(default_factory=get_current_time)
    last_fetched_at: datetime | None = None