"""Durable answers and evaluations, always scoped to the authenticated student."""
from uuid import uuid4
from psycopg.types.json import Jsonb
from app.database import get_connection
from app.errors import AppError


def _reply(row):
    return {'messageId': str(row['id']), 'response': row['answer'], 'presentation': row['presentation'], 'suggestions': row['suggestions']}


def _check_question(row, question):
    if row['question'] != question:
        raise AppError(409, 'REQUEST_CONFLICT', 'Essa identificação de mensagem já foi usada. Envie uma nova pergunta.')


def find_chat_response(registration, request_id, question):
    with get_connection() as conn:
        row = conn.execute("""SELECT r.* FROM chatbot_responses r JOIN students s ON s.id=r.student_id
                              WHERE s.registration=%s AND r.request_id=%s""", (registration, request_id)).fetchone()
    if row:
        _check_question(row, question)
        return _reply(row)
    return None


def save_chat_response(registration, request_id, question, answer, presentation, suggestions):
    with get_connection() as conn:
        row = conn.execute("""INSERT INTO chatbot_responses(id, student_id, request_id, question, answer, presentation, suggestions)
            SELECT %s, s.id, %s, %s, %s, %s, %s FROM students s WHERE s.registration=%s
            ON CONFLICT(student_id, request_id) DO NOTHING RETURNING *""",
            (uuid4(), request_id, question, answer, Jsonb(presentation) if presentation else None, Jsonb(suggestions), registration)).fetchone()
        created = row is not None
        if not row:
            row = conn.execute("""SELECT r.* FROM chatbot_responses r JOIN students s ON s.id=r.student_id
                WHERE s.registration=%s AND r.request_id=%s""", (registration, request_id)).fetchone()
        if not row:
            raise AppError(404, 'STUDENT_NOT_FOUND', 'Cadastro acadêmico não encontrado.')
        _check_question(row, question)
    return _reply(row), created


def save_feedback(registration, response_id, rating):
    with get_connection() as conn:
        row = conn.execute("""INSERT INTO chatbot_response_feedback(response_id, rating)
            SELECT r.id, %s FROM chatbot_responses r JOIN students s ON s.id=r.student_id
            WHERE r.id=%s AND s.registration=%s
            ON CONFLICT(response_id) DO UPDATE SET rating=EXCLUDED.rating, updated_at=now()
            RETURNING rating""", (rating, response_id, registration)).fetchone()
        if not row:
            raise AppError(404, 'RESPONSE_NOT_FOUND', 'Resposta não encontrada para esta sessão.')
    return {'rating': row['rating']}
