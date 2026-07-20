from src.config import settings


def test_defaults():
    assert settings.ollama_model == "llama3.2:3b"
    assert settings.retrieval_top_k == 5
    assert settings.app_env == "development"


def test_paths_resolve_absolute():
    assert settings.faiss_index_path.is_absolute()
    assert settings.faiss_metadata_path.is_absolute()
    assert settings.trace_db_path.is_absolute()
