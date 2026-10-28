from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    registration: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    sessionId: str


class ChatRequest(BaseModel):
    sessionId: str = Field(min_length=1)
    message: str = Field(min_length=1, max_length=4000)
    requestId: UUID | None = None

    @field_validator('message')
    @classmethod
    def non_blank(cls, value):
        if not value.strip(): raise ValueError('Informe uma mensagem.')
        return value.strip()


class PresentationField(BaseModel):
    label: str
    value: str
    pending: bool = False
    emphasis: bool = False


class PresentationStatus(BaseModel):
    label: str
    tone: Literal['success', 'danger', 'neutral']


class SubjectCard(BaseModel):
    title: str
    subtitle: str
    fields: list[PresentationField]
    status: PresentationStatus
    note: str | None = None


class ChatPresentation(BaseModel):
    kind: Literal['subject-cards']
    title: str
    cards: list[SubjectCard]


class ChatResponse(BaseModel):
    response: str
    messageId: UUID
    presentation: ChatPresentation | None = None
    suggestions: list[str] = Field(default_factory=list)


class ChatFeedbackRequest(BaseModel):
    sessionId: str = Field(min_length=1, max_length=100)
    messageId: UUID
    rating: Literal['helpful', 'not_helpful']


class RefreshTokenRequest(BaseModel):
    refreshToken: str = Field(min_length=1)
