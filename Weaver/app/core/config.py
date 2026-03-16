import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Weaver"
    api_v1_prefix: str = "/api/v1"
    upload_dir: str = "app/storage/uploads"
    max_upload_size: int = 100 * 1024 * 1024  # 100 MB

    # CORS origins - can be overridden via CORS_ORIGINS env variable
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
    ]

    # Production environment flag
    environment: str = "development"

    class Config:
        env_file = ".env"


# Allow environment variable to override CORS origins
_cors_env = os.getenv("CORS_ORIGINS")
if _cors_env:
    cors_list = [origin.strip() for origin in _cors_env.split(",")]
    Settings.model_fields["cors_origins"].default = cors_list

settings = Settings()
