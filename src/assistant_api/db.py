"""Persistence with SQLModel (SQLAlchemy + Pydantic) — Lab 5 STARTER.

The models and `record_interaction` are given as worked examples. Complete TODO R1 and R2.

Privacy by design: we store *metadata* about interactions (intent, latency, topic, outcome),
a salted hash of the session id, and feedback. We do NOT store the raw user message.
"""

import hashlib
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import case, func
from sqlalchemy.pool import StaticPool
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_session"
    id: str = Field(primary_key=True, max_length=16)  # salted hash, never the raw id
    channel: str = Field(default="web", max_length=16)
    created_at: datetime = Field(default_factory=utcnow)
    interactions: list["Interaction"] = Relationship(back_populates="session")


class Interaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    request_id: str = Field(index=True, unique=True, max_length=32)
    session_id: str = Field(foreign_key="chat_session.id", index=True)
    intent: str = Field(index=True, max_length=16)
    topic: str | None = Field(default=None, max_length=32)  # e.g. handbook rule id
    resolved: bool = True  # False = unknown / refused / error
    degraded: bool = False
    latency_ms: float = 0.0
    created_at: datetime = Field(default_factory=utcnow, index=True)
    session: Optional["ChatSession"] = Relationship(back_populates="interactions")
    feedback: list["Feedback"] = Relationship(back_populates="interaction")


class Feedback(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    request_id: str = Field(foreign_key="interaction.request_id", index=True)
    rating: int  # -1, 0, 1 (validated at the API)
    comment: str | None = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=utcnow)
    interaction: Optional["Interaction"] = Relationship(back_populates="feedback")


def make_engine(url: str):  # noqa: ANN201
    if url in ("sqlite://", "sqlite:///:memory:"):
        return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)


def init_db(engine) -> None:
    SQLModel.metadata.create_all(engine)


def hash_session(raw: str, salt: str) -> str:
    return hashlib.sha256((salt + raw).encode()).hexdigest()[:16]


class Repository:
    """All database access goes through here — the API never writes SQL."""

    def __init__(self, engine, salt: str):
        self.engine, self.salt = engine, salt

    def record_interaction(
        self,
        raw_session: str,
        request_id: str,
        intent: str,
        topic: str | None,
        resolved: bool,
        degraded: bool,
        latency_ms: float,
    ) -> None:
        sid = hash_session(raw_session, self.salt)
        with Session(self.engine) as db:  # one transaction
            if db.get(ChatSession, sid) is None:
                db.add(ChatSession(id=sid))
            db.add(
                Interaction(
                    request_id=request_id,
                    session_id=sid,
                    intent=intent,
                    topic=topic,
                    resolved=resolved,
                    degraded=degraded,
                    latency_ms=latency_ms,
                )
            )
            db.commit()

    def add_feedback(self, request_id: str, rating: int, comment: str | None) -> Feedback | None:
        with Session(self.engine) as db:
            exists = db.exec(select(Interaction).where(Interaction.request_id == request_id)).first()
            if exists is None:
                return None          # the API turns this into 404
            # TODO R1 (4 lines) — follow record_interaction above:
            #   fb = Feedback(request_id=request_id, rating=rating, comment=comment)
            #   db.add(fb); db.commit(); db.refresh(fb)   # refresh loads the new id from the database
            #   return fb
            fb = Feedback(request_id=request_id, rating=rating, comment=comment)
            db.add(fb)
            db.commit()
            db.refresh(fb) # load the id the database just gave it
            return fb
            raise NotImplementedError("R1")

    def list_feedback(self, limit: int = 100) -> list[Feedback]:
        with Session(self.engine) as db:
            # TODO R2 (1 line): newest first, at most `limit` rows. SQL would be:
            #   SELECT * FROM feedback ORDER BY created_at DESC LIMIT ?
            # In SQLModel: select(Feedback).order_by(Feedback.created_at.desc()).limit(limit)
            raise NotImplementedError("R2")

    def intent_stats(self) -> list[dict]:
        """Requests, average latency and unresolved rate per intent."""
        with Session(self.engine) as db:
            unresolved = func.sum(case((Interaction.resolved.is_(False), 1), else_=0))
            q = (
                select(Interaction.intent, func.count(), func.avg(Interaction.latency_ms), unresolved)
                .group_by(Interaction.intent)
                .order_by(func.count().desc())
            )
            rows = db.exec(q).all()
        return [
            {"intent": i, "requests": n, "avg_latency_ms": round(avg or 0, 1), "unresolved": int(u or 0)}
            for i, n, avg, u in rows
        ]
