"""Prompt-cache policy backend for cache-ai.

Provides ``PromptCachePolicy``, a zero-dependency implementation that
adds provider-specific cache-control hints to message lists and tracks
hit/miss statistics via content hashing.
"""

from __future__ import annotations

import hashlib
import json
import threading

from cache_ai.providers import apply_provider_hints
from cache_ai.types import CacheStats


def _content_hash(messages: list[dict]) -> str:
    """Return a deterministic SHA-256 hex digest for *messages*."""
    serialised = json.dumps(messages, sort_keys=True, default=str)
    return hashlib.sha256(serialised.encode()).hexdigest()  # noqa: S324


class PromptCachePolicy:
    """Adds provider-specific cache hints and tracks cache statistics.

    Satisfies :class:`~cache_ai.protocols.CachePolicy` via structural
    subtyping.  Thread-safe via a single lock.

    Cache-hit detection works by hashing the full message list: if the
    same content hash has been seen before, it counts as a hit;
    otherwise it is a miss.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._seen_hashes: set[str] = set()
        self._hits: int = 0
        self._misses: int = 0

    def apply_cache_hints(self, messages: list[dict], *, provider: str) -> list[dict]:
        """Annotate *messages* with cache-control hints for *provider*.

        Supported providers: ``anthropic``, ``openai``, ``google``/``gemini``.
        Unknown providers get an unmodified shallow copy.  A content hash
        is tracked for hit/miss statistics.
        """
        content_hash = _content_hash(messages)

        with self._lock:
            if content_hash in self._seen_hashes:
                self._hits += 1
            else:
                self._seen_hashes.add(content_hash)
                self._misses += 1

        return apply_provider_hints(messages, provider)

    async def cache_stats(self) -> CacheStats:
        """Return current cache utilization statistics."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0.0
            return CacheStats(
                hits=self._hits,
                misses=self._misses,
                hit_rate=hit_rate,
                tokens_saved=0,
                cost_saved=0.0,
            )
