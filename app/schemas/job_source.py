from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.job import Job


class JobSourceType(str, Enum):
    GREENHOUSE = "greenhouse"


class JobSourceCreate(BaseModel):
    source_type: JobSourceType = JobSourceType.GREENHOUSE
    company_slug: str = Field(min_length=2, max_length=100)
    display_name: str | None = Field(default=None, max_length=150)
    is_active: bool = True


class JobSourceUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=150)
    is_active: bool | None = None


class JobSource(BaseModel):
    id: int
    source_type: JobSourceType
    company_slug: str
    display_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_fetched_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class JobFetchSummary(BaseModel):
    source_type: JobSourceType
    company_slug: str
    fetched_count: int
    created_count: int
    skipped_count: int
    created_jobs: list[Job]