from app.core.config import Settings


def test_settings_defaults():
    settings = Settings()

    assert settings.app_name == "JobMatch AI"
    assert settings.environment in ["development", "testing", "production"]
    assert settings.algorithm == "HS256"
    assert settings.access_token_expire_minutes > 0


def test_cors_origins_list_parses_comma_separated_values():
    settings = Settings(
        backend_cors_origins="http://localhost:3000,http://127.0.0.1:3000"
    )

    assert settings.cors_origins_list == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]