from fastapi import FastAPI

from app.routers import profiles, system


app = FastAPI(
    title="JobMatch AI",
    description="AI-powered job matching and application tracking platform.",
    version="0.1.0",
)


app.include_router(system.router)
app.include_router(profiles.router)