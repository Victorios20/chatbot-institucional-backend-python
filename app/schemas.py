from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    registration: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    sessionId: str


class ChatRequest(BaseModel):
    sessionId: str = Field(min_length=1)
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    response: str


class RefreshTokenRequest(BaseModel):
    refreshToken: str = Field(min_length=1)
