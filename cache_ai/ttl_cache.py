"""Generic in-memory TTL cache for cache-ai.

Provides ``TTLCache``, a thread-safe key-value cache with optional
time-to-live expiry.  Zero external dependencies -- stdlib only.
"""

from __future__ import annotations

import threading
import time
from collections import OrderedDict

from cache_ai.types import CacheEntry, CacheStats


class TTLCache:
    """Thread-safe in-memory cache with time-to-live expiry.

    Satisfies :class:`~cache_ai.protocols.CacheBackend` via structural
    subtyping.

    Parameters
    ----------
    default_ttl:
        Default time-to-live in seconds for entries that do not specify
        their own TTL.  ``None`` means entries never expire by default.
    max_size:
        Maximum number of entries.  When exceeded, the oldest entry is
        evicted.  ``None`` means unbounded.
    """

    def __init__(
        self,
        *,
        default_ttl: float | None = None,
        max_size: int | None = None,
    ) -> None:
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._lock = threading.Lock()
        self._entries: OrderedDict[str, CacheEntry] = OrderedDict()
        self._hits: int = 0
        self._misses: int = 0

    def _is_expired(self, entry: CacheEntry) -> bool:
        if entry.expires_at is None:
            return False
        return time.monotonic() > entry.expires_at

    def _evict_expired(self) -> None:
        expired = [k for k, v in self._entries.items() if self._is_expired(v)]
        for k in expired:
            del self._entries[k]

    def _evict_oldest(self) -> None:
        if self._max_size is not None and len(self._entries) >= self._max_size:
            self._entries.popitem(last=False)

    def get(self, key: str) -> object | None:
        """Return the cached value for *key*, or ``None`` if missing/expired."""
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                self._misses += 1
                return None
            if self._is_expired(entry):
                del self._entries[key]
                self._misses += 1
                return None
            self._hits += 1
            entry.hit_count += 1
            return entry.value

    def put(self, key: str, value: object, *, ttl: float | None = None) -> None:
        """Store *value* under *key* with optional TTL in seconds."""
        effective_ttl = ttl if ttl is not None else self._default_ttl
        now = time.monotonic()
        expires_at = now + effective_ttl if effective_ttl is not None else None

        with self._lock:
            self._evict_expired()
            self._evict_oldest()
            self._entries[key] = CacheEntry(
                key=key,
                value=value,
                created_at=now,
                expires_at=expires_at,
            )
            self._entries.move_to_end(key)

    def invalidate(self, key: str) -> bool:
        """Remove *key* from the cache.  Returns ``True`` if it existed."""
        with self._lock:
            return self._entries.pop(key, None) is not None

    def clear(self) -> None:
        """Remove all entries and reset statistics."""
        with self._lock:
            self._entries.clear()
            self._hits = 0
            self._misses = 0

    def stats(self) -> CacheStats:
        """Return cache utilization statistics."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0.0
            return CacheStats(
                hits=self._hits,
                misses=self._misses,
                hit_rate=hit_rate,
            )

    def __len__(self) -> int:
        with self._lock:
            self._evict_expired()
            return len(self._entries)

    def keys(self) -> list[str]:
        """Return all non-expired keys."""
        with self._lock:
            self._evict_expired()
            return list(self._entries.keys())
