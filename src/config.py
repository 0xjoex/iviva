"""
Centralized application configuration.

Everything reads from environment variables (via .env in dev), so the same
code runs unmodified in local dev, CI, and prod — only the environment
differs.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    # LLM
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    ollama_temperature: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))

    # Embeddings
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # RAG
    faiss_index_path: Path = field(
        default_factory=lambda: BASE_DIR / os.getenv("FAISS_INDEX_PATH", "data/index/faiss.index")
    )
    faiss_metadata_path: Path = field(
        default_factory=lambda: BASE_DIR / os.getenv("FAISS_METADATA_PATH", "data/index/metadata.json")
    )
    retrieval_top_k: int = int(os.getenv("RETRIEVAL_TOP_K", "5"))

    # Tracing
    trace_db_path: Path = field(
        default_factory=lambda: BASE_DIR / os.getenv("TRACE_DB_PATH", "data/logs/traces.db")
    )

    # CRM
    crm_api_base_url: str = os.getenv("CRM_API_BASE_URL", "https://api.example-crm.com/v1")
    crm_api_key: str = os.getenv("CRM_API_KEY", "changeme")
    crm_webhook_timeout_seconds: float = float(os.getenv("CRM_WEBHOOK_TIMEOUT_SECONDS", "5"))

    # App
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()