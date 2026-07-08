"""
Text -> vector embeddings, using a small local model (no API calls, no cost).

FAISS can only compare numbers, not text. This module turns text into a
fixed-length vector such that texts with similar meaning end up with
similar vectors - that's what makes semantic search possible.
"""
from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

from src.config import settings

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    return vectors.astype("float32")


def embed_query(text: str) -> np.ndarray:
    return embed_texts([text])[0]
