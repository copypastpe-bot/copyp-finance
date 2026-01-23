from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

ASYNC_DRIVER_PREFIX = "postgresql+asyncpg://"


class DbSettings(BaseSettings):
    database_url: str | None = Field(default=None, validation_alias="DATABASE_URL")
    db_host: str = Field(validation_alias="DB_HOST")
    db_port: int = Field(default=5432, validation_alias="DB_PORT")
    db_name: str = Field(validation_alias="DB_NAME")
    db_user: str = Field(validation_alias="DB_USER")
    db_password: str = Field(validation_alias="DB_PASSWORD")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    def get_async_database_url(self) -> str:
        if self.database_url:
            return self._normalize_database_url(self.database_url)
        return (
            f"{ASYNC_DRIVER_PREFIX}{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @staticmethod
    def _normalize_database_url(raw_url: str) -> str:
        if raw_url.startswith(ASYNC_DRIVER_PREFIX):
            return raw_url
        if raw_url.startswith("postgresql://"):
            return raw_url.replace("postgresql://", ASYNC_DRIVER_PREFIX, 1)
        if raw_url.startswith("postgres://"):
            return raw_url.replace("postgres://", ASYNC_DRIVER_PREFIX, 1)
        return raw_url


db_settings = DbSettings()
