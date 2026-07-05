from datetime import datetime, timezone

from sqlalchemy import Column, JSON, UniqueConstraint
from sqlmodel import Field, SQLModel


def get_current_time() -> datetime:
    return datetime.now(timezone.utc)

'''class UserDB(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)

    email: str = Field(index=True, unique=True)
    full_name: str

    hashed_password: str

    is_active: bool = True

    created_at: datetime = Field(default_factory=get_current_time)
    updated_at: datetime = Field(default_factory=get_current_time)'''

class CandidateProfileDB(SQLModel, table=True):
    __tablename__ = "candidate_profiles"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")

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


class JobMatchDB(SQLModel, table=True):
    __tablename__ = "job_matches"

    __table_args__ = (
        UniqueConstraint("profile_id", "job_id", name="uq_job_match_profile_job"),
    )

    id: int | None = Field(default=None, primary_key=True)

    profile_id: int = Field(foreign_key="candidate_profiles.id")
    job_id: int = Field(foreign_key="jobs.id")

    job_title: str
    company: str
    location: str
    apply_url: str

    match_percentage: float

    skill_score: float
    location_score: float
    remote_score: float
    salary_score: float

    matched_skills: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    missing_skills: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    required_skills: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    match_reasons: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    concerns: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    explanation: str

    created_at: datetime = Field(default_factory=get_current_time)
    updated_at: datetime = Field(default_factory=get_current_time)

class UserDB(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)

    email: str = Field(index=True, unique=True)
    full_name: str

    hashed_password: str

    role: str = Field(default="user", index=True)

    is_active: bool = True

    created_at: datetime = Field(default_factory=get_current_time)
    updated_at: datetime = Field(default_factory=get_current_time)