from datetime import UTC, datetime, timedelta

from app.config import settings
from app.database import get_connection
from app.errors import AppError


def find_student_by_registration(registration: str) -> dict | None:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, registration, full_name, password_hash, account_non_locked,
                   failed_attempts, lock_time, course_id
              FROM students
             WHERE registration = %s
            """,
            (registration,),
        ).fetchone()


def register_failure(student: dict) -> None:
    failed_attempts = int(student["failed_attempts"]) + 1
    account_non_locked = failed_attempts < settings.lock_max_attempts
    lock_time = datetime.now(UTC).replace(tzinfo=None) if not account_non_locked else student["lock_time"]
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE students
               SET failed_attempts = %s,
                   account_non_locked = %s,
                   lock_time = %s
             WHERE id = %s
            """,
            (failed_attempts, account_non_locked, lock_time, student["id"]),
        )


def reset_failures(student_id: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE students
               SET failed_attempts = 0,
                   account_non_locked = TRUE,
                   lock_time = NULL
             WHERE id = %s
            """,
            (student_id,),
        )


def validate_lock(student: dict) -> None:
    if student["account_non_locked"]:
        return

    lock_time = student["lock_time"]
    locked_until = lock_time + timedelta(minutes=settings.lock_duration_minutes)
    if locked_until > datetime.now(UTC).replace(tzinfo=None):
        raise AppError(423, "ACCOUNT_LOCKED", "Account locked for 15 minutes due to repeated failures")

    reset_failures(student["id"])


def get_student_context_by_registration(registration: str) -> dict:
    with get_connection() as conn:
        student = conn.execute(
            """
            SELECT s.registration,
                   s.full_name,
                   c.name AS course_name,
                   c.required_optional_credits,
                   e.current_semester,
                   e.completed_optional_credits
              FROM students s
              JOIN courses c ON c.id = s.course_id
              JOIN enrollments e ON e.student_id = s.id
             WHERE s.registration = %s
            """,
            (registration,),
        ).fetchone()

        if not student:
            raise AppError(404, "STUDENT_NOT_FOUND", f"Student {registration} not found")

        subjects = conn.execute(
            """
            SELECT sub.name,
                   sub.teacher,
                   sub.workload_hours,
                   sub.minimum_attendance_percentage,
                   ss.current_attendance_percentage,
                   ss.absences_in_hours,
                   sub.class_duration_minutes
              FROM students s
              JOIN student_subjects ss ON ss.student_id = s.id
              JOIN subjects sub ON sub.id = ss.subject_id
             WHERE s.registration = %s
             ORDER BY sub.name
            """,
            (registration,),
        ).fetchall()

    return {
        "registration": student["registration"],
        "fullName": student["full_name"],
        "course": {
            "name": student["course_name"],
            "currentSemester": student["current_semester"],
            "requiredOptionalCredits": student["required_optional_credits"],
            "completedOptionalCredits": student["completed_optional_credits"],
        },
        "subjects": [
            {
                "name": subject["name"],
                "teacher": subject["teacher"],
                "workloadHours": subject["workload_hours"],
                "minimumAttendancePercentage": subject["minimum_attendance_percentage"],
                "currentAttendancePercentage": subject["current_attendance_percentage"],
                "absencesInHours": subject["absences_in_hours"],
                "classDurationMinutes": subject["class_duration_minutes"],
            }
            for subject in subjects
        ],
    }
