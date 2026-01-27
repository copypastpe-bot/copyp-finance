from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    bot_token: str
    default_timezone: str = "Europe/Belgrade"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


app_settings = AppSettings()
