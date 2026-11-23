"""A tiny client for the assistant API. The UI talks to the backend ONLY through this class."""

from __future__ import annotations

from dataclasses import dataclass, field

import httpx


@dataclass
class ChatResult:
    ok: bool
    answer: str = ""
    intent: str = ""
    sources: list[dict] = field(default_factory=list)
    path: str = ""
    escalate: bool = False
    degraded: bool = False
    request_id: str = ""
    error: str = ""  # human-readable message when ok is False


class AssistantClient:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        timeout_s: float = 20.0,
        transport: httpx.BaseTransport | None = None,
    ):
        self._http = httpx.Client(base_url=base_url, timeout=timeout_s, transport=transport)

    def ask(self, message: str, session_id: str) -> ChatResult:
        try:
            r = self._http.post("/v1/chat", json={"message": message, "session_id": session_id})
        except httpx.TimeoutException:
            return ChatResult(ok=False, error="The assistant is taking too long. Please try again.")
        except httpx.HTTPError:
            return ChatResult(ok=False, error="Cannot reach the assistant. Is the backend running?")
        if r.status_code == 422:
            return ChatResult(ok=False, error="Please type a question (1–2000 characters).")
        if r.status_code == 429:
            return ChatResult(ok=False, error="Too many questions in a short time. Please wait a minute.")
        if r.status_code != 200:
            return ChatResult(ok=False, error=f"Something went wrong on our side (error {r.status_code}).")
        d = r.json()
        return ChatResult(
            ok=True,
            answer=d["answer"],
            intent=d["intent"],
            sources=d.get("sources", []),
            path=d.get("path", ""),
            escalate=d.get("escalate", False),
            degraded=d.get("degraded", False),
            request_id=d["request_id"],
        )

    def send_feedback(self, request_id: str, rating: int, comment: str | None = None) -> bool:
        try:
            r = self._http.post("/v1/feedback", json={"request_id": request_id, "rating": rating, "comment": comment})
        except httpx.HTTPError:
            return False
        return r.status_code == 201

    def healthy(self) -> bool:
        try:
            return self._http.get("/health").status_code == 200
        except httpx.HTTPError:
            return False
