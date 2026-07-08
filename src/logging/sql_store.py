"""
Persistent SQL log store for pipeline events.

Every meaningful step (node entered, retrieval performed, LLM called,
escalation triggered) is written here as a row keyed by trace_id, giving
an auditable, queryable history of every conversation the system handled.
SQLite by default (zero-ops for a single instance); swap the connection
string for Postgres later without touching call sites.
"""
from __future__ import annotations

import datetime as dt
import json
from typing import Any

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import settings

Base = declarative_base()


class TraceEvent(Base):
    __tablename__ = "trace_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String(32), index=True, nullable=False)
    node = Column(String(64), nullable=False)
    event = Column(String(64), nullable=False)
    payload = Column(Text, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow, index=True)


def _make_engine():
    settings.trace_db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{settings.trace_db_path}", future=True)


_engine = _make_engine()
_SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False, future=True)


def init_db() -> None:
    Base.metadata.create_all(_engine)


def log_event(trace_id: str, node: str, event: str, payload: dict[str, Any] | None = None) -> None:
    init_db()
    with _SessionLocal() as session:
        session.add(
            TraceEvent(
                trace_id=trace_id,
                node=node,
                event=event,
                payload=json.dumps(payload or {}, default=str),
            )
        )
        session.commit()


def get_trace_history(trace_id: str) -> list[dict[str, Any]]:
    init_db()
    with _SessionLocal() as session:
        rows = (
            session.query(TraceEvent)
            .filter(TraceEvent.trace_id == trace_id)
            .order_by(TraceEvent.created_at.asc())
            .all()
        )
        return [
            {
                "node": r.node,
                "event": r.event,
                "payload": json.loads(r.payload) if r.payload else {},
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
