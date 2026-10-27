from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from app.errors import AppError


@dataclass
class ChatMessage:
    sender: str
    content: str
    created_at: datetime


@dataclass
class StudentSession:
    session_id: str
    student_context: dict
    history: list[ChatMessage] = field(default_factory=list)


class InMemorySessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, StudentSession] = {}

    def create(self, student_context: dict) -> StudentSession:
        session = StudentSession(session_id=str(uuid4()), student_context=student_context)
        self.save(session)
        return session

    def save(self, session: StudentSession) -> None:
        self._sessions[session.session_id] = session

    def get(self, session_id: str) -> StudentSession:
        session = self._sessions.get(session_id)
        if not session:
            raise AppError(404, "SESSION_NOT_FOUND", f"Session {session_id} was not found or expired")
        return session

    def add_message(self, session: StudentSession, sender: str, content: str) -> None:
        session.history.append(ChatMessage(sender=sender, content=content, created_at=datetime.now(UTC)))
        session.history[:] = session.history[-24:]
        self.save(session)


session_store = InMemorySessionStore()
