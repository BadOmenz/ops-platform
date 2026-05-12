from functools import lru_cache

from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = "local"
    app_name: str = "Ops Platform API"
    database_url: str = Field(
        default="postgresql+psycopg://ops_platform:ops_platform@localhost:5435/ops_platform"
    )
    allowed_origins: list[str] = ["http://localhost:5173"]
    entra_tenant_id: str = ""
    entra_client_id: str = ""
    entra_authority: str = ""
    dev_auth_enabled: bool = True
    dev_auth_subject: str = "dev-user"
    dev_auth_email: str = "dev.user@example.com"
    dev_auth_display_name: str = "Dev User"
    demo_mode_enabled: bool = False
    demo_session_ttl_hours: int = 24

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
