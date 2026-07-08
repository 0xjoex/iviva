"""
Trace ID generation and propagation.

A single trace_id is minted when a query enters the system and is threaded
through every node in the LangGraph pipeline, every retrieval call, and
every LLM call - so you can reconstruct "what happened for this one
customer message" after the fact.
"""
from __future__ import annotations

import contextvars
import logging
import uuid

_trace_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "trace_id", default="untraced"
)


def new_trace_id() -> str:
    """Mint a new trace ID and bind it to the current context."""
    trace_id = uuid.uuid4().hex[:16]
    _trace_id_ctx.set(trace_id)
    return trace_id


def get_trace_id() -> str:
    return _trace_id_ctx.get()


def bind_trace_id(trace_id: str) -> None:
    _trace_id_ctx.set(trace_id)


class TraceIdFilter(logging.Filter):
    """Injects the current trace_id into every log record automatically."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = get_trace_id()
        return True


def get_logger(name: str) -> logging.Logger:
    """
    Root/child logger factory. All loggers are children of "rag_pipeline",
    so one handler config controls the whole app's log format/output,
    while each module still gets its own named child logger.
    """
    return logging.getLogger(f"rag_pipeline.{name}")


def configure_logging(level: str = "INFO") -> None:
    root = logging.getLogger("rag_pipeline")
    root.setLevel(level)

    if root.handlers:
        return

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | trace=%(trace_id)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    handler.addFilter(TraceIdFilter())
    root.addHandler(handler)
