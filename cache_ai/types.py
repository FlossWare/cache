"""Data models for cache-ai.

All models are plain dataclasses with no imports outside the standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CacheStats:
    """Cache utilization statistics."""

    hits: int
    misses: int
    hit_rate: float
    tokens_saved: int = 0
    cost_saved: float = 0.0


@dataclass
class CacheEntry:
    """A single cache entry with optional TTL metadata."""

    key: str
    value: object
    created_at: float
    expires_at: float | None = None
    hit_count: int = 0


@dataclass
class ChatMessage:
    """Minimal chat message for LLM interactions."""

    role: str
    content: str


@dataclass
class ChatResponse:
    """Minimal chat response from an LLM backend."""

    content: str
    model: str = ""
    usage: dict = field(default_factory=dict)
