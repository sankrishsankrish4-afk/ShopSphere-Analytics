from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables or backend/.env."""

    app_name: str = "ShopSphere Analytics API"
    app_version: str = "1.0.0"
    app_description: str = (
        "Market basket analytics API for association rules, customer segments, "
        "and real-time cart recommendations."
    )
    database_url: str = Field(
        default=f"sqlite:///{(BACKEND_DIR / 'data' / 'shopsphere.db').as_posix()}",
        alias="DATABASE_URL",
    )
    api_port: int = Field(default=8000, alias="API_PORT")
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
