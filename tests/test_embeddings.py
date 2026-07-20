import numpy as np

from src.rag.embeddings import embed_query, embed_texts


def test_embed_texts_returns_normalized_float32_vectors():
    vectors = embed_texts(["hello world", "goodbye world"])

    assert vectors.dtype == np.float32
    assert vectors.shape[0] == 2
    norms = np.linalg.norm(vectors, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-5)


def test_embed_query_matches_embed_texts_single_row():
    query_vector = embed_query("hello world")
    batch_vector = embed_texts(["hello world"])[0]

    assert np.allclose(query_vector, batch_vector)
