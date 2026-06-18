from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import applications, jobs, matches, profiles, system


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="JobMatch AI",
    description="AI-powered job matching and application tracking platform.",
    version="0.1.0",
    lifespan=lifespan,
)


app.include_router(system.router)
app.include_router(profiles.router)
app.include_router(jobs.router)
app.include_router(matches.router)
app.include_router(applications.router)