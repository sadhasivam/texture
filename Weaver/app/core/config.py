from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Weaver"
    api_v1_prefix: str = "/api/v1"
    upload_dir: str = "app/storage/uploads"
    max_upload_size: int = 100 * 1024 * 1024  # 100 MB
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
