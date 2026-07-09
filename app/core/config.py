from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "JobMatch AI"
    environment: str = "development"
    debug: bool = True

    database_url: str = "sqlite:///./jobmatch.db"

    secret_key: str = Field(default="change-me-in-development")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    backend_cors_origins: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

    @property
    def is_testing(self) -> bool:
        return self.environment.lower() == "testing"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        if not self.backend_cors_origins:
            return []

        return [
            origin.strip()
            for origin in self.backend_cors_origins.split(",")
            if origin.strip()
        ]

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.is_production:
            if self.debug:
                raise ValueError("DEBUG must be false in production.")

            if self.secret_key == "change-me-in-development":
                raise ValueError("SECRET_KEY must be changed in production.")

            if self.database_url.startswith("sqlite"):
                raise ValueError("SQLite should not be used in production.")

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()