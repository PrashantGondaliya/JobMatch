from fastapi import APIRouter


router = APIRouter(tags=["System"])


@router.get("/")
def root():
    return {
        "message": "Welcome to JobMatch AI",
        "status": "running"
    }


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": "JobMatch AI",
        "version": "0.1.0"
    }


@router.get("/version")
def get_version():
    return {
        "app": "JobMatch AI",
        "version": "0.1.0",
        "environment": "development"
    }