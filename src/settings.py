from functools import cache
from typing import Any

from pydantic import PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MARIA_API_URL: str = "https://dev.mariasaude.digital/maria/app/v1"
    MARIA_API_SUPER_TOKEN: str | None = None

    POSTGRES_DB: str = "maria"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URI: str | None = None

    @field_validator("DATABASE_URI")
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=info.data.get("POSTGRES_USER"),
                password=info.data.get("POSTGRES_PASSWORD"),
                host=info.data.get("POSTGRES_HOST"),
                port=info.data.get("POSTGRES_PORT"),
                path=info.data.get("POSTGRES_DB"),
            )
        )

    model_config = SettingsConfigDict(env_file=[".env"], env_file_encoding="utf-8", extra="ignore")


@cache
def get_settings() -> Settings:
    return Settings()


settings = Settings()
