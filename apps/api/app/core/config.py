"""Application configuration via environment variables (pydantic-settings)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All settings come from the environment; never commit real secrets."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    database_url: str = "postgresql+psycopg://bloodbank:bloodbank_dev@localhost:5432/bloodbank"
    redis_url: str = "redis://localhost:6379/0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    secret_key: str = "change-me-to-a-long-random-string"
    encryption_key: str = ""  # Fernet key; empty = derive a dev-only key (see crypto.py)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    mfa_token_expire_minutes: int = 5
    cors_origins: str = "http://localhost:3000"
    seed_admin_email: str = "admin@bloodbank.local"
    seed_admin_password: str = "Admin@123456"
    # Rate limits (per minute, per IP) — see docs/decisions.md.
    rate_limit_login_per_minute: int = 10
    rate_limit_auth_per_minute: int = 30
    rate_limit_write_per_minute: int = 60
    testing: bool = False


settings = Settings()
