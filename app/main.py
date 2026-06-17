from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="JobMatch AI",
    description="AI-powered job matching and application tracking platform.",
    version="0.1.0",
)


class CandidateProfileCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    target_role: str = Field(min_length=2, max_length=100)
    years_of_experience: float = Field(ge=0, le=50)
    skills: list[str] = Field(min_length=1)
    preferred_locations: list[str] = []
    remote_preference: str = "remote"
    expected_salary_min: int | None = Field(default=None, ge=0)
    expected_salary_max: int | None = Field(default=None, ge=0)


class CandidateProfile(CandidateProfileCreate):
    id: int


profiles: list[CandidateProfile] = []


@app.get("/")
def root():
    return {
        "message": "Welcome to JobMatch AI",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": "JobMatch AI",
        "version": "0.1.0"
    }


@app.get("/version")
def get_version():
    return {
        "app": "JobMatch AI",
        "version": "0.1.0",
        "environment": "development"
    }


@app.post("/profiles", response_model=CandidateProfile)
def create_profile(profile_data: CandidateProfileCreate):
    new_profile = CandidateProfile(
        id=len(profiles) + 1,
        **profile_data.model_dump()
    )

    profiles.append(new_profile)

    return new_profile


@app.get("/profiles", response_model=list[CandidateProfile])
def get_profiles():
    return profiles


@app.get("/profiles/{profile_id}", response_model=CandidateProfile)
def get_profile(profile_id: int):
    for profile in profiles:
        if profile.id == profile_id:
            return profile

    raise HTTPException(status_code=404, detail="Profile not found")