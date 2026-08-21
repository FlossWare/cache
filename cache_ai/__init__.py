"""cache-ai -- Prompt caching, TTL caching, and provider-specific cache hints.

Public API
----------
Types:
    CacheStats, CacheEntry, ChatMessage, ChatResponse

Protocols:
    CachePolicy, CacheBackend, LLMBackend

Cache:
    PromptCachePolicy

TTL Cache:
    TTLCache

Providers:
    apply_anthropic_hints, apply_openai_hints, apply_google_hints,
    apply_provider_hints

Decorators (ADR-0006):
    with_prompt_cache, cacheable
"""

from __future__ import annotations

from cache_ai.cache import PromptCachePolicy
from cache_ai.decorators import cacheable, with_prompt_cache
from cache_ai.protocols import CacheBackend, CachePolicy, LLMBackend
from cache_ai.providers import (
    apply_anthropic_hints,
    apply_google_hints,
    apply_openai_hints,
    apply_provider_hints,
)
from cache_ai.ttl_cache import TTLCache
from cache_ai.types import CacheEntry, CacheStats, ChatMessage, ChatResponse

__all__ = [
    "CacheBackend",
    "CacheEntry",
    "CachePolicy",
    "CacheStats",
    "ChatMessage",
    "ChatResponse",
    "LLMBackend",
    "PromptCachePolicy",
    "TTLCache",
    "apply_anthropic_hints",
    "apply_google_hints",
    "apply_openai_hints",
    "apply_provider_hints",
    "cacheable",
    "with_prompt_cache",
]

__version__ = "0.1"
