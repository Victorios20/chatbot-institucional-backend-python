from app.errors import AppError
from app.gemini_service import generate_chat_answer
from app.rag.rag_service import build_rag_context
from app.academic_answers import structured_result, attendance_answer, clean_label
from app.chat_presentation import follow_up_suggestions
from app.chat_repository import find_chat_response, save_chat_response, save_feedback
from uuid import uuid4
from app.rag.intent_classifier import classify_intents, detect_subjects, normalize_text
from app.schemas import ChatRequest, LoginRequest
from app.security import password_matches
from app.session_store import session_store
from app.student_repository import (
    find_student_by_registration,
    get_student_context_by_registration,
    register_failure,
    reset_failures,
    validate_lock,
)


def login(request: LoginRequest) -> dict:
    registration = request.registration.strip()
    student = find_student_by_registration(registration)
    if not student:
        raise AppError(401, "INVALID_CREDENTIALS", "Registration or password is invalid")

    try:
        validate_lock(student)
    except AppError as exc:
        raise AppError(exc.status_code, "INVALID_CREDENTIALS", "Registration or password is invalid") from exc

    if not password_matches(request.password, student["password_hash"]):
        register_failure(student)
        raise AppError(401, "INVALID_CREDENTIALS", "Registration or password is invalid")

    reset_failures(student["id"])
    student_context = get_student_context_by_registration(registration)
    session = session_store.create(student_context)
    return {"sessionId": session.session_id}


def send_message(request: ChatRequest) -> dict:
    session = session_store.get(request.sessionId.strip())
    message = request.message.strip()
    registration = session.student_context['registration']
    request_id = getattr(request, 'requestId', None) or uuid4()
    cached = find_chat_response(registration, request_id, message)
    if cached:
        return cached
    names = {i.name for i in classify_intents(message)}
    presentation = None
    academic = {}
    detected = []
    answer = None
    if 'attendance' in names and not names & {'grades', 'pmg', 'financial', 'calendar', 'history'}:
        fresh = get_student_context_by_registration(session.student_context['registration'])
        detected = detect_subjects(message, fresh)
        normalized = normalize_text(message)
        if not detected and (normalized.startswith('e ') or any(w in normalized.split() for w in ('nela', 'nessa', 'dela'))):
            for previous in reversed(session.history):
                if previous.sender == 'STUDENT':
                    detected = detect_subjects(previous.content, fresh)
                    if detected: break
        answer = attendance_answer(message, fresh, detected)
    if answer is None:
        rag_context = build_rag_context(message, session.student_context, session.history)
        result = structured_result(message, rag_context, session.student_context)
        answer = result.text if result else None
        presentation = result.presentation if result else None
        academic = rag_context.get('databaseQueries', {}).get('academic', {}).get('data', {})
        detected = rag_context.get('detectedSubjects', [])
        names = {i['name'] for i in rag_context.get('intents', [])}
        if answer is None:
            answer = generate_chat_answer(message, session.student_context, rag_context=rag_context, history=session.history)
    answer = clean_label(answer)
    answer = answer[:1].upper() + answer[1:]
    suggestions = [s for s in follow_up_suggestions(names, detected, academic) if normalize_text(s) != normalize_text(message)][:3]
    reply, created = save_chat_response(registration, request_id, message, answer, presentation, suggestions)
    if created:
        session_store.add_message(session, "STUDENT", message)
        session_store.add_message(session, "ASSISTANT", answer)
    return reply


def get_chat_session(session_id):
    student = session_store.get(session_id.strip()).student_context
    course = student.get('course', {})
    return {'student': {'fullName': student['fullName'], 'courseName': course.get('name'), 'semester': course.get('currentSemester')}}


def submit_feedback(request):
    session = session_store.get(request.sessionId.strip())
    return save_feedback(session.student_context['registration'], request.messageId, request.rating)
