"""Protocols for cache-ai (ADR-0020: Capability-Protocol Separation).

Defines structural interfaces that any conforming object can satisfy
without inheritance.  All protocols are runtime-checkable.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from cache_ai.types import CacheStats


@runtime_checkable
class CachePolicy(Protocol):
    """Protocol for prompt-cache policies that annotate messages."""

    def apply_cache_hints(
        self, messages: list[dict], *, provider: str
    ) -> list[dict]: ...

    async def cache_stats(self) -> CacheStats: ...


@runtime_checkable
class CacheBackend(Protocol):
    """Protocol for generic key-value cache backends with TTL."""

    def get(self, key: str) -> object | None: ...

    def put(self, key: str, value: object, *, ttl: float | None = None) -> None: ...

    def invalidate(self, key: str) -> bool: ...

    def clear(self) -> None: ...

    def stats(self) -> CacheStats: ...


@runtime_checkable
class LLMBackend(Protocol):
    """Minimal LLM backend protocol for decorator integration."""

    async def chat(
        self,
        messages: list[dict],
        *,
        model: str = "",
    ) -> object: ...
