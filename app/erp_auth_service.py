from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.config import settings
from app.database import get_connection
from app.errors import AppError
from app.security import generate_access_token, hash_token, parse_access_token, password_matches
from app.student_repository import (
    find_student_by_registration,
    get_student_context_by_registration,
    register_failure,
    reset_failures,
    validate_lock,
)


def issue_erp_tokens(student: dict) -> dict:
    access_token = generate_access_token(student["registration"])
    raw_refresh_token = f"{uuid4()}.{uuid4()}"
    expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(seconds=settings.refresh_token_expiration_seconds)

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO refresh_tokens (id, token_hash, student_id, expires_at, revoked)
            VALUES (%s, %s, %s, %s, FALSE)
            """,
            (uuid4(), hash_token(raw_refresh_token), student["id"], expires_at),
        )

    return {
        "accessToken": access_token,
        "expiresIn": settings.jwt_expiration_seconds,
        "refreshToken": raw_refresh_token,
    }


def erp_login(registration: str, password: str) -> dict:
    student = find_student_by_registration(registration)
    if not student:
        raise AppError(401, "AUTHENTICATION_FAILED", "Invalid credentials")

    validate_lock(student)

    if not password_matches(password, student["password_hash"]):
        register_failure(student)
        updated = find_student_by_registration(registration)
        if updated and not updated["account_non_locked"]:
            raise AppError(423, "ACCOUNT_LOCKED", "Account locked for 15 minutes due to repeated failures")
        raise AppError(401, "AUTHENTICATION_FAILED", "Invalid credentials")

    reset_failures(student["id"])
    return issue_erp_tokens(student)


def erp_refresh(refresh_token: str) -> dict:
    token_hash = hash_token(refresh_token)
    with get_connection() as conn:
        token = conn.execute(
            """
            SELECT rt.id, rt.student_id, rt.expires_at, rt.revoked,
                   s.registration, s.full_name, s.password_hash, s.account_non_locked,
                   s.failed_attempts, s.lock_time, s.course_id
              FROM refresh_tokens rt
              JOIN students s ON s.id = rt.student_id
             WHERE rt.token_hash = %s
            """,
            (token_hash,),
        ).fetchone()

        if not token or token["revoked"] or token["expires_at"] < datetime.now(UTC).replace(tzinfo=None):
            raise AppError(401, "INVALID_REFRESH_TOKEN", "Refresh token is expired or revoked")

        conn.execute("UPDATE refresh_tokens SET revoked = TRUE WHERE id = %s", (token["id"],))

    return issue_erp_tokens(token)


def registration_from_bearer(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AppError(403, "ACCESS_DENIED", "Access denied")
    return parse_access_token(authorization[7:].strip())


def context_from_token(authorization: str | None) -> dict:
    return get_student_context_by_registration(registration_from_bearer(authorization))
