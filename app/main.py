from fastapi import FastAPI

from app.routers import applications, jobs, matches, profiles, system


app = FastAPI(
    title="JobMatch AI",
    description="AI-powered job matching and application tracking platform.",
    version="0.1.0",
)


app.include_router(system.router)
app.include_router(profiles.router)
app.include_router(jobs.router)
app.include_router(matches.router)
app.include_router(applications.router)