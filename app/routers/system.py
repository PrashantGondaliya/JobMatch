from fastapi import APIRouter

from app.core.config import settings


router = APIRouter(tags=["System"])


@router.get("/")
def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "environment": settings.environment,
    }


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }


@router.get("/version")
def version():
    return {
        "version": "0.1.0",
        "app": settings.app_name,
    }