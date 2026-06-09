import hashlib
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Openmailer"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str = ""
    encryption_key: str = ""
    environment: str = "development"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/openmailer"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/openmailer"

    redis_url: str = "redis://localhost:6379/0"

    celery_broker_url: str = ""
    celery_result_backend: str = ""

    jwt_secret_key: str = ""
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

    frontend_url: str = ""

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._apply_railway_defaults()

    def _apply_railway_defaults(self):
        rid = os.environ.get("RAILWAY_SERVICE_ID")
        if not rid:
            return

        if not self.secret_key:
            self.secret_key = hashlib.sha256(f"openmailer:{rid}:sk".encode()).hexdigest()

        if not self.jwt_secret_key:
            self.jwt_secret_key = hashlib.sha256(f"openmailer:{rid}:jwt".encode()).hexdigest()

        if not self.encryption_key:
            raw = hashlib.sha256(f"openmailer:{rid}:enc".encode()).digest()[:32]
            import base64
            self.encryption_key = base64.urlsafe_b64encode(raw).decode()

        if not self.celery_broker_url and self.redis_url:
            import re
            self.celery_broker_url = re.sub(r"/\d+$", "/1", self.redis_url)

        if not self.celery_result_backend and self.redis_url:
            import re
            self.celery_result_backend = re.sub(r"/\d+$", "/2", self.redis_url)

        own_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
        frontend_url = self.frontend_url or os.environ.get("FRONTEND_URL", "")
        origins = ["http://localhost:3000"]
        if frontend_url:
            origins.append(f"https://{frontend_url}".replace("https://https://", "https://"))
        if own_domain:
            origins.append(f"https://{own_domain}")
        self.cors_origins = ",".join(origins)

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
