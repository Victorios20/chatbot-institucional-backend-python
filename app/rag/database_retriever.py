from collections.abc import Callable
from decimal import Decimal
from datetime import date, datetime, time
from uuid import UUID

from app.database import get_connection


QueryResult = dict[str, object]


def serialize_value(value):
    if isinstance(value, (datetime, date, time, UUID)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def serialize_rows(rows) -> list[dict]:
    return [{key: serialize_value(value) for key, value in row.items()} for row in rows]


def filter_by_subject(rows: list[dict], detected_subjects: list[str]) -> list[dict]:
    if not detected_subjects:
        return rows
    wanted = {subject.lower() for subject in detected_subjects}
    return [row for row in rows if str(row.get("subject_name", row.get("name", ""))).lower() in wanted]


def safe_query(query_name: str, callback: Callable[[], object]) -> QueryResult:
    try:
        return {"available": True, "data": callback()}
    except Exception as exc:
        # Some RAG tables may not exist until V5/V6 are applied. Keep the chat alive.
        return {
            "available": False,
            "data": [],
            "note": f"Consulta {query_name} indisponivel no banco atual.",
            "errorType": exc.__class__.__name__,
        }


def fetch_student_profile(registration: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT s.registration,
                   s.full_name,
                   c.name AS course_name,
                   e.current_semester,
                   c.required_optional_credits,
                   e.completed_optional_credits
              FROM students s
              JOIN courses c ON c.id = s.course_id
              JOIN enrollments e ON e.student_id = s.id
             WHERE s.registration = %s
            """,
            (registration,),
        ).fetchall()
    return serialize_rows(rows)


def fetch_student_subjects(registration: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT sub.name AS subject_name,
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
    return serialize_rows(rows)


def fetch_subject_attendance(registration: str, detected_subjects: list[str]) -> list[dict]:
    return filter_by_subject(fetch_student_subjects(registration), detected_subjects)


def fetch_student_grades(registration: str, detected_subjects: list[str]) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT sub.name AS subject_name,
                   sg.assessment_name,
                   sg.grade_value,
                   sg.weight,
                   sg.recorded_at
              FROM students s
              JOIN student_grades sg ON sg.student_id = s.id
              JOIN subjects sub ON sub.id = sg.subject_id
             WHERE s.registration = %s
             ORDER BY sub.name, sg.assessment_name
            """,
            (registration,),
        ).fetchall()
    return filter_by_subject(serialize_rows(rows), detected_subjects)


def fetch_assessment_models(registration: str, detected_subjects: list[str]) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT sub.name AS subject_name,
                   am.model_type,
                   am.minimum_average,
                   am.formula_description,
                   am.av3_has_greater_weight
              FROM students s
              JOIN student_subjects ss ON ss.student_id = s.id
              JOIN subjects sub ON sub.id = ss.subject_id
              JOIN assessment_models am ON am.subject_id = sub.id
             WHERE s.registration = %s
             ORDER BY sub.name
            """,
            (registration,),
        ).fetchall()
    return filter_by_subject(serialize_rows(rows), detected_subjects)


def fetch_curriculum_rules(registration: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT c.name AS course_name,
                   cr.total_semesters,
                   cr.required_optional_hours,
                   cr.required_complementary_hours,
                   cr.requires_internship,
                   cr.notes
              FROM students s
              JOIN courses c ON c.id = s.course_id
              JOIN curriculum_rules cr ON cr.course_id = c.id
             WHERE s.registration = %s
            """,
            (registration,),
        ).fetchall()
    return serialize_rows(rows)


def fetch_complementary_activities(registration: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT ca.activity_type,
                   ca.description,
                   ca.hours,
                   ca.status,
                   ca.approved_by,
                   ca.approved_at
              FROM students s
              JOIN complementary_activities ca ON ca.student_id = s.id
             WHERE s.registration = %s
             ORDER BY ca.status, ca.activity_type
            """,
            (registration,),
        ).fetchall()
    return serialize_rows(rows)


def fetch_financial_records(registration: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT fr.reference_month,
                   fr.amount,
                   fr.due_date,
                   fr.status,
                   fr.paid_at,
                   fr.payment_method,
                   fr.description
              FROM students s
              JOIN financial_records fr ON fr.student_id = s.id
             WHERE s.registration = %s
             ORDER BY fr.reference_month DESC
             LIMIT 6
            """,
            (registration,),
        ).fetchall()
    return serialize_rows(rows)


def fetch_student_benefits(registration: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT sb.benefit_type,
                   sb.percentage,
                   sb.status,
                   sb.valid_from,
                   sb.valid_until,
                   sb.loss_reason
              FROM students s
              JOIN student_benefits sb ON sb.student_id = s.id
             WHERE s.registration = %s
             ORDER BY sb.status, sb.benefit_type
            """,
            (registration,),
        ).fetchall()
    return serialize_rows(rows)


def fetch_academic_events() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT title,
                   event_type,
                   starts_on,
                   ends_on,
                   audience,
                   description
              FROM academic_events
             ORDER BY starts_on
             LIMIT 12
            """
        ).fetchall()
    return serialize_rows(rows)


def fetch_internships(registration: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT i.company_name,
                   i.internship_type,
                   i.status,
                   i.starts_on,
                   i.ends_on,
                   i.weekly_hours,
                   i.approved_hours,
                   i.supervisor
              FROM students s
              JOIN internships i ON i.student_id = s.id
             WHERE s.registration = %s
             ORDER BY i.starts_on DESC
            """,
            (registration,),
        ).fetchall()
    return serialize_rows(rows)


def fetch_detailed_attendance(registration: str, detected_subjects: list[str]) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT sub.name AS subject_name,
                   cls.class_date,
                   cls.topic,
                   cls.is_required_for_all,
                   cs.shift,
                   cs.slot_code AS planned_slot_code,
                   cs.duration_minutes,
                   ar.attended_slot_code,
                   ar.minutes_attended,
                   ar.status,
                   ea.reason AS excuse_reason,
                   ea.counts_against_attendance
              FROM students s
              JOIN attendance_records ar ON ar.student_id = s.id
              JOIN classes cls ON cls.id = ar.class_id
              JOIN subjects sub ON sub.id = cls.subject_id
              LEFT JOIN class_slots cs ON cs.id = cls.slot_id
              LEFT JOIN excused_absences ea ON ea.attendance_record_id = ar.id
             WHERE s.registration = %s
             ORDER BY cls.class_date DESC, sub.name
             LIMIT 12
            """,
            (registration,),
        ).fetchall()
    return filter_by_subject(serialize_rows(rows), detected_subjects)


QUERY_FUNCTIONS: dict[str, Callable[[str, list[str]], object]] = {
    "student_profile": lambda registration, subjects: fetch_student_profile(registration),
    "student_subjects": lambda registration, subjects: fetch_student_subjects(registration),
    "subject_attendance": lambda registration, subjects: fetch_subject_attendance(registration, subjects),
    "student_grades": lambda registration, subjects: fetch_student_grades(registration, subjects),
    "assessment_models": lambda registration, subjects: fetch_assessment_models(registration, subjects),
    "curriculum_rules": lambda registration, subjects: fetch_curriculum_rules(registration),
    "complementary_activities": lambda registration, subjects: fetch_complementary_activities(registration),
    "financial_records": lambda registration, subjects: fetch_financial_records(registration),
    "student_benefits": lambda registration, subjects: fetch_student_benefits(registration),
    "academic_events": lambda registration, subjects: fetch_academic_events(),
    "internships": lambda registration, subjects: fetch_internships(registration),
    "detailed_attendance": lambda registration, subjects: fetch_detailed_attendance(registration, subjects),
}


def retrieve_database_context(registration: str, query_names: list[str], detected_subjects: list[str]) -> dict:
    results = {}
    for query_name in query_names:
        callback = QUERY_FUNCTIONS.get(query_name)
        if not callback:
            continue
        results[query_name] = safe_query(query_name, lambda cb=callback: cb(registration, detected_subjects))
    return results
