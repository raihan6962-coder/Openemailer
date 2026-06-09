from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    app_name: str = "Openmailer"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str = "change-this-to-a-long-random-string"
    encryption_key: str = "change-this-to-a-32-char-hex-string-for-aes"
    environment: str = "development"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/openmailer"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/openmailer"

    redis_url: str = "redis://localhost:6379/0"
    redis_celery_url: str = "redis://localhost:6379/1"

    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    jwt_secret_key: str = "change-this-to-a-long-random-jwt-secret"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"

    outlook_client_id: str = ""
    outlook_client_secret: str = ""
    outlook_redirect_uri: str = "http://localhost:8000/api/v1/auth/outlook/callback"

    default_smtp_port: int = 587
    default_imap_port: int = 993

    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    log_level: str = "DEBUG"
    log_format: str = "json"

    warmup_min_daily: int = 5
    warmup_max_daily: int = 50
    warmup_network_min_trust: int = 50

    stripe_api_key: str = ""
    stripe_webhook_secret: str = ""

    enable_oauth: bool = True
    enable_warmup: bool = True
    enable_billing: bool = False

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
