from fastapi import FastAPI

app = FastAPI(
    title="JobMatch AI",
    description="AI-powered job matching and application tracking platform.",
    version="0.1.0",
)


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