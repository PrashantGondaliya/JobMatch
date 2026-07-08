from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import (
    applications,
    auth,
    job_sources,
    jobs,
    matches,
    profiles,
    system,
)


app = FastAPI(
    title=settings.app_name,
    description="AI-powered job matching and application tracking platform.",
    version="0.1.0",
    debug=settings.debug,
)


if settings.cors_origins_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app.include_router(system.router)
app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(jobs.router)
app.include_router(matches.router)
app.include_router(applications.router)
app.include_router(job_sources.router)