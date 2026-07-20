"""
FastAPI application entrypoint.
"""
from __future__ import annotations

from fastapi import FastAPI

from src.config import settings
from src.logging.sql_store import log_event
from src.logging.trace import configure_logging, get_logger, new_trace_id

configure_logging(settings.log_level)
logger = get_logger("api")

app = FastAPI(title="iviva", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "env": settings.app_env}


@app.post("/messages")
def receive_message(payload: dict) -> dict:
    trace_id = new_trace_id()
    logger.info("message received")
    log_event(trace_id, "api", "message_received", payload)
    return {"trace_id": trace_id, "status": "received"}
