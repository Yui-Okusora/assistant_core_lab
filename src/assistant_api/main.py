"""FastAPI application:  uvicorn assistant_api.main:create_app --factory --reload

Endpoints (v1): GET /health, POST /v1/chat, POST /v1/feedback, GET /v1/feedback (admin), GET /v1/weather
"""

from __future__ import annotations

import time
import uuid

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from assistant_api.db import Repository, init_db, make_engine
from assistant_api.ratelimit import RateLimiter
from assistant_api.schemas import ChatRequest, ChatResponse, ErrorResponse, FeedbackIn, FeedbackOut, Weather
from assistant_api.weather import ExternalServiceError, WeatherClient
from assistant_core import AssistantService, Message, build_service
from assistant_core.config import Settings, load_settings


def create_app(
    settings: Settings | None = None,
    service: AssistantService | None = None,
    weather: WeatherClient | None = None,
    repo: Repository | None = None,
) -> FastAPI:
    settings = settings or load_settings()
    service = service or build_service(settings)
    weather = weather or WeatherClient(
        settings.weather_url, settings.campus_lat, settings.campus_lon, timeout_s=settings.weather_timeout_s
    )
    limiter = RateLimiter(settings.rate_limit_per_min)
    if repo is None:
        engine = make_engine(settings.database_url)
        init_db(engine)
        repo = Repository(engine, settings.session_salt)

    app = FastAPI(
        title="Study Assistant API", version="1.0.0", description="Backend of the CSC10014 Smart Virtual Assistant."
    )

    def error(code: int, key: str, message: str) -> JSONResponse:
        return JSONResponse(status_code=code, content={"error": {"code": key, "message": message}})

    @app.exception_handler(RequestValidationError)
    async def on_validation(_: Request, exc: RequestValidationError):
        first = exc.errors()[0]
        field = ".".join(str(p) for p in first["loc"][1:]) or "body"
        return error(422, "invalid_request", f"{field}: {first['msg']}")

    @app.exception_handler(HTTPException)
    async def on_http(_: Request, exc: HTTPException):
        return error(exc.status_code, str(exc.detail).lower().replace(" ", "_"), str(exc.detail))

    def require_admin(x_api_key: str | None = Header(default=None)) -> None:
        if not settings.api_admin_key or x_api_key != settings.api_admin_key:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing or invalid API key")

    @app.get("/health", tags=["ops"])
    def health() -> dict:
        return {"status": "ok", "version": app.version}

    @app.post(
        "/v1/chat",
        response_model=ChatResponse,
        tags=["chat"],
        responses={422: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
    )
    def chat(req: ChatRequest, request: Request) -> ChatResponse:
        client = request.client.host if request.client else "unknown"
        if not limiter.allow(client):
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many requests")
        start = time.perf_counter()
        resp = service.handle(Message(text=req.message, session_id=req.session_id))
        request_id = uuid.uuid4().hex[:12]
        repo.record_interaction(
            req.session_id,
            request_id,
            resp.intent.value,
            topic=resp.sources[0].id if resp.sources else None,
            resolved=resp.intent.value != "unknown",
            degraded=resp.degraded,
            latency_ms=round((time.perf_counter() - start) * 1000, 2),
        )
        return ChatResponse(**resp.model_dump(), request_id=request_id)

    @app.post(
        "/v1/feedback",
        response_model=FeedbackOut,
        status_code=201,
        tags=["feedback"],
        responses={404: {"model": ErrorResponse}},
    )
    def add_feedback(fb: FeedbackIn) -> FeedbackOut:
        saved = repo.add_feedback(fb.request_id, fb.rating, fb.comment)
        if saved is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Unknown request id")
        return FeedbackOut.model_validate(saved, from_attributes=True)

    @app.get("/v1/feedback", response_model=list[FeedbackOut], tags=["feedback"], dependencies=[Depends(require_admin)])
    def list_feedback(limit: int = 100) -> list[FeedbackOut]:
        return [FeedbackOut.model_validate(f, from_attributes=True) for f in repo.list_feedback(limit)]

    @app.get("/v1/stats/intents", tags=["stats"], dependencies=[Depends(require_admin)])
    def intent_stats() -> list[dict]:
        return repo.intent_stats()

    @app.get("/v1/weather", response_model=Weather, tags=["external"], responses={503: {"model": ErrorResponse}})
    def campus_weather() -> Weather:
        try:
            return weather.current()
        except ExternalServiceError:
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Weather service unavailable") from None

    return app
