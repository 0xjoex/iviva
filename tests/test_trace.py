import logging

from src.logging.trace import TraceIdFilter, bind_trace_id, get_trace_id, new_trace_id


def test_new_trace_id_is_16_char_hex():
    trace_id = new_trace_id()
    assert len(trace_id) == 16
    int(trace_id, 16)


def test_bind_and_get_trace_id():
    bind_trace_id("abc123")
    assert get_trace_id() == "abc123"


def test_trace_id_filter_injects_current_trace_id():
    bind_trace_id("deadbeef12345678")
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "msg", None, None)

    assert TraceIdFilter().filter(record) is True
    assert record.trace_id == "deadbeef12345678"
