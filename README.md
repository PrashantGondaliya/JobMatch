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