"""Tests for cache_ai.providers."""

from cache_ai.providers import (
    apply_anthropic_hints,
    apply_google_hints,
    apply_openai_hints,
    apply_provider_hints,
)


def test_anthropic_hints_system_messages():
    messages = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello"},
    ]
    result = apply_anthropic_hints(messages)
    assert result[0]["cache_control"] == {"type": "ephemeral"}
    assert "cache_control" not in result[1]


def test_anthropic_hints_no_system():
    messages = [{"role": "user", "content": "Hello"}]
    result = apply_anthropic_hints(messages)
    assert len(result) == 1
    assert "cache_control" not in result[0]


def test_anthropic_hints_does_not_mutate_original():
    messages = [{"role": "system", "content": "sys"}]
    original = list(messages)
    apply_anthropic_hints(messages)
    assert messages == original


def test_openai_hints_returns_copy():
    messages = [{"role": "user", "content": "Hello"}]
    result = apply_openai_hints(messages)
    assert result == messages
    assert result is not messages


def test_google_hints_system_messages():
    messages = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello"},
    ]
    result = apply_google_hints(messages)
    assert result[0]["cached_content"] is True
    assert "cached_content" not in result[1]


def test_provider_dispatch_anthropic():
    msgs = [{"role": "system", "content": "sys"}]
    result = apply_provider_hints(msgs, "anthropic")
    assert "cache_control" in result[0]


def test_provider_dispatch_openai():
    msgs = [{"role": "system", "content": "sys"}]
    result = apply_provider_hints(msgs, "openai")
    assert "cache_control" not in result[0]


def test_provider_dispatch_google():
    msgs = [{"role": "system", "content": "sys"}]
    result = apply_provider_hints(msgs, "google")
    assert "cached_content" in result[0]


def test_provider_dispatch_gemini():
    msgs = [{"role": "system", "content": "sys"}]
    result = apply_provider_hints(msgs, "gemini")
    assert "cached_content" in result[0]


def test_provider_dispatch_unknown():
    msgs = [{"role": "system", "content": "sys"}]
    result = apply_provider_hints(msgs, "unknown-provider")
    assert result == msgs
    assert result is not msgs
