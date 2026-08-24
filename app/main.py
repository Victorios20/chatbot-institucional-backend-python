from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.chatbot_service import login, send_message
from app.config import settings
from app.erp_auth_service import context_from_token, erp_login, erp_refresh
from app.errors import AppError, app_error_handler, error_body
from app.schemas import ChatRequest, LoginRequest, RefreshTokenRequest

app = FastAPI(title="Backend Python - Chatbot Institucional")

app.add_exception_handler(AppError, app_error_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_origin, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def generic_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=error_body(500, "INTERNAL_ERROR", "Unexpected internal error", request.url.path),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    message = ", ".join(
        f"{'.'.join(str(part) for part in error['loc'][1:])}: {error['msg']}"
        for error in exc.errors()
    )
    return JSONResponse(
        status_code=400,
        content=error_body(400, "VALIDATION_ERROR", message or "Invalid request body", request.url.path),
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/auth/login")
def public_login(request: LoginRequest) -> dict:
    return login(request)


@app.post("/chat/message")
def public_chat_message(request: ChatRequest) -> dict:
    return send_message(request)


@app.post("/erp/auth/login")
def erp_public_login(request: LoginRequest) -> dict:
    return erp_login(request.registration.strip(), request.password)


@app.post("/auth/refresh")
@app.post("/erp/auth/refresh")
def refresh(request: RefreshTokenRequest) -> dict:
    return erp_refresh(request.refreshToken)


@app.get("/students/me/context")
@app.get("/erp/students/me/context")
def student_context(authorization: str | None = Header(default=None)) -> dict:
    return context_from_token(authorization)
