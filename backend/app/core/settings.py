from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
    env_file=".env.local",
    env_file_encoding="utf-8",
    extra="ignore",
)
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    admin_username: str
    admin_password: str

    database_url: str
    api_base_url: str = "http://localhost:8000"

settings = Settings()
