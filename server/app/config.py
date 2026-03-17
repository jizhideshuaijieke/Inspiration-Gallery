from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_env: str = "dev"

    db_url: str

    jwt_secret: str = "dev-secret-change-me"
    jwt_expire_minutes: int = 10080

    # Disabled by default; keep real generation path active.
    demo_instant_task_success: bool = False
    model_root: str = str(Path(__file__).resolve().parents[2] / "transfer-models" / "checkpoints")
    model_device: str = "cpu"
    max_concurrency: int = 1

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
