import base64
import hashlib
import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.config import settings


def password_matches(raw_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(raw_password.encode("utf-8"), password_hash.encode("utf-8"))


def hash_token(token: str) -> str:
    digest = hashlib.sha256(token.encode("utf-8")).digest()
    return base64.b64encode(digest).decode("ascii")


def generate_access_token(registration: str) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": registration,
        "iss": settings.jwt_issuer,
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + timedelta(seconds=settings.jwt_expiration_seconds),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def parse_access_token(token: str) -> str:
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=["HS256"],
        issuer=settings.jwt_issuer,
    )
    return str(payload["sub"])
