from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ApplicationStatus(str, Enum):
    SAVED = "saved"
    APPLIED = "applied"
    ASSESSMENT = "assessment"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class ApplicationCreate(BaseModel):
    profile_id: int = Field(gt=0)
    job_id: int = Field(gt=0)
    status: ApplicationStatus = ApplicationStatus.SAVED
    notes: str | None = Field(default=None, max_length=1000)


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
    notes: str | None = Field(default=None, max_length=1000)


class JobApplication(BaseModel):
    id: int
    profile_id: int
    job_id: int
    status: ApplicationStatus
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    applied_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)