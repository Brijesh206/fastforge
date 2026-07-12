"""Tests for logging context."""

from fastforge_logging.context import bind_log_context, clear_log_context, get_log_context


def test_bind_log_context_merges_context_values() -> None:
    clear_log_context()
    bind_log_context(request_id="req_123")
    context = bind_log_context(user_id="user_123")

    assert context.request_id == "req_123"
    assert context.user_id == "user_123"
    assert get_log_context().to_dict() == {
        "request_id": "req_123",
        "user_id": "user_123",
    }


def test_clear_log_context_removes_values() -> None:
    bind_log_context(request_id="req_123")
    clear_log_context()

    assert get_log_context().to_dict() == {}
