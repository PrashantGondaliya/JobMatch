# JobMatch AI

JobMatch AI is an AI-powered job discovery and application tracking platform.

## Current Features

- FastAPI backend
- Health check endpoint
- Project setup with Git and virtual environment

## Tech Stack

- Python
- FastAPI
- Uvicorn

## Run Locally

```bash
python -m uvicorn app.main:app --reload

## Database Migrations

This project uses Alembic for database migrations.

Create a new migration after changing database models:

```bash
alembic revision --autogenerate -m "describe change"

## Deployment Preparation

This project is prepared for deployment using environment variables and Alembic migrations.

### Required environment variables

```bash
APP_NAME=JobMatch AI
ENVIRONMENT=production
DEBUG=false

DATABASE_URL=postgresql+psycopg://username:password@host:5432/jobmatch

SECRET_KEY=replace_with_a_strong_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=60

BACKEND_CORS_ORIGINS=https://your-frontend-domain.com

```markdown
## Production Checklist

Before deploying:

- [ ] All tests pass with `python -m pytest -q`
- [ ] `.env` is not committed
- [ ] `SECRET_KEY` is strong and private
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=false`
- [ ] `DATABASE_URL` points to PostgreSQL
- [ ] Alembic migrations are committed
- [ ] `alembic upgrade head` runs successfully
- [ ] CORS origins are set correctly
- [ ] `/health` endpoint works

## Running with Docker

This project includes Docker support for running the FastAPI backend with PostgreSQL.

### Build and run

```bash
docker compose up --build