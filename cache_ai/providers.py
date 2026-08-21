"""Provider-specific cache hint application logic.

Each function annotates a message list with cache-control metadata
appropriate for a specific LLM provider's API.  All functions return
a shallow copy -- the caller's original list is never mutated.
"""

from __future__ import annotations


def apply_anthropic_hints(messages: list[dict]) -> list[dict]:
    """Add ``cache_control`` to system messages for the Anthropic API.

    Anthropic supports ephemeral prompt caching for system messages.
    Each system message receives ``cache_control: {"type": "ephemeral"}``.
    """
    result: list[dict] = []
    for msg in messages:
        if msg.get("role") == "system":
            annotated = {**msg, "cache_control": {"type": "ephemeral"}}
            result.append(annotated)
        else:
            result.append(msg)
    return result


def apply_openai_hints(messages: list[dict]) -> list[dict]:
    """Return messages unchanged -- OpenAI manages caching server-side."""
    return list(messages)


def apply_google_hints(messages: list[dict]) -> list[dict]:
    """Add ``cached_content`` markers for the Google Gemini API.

    Google Gemini supports context caching for system instructions and
    long context prefixes.  System messages receive a ``cached_content``
    marker.
    """
    result: list[dict] = []
    for msg in messages:
        if msg.get("role") == "system":
            annotated = {**msg, "cached_content": True}
            result.append(annotated)
        else:
            result.append(msg)
    return result


def apply_provider_hints(messages: list[dict], provider: str) -> list[dict]:
    """Dispatch to the correct hint-application function for *provider*."""
    dispatch = {
        "anthropic": apply_anthropic_hints,
        "openai": apply_openai_hints,
        "google": apply_google_hints,
        "gemini": apply_google_hints,
    }
    handler = dispatch.get(provider)
    if handler is not None:
        return handler(messages)
    return list(messages)
