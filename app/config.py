import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value else default


@dataclass(frozen=True)
class Settings:
    port: int = _int_env("PORT", 8080)
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/university_erp",
    )
    jwt_secret: str = os.getenv(
        "JWT_SECRET",
        "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    )
    jwt_issuer: str = os.getenv("JWT_ISSUER", "university-erp-service")
    jwt_expiration_seconds: int = _int_env("JWT_EXPIRATION_SECONDS", 900)
    refresh_token_expiration_seconds: int = _int_env(
        "REFRESH_TOKEN_EXPIRATION_SECONDS",
        2_592_000,
    )
    lock_max_attempts: int = _int_env("LOCK_MAX_ATTEMPTS", 5)
    lock_duration_minutes: int = _int_env("LOCK_DURATION_MINUTES", 15)
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
    allowed_origin: str = os.getenv("ALLOWED_ORIGIN", "http://localhost:3000")


settings = Settings()
