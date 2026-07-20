import importlib

import pytest


@pytest.fixture
def sql_store(monkeypatch, tmp_path):
    monkeypatch.setenv("TRACE_DB_PATH", str(tmp_path / "traces.db"))

    import src.config as config_module
    import src.logging.sql_store as sql_store_module

    importlib.reload(config_module)
    importlib.reload(sql_store_module)
    return sql_store_module


def test_log_event_and_get_trace_history(sql_store):
    sql_store.log_event("trace-1", "retriever", "started", {"query": "hello"})
    sql_store.log_event("trace-1", "retriever", "finished", {"hits": 3})
    sql_store.log_event("trace-2", "retriever", "started", {})

    history = sql_store.get_trace_history("trace-1")

    assert len(history) == 2
    assert history[0]["node"] == "retriever"
    assert history[0]["event"] == "started"
    assert history[0]["payload"] == {"query": "hello"}
    assert history[1]["event"] == "finished"
    assert history[1]["payload"] == {"hits": 3}


def test_get_trace_history_returns_empty_for_unknown_trace(sql_store):
    assert sql_store.get_trace_history("nonexistent") == []
