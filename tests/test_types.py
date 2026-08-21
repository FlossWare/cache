"""Tests for cache_ai.types."""

from cache_ai.types import CacheEntry, CacheStats, ChatMessage, ChatResponse


def test_cache_stats_defaults():
    stats = CacheStats(hits=5, misses=3, hit_rate=0.625)
    assert stats.hits == 5
    assert stats.misses == 3
    assert stats.hit_rate == 0.625
    assert stats.tokens_saved == 0
    assert stats.cost_saved == 0.0


def test_cache_stats_with_savings():
    stats = CacheStats(hits=10, misses=2, hit_rate=0.833, tokens_saved=5000, cost_saved=0.05)
    assert stats.tokens_saved == 5000
    assert stats.cost_saved == 0.05


def test_cache_entry_no_expiry():
    entry = CacheEntry(key="k1", value="v1", created_at=100.0)
    assert entry.key == "k1"
    assert entry.value == "v1"
    assert entry.expires_at is None
    assert entry.hit_count == 0


def test_cache_entry_with_expiry():
    entry = CacheEntry(key="k2", value=42, created_at=100.0, expires_at=200.0)
    assert entry.expires_at == 200.0


def test_chat_message():
    msg = ChatMessage(role="user", content="hello")
    assert msg.role == "user"
    assert msg.content == "hello"


def test_chat_response_defaults():
    resp = ChatResponse(content="hi")
    assert resp.content == "hi"
    assert resp.model == ""
    assert resp.usage == {}


def test_chat_response_with_model():
    resp = ChatResponse(content="done", model="gpt-4o", usage={"total_tokens": 50})
    assert resp.model == "gpt-4o"
    assert resp.usage["total_tokens"] == 50
