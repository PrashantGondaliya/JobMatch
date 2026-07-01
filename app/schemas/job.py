from pydantic import BaseModel, ConfigDict, Field


class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    company: str = Field(min_length=2, max_length=150)
    location: str = Field(default="Not specified", max_length=150)
    remote_type: str = Field(default="not_specified", max_length=50)
    employment_type: str = Field(default="full_time", max_length=50)
    description: str = Field(min_length=20)
    apply_url: str = Field(min_length=5, max_length=500)
    source: str = Field(default="manual", max_length=100)
    required_skills: list[str] = Field(default_factory=list)
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)


class Job(JobCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    items: list[Job]
    total_count: int
    returned_count: int
    limit: int
    offset: int