from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str | None = None
    ADMIN_USER_ID: int = 751585223  # ID администратора

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
