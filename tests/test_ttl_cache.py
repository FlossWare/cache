"""Tests for cache_ai.ttl_cache."""

import time

from cache_ai.ttl_cache import TTLCache


def test_put_and_get():
    cache = TTLCache()
    cache.put("k1", "v1")
    assert cache.get("k1") == "v1"


def test_get_missing_key():
    cache = TTLCache()
    assert cache.get("nonexistent") is None


def test_invalidate():
    cache = TTLCache()
    cache.put("k1", "v1")
    assert cache.invalidate("k1") is True
    assert cache.get("k1") is None


def test_invalidate_missing_key():
    cache = TTLCache()
    assert cache.invalidate("nonexistent") is False


def test_clear():
    cache = TTLCache()
    cache.put("k1", "v1")
    cache.put("k2", "v2")
    cache.clear()
    assert len(cache) == 0
    assert cache.get("k1") is None


def test_ttl_expiry():
    cache = TTLCache()
    cache.put("k1", "v1", ttl=0.01)
    time.sleep(0.02)
    assert cache.get("k1") is None


def test_default_ttl():
    cache = TTLCache(default_ttl=0.01)
    cache.put("k1", "v1")
    time.sleep(0.02)
    assert cache.get("k1") is None


def test_no_ttl_never_expires():
    cache = TTLCache()
    cache.put("k1", "v1")
    assert cache.get("k1") == "v1"


def test_max_size_evicts_oldest():
    cache = TTLCache(max_size=2)
    cache.put("k1", "v1")
    cache.put("k2", "v2")
    cache.put("k3", "v3")
    assert cache.get("k1") is None
    assert cache.get("k2") == "v2"
    assert cache.get("k3") == "v3"


def test_overwrite_key():
    cache = TTLCache()
    cache.put("k1", "v1")
    cache.put("k1", "v2")
    assert cache.get("k1") == "v2"


def test_stats_hits_and_misses():
    cache = TTLCache()
    cache.put("k1", "v1")
    cache.get("k1")  # hit
    cache.get("k1")  # hit
    cache.get("k2")  # miss
    stats = cache.stats()
    assert stats.hits == 2
    assert stats.misses == 1
    assert stats.hit_rate == 2 / 3


def test_len():
    cache = TTLCache()
    cache.put("k1", "v1")
    cache.put("k2", "v2")
    assert len(cache) == 2


def test_keys():
    cache = TTLCache()
    cache.put("a", 1)
    cache.put("b", 2)
    keys = cache.keys()
    assert sorted(keys) == ["a", "b"]


def test_len_excludes_expired():
    cache = TTLCache()
    cache.put("k1", "v1", ttl=0.01)
    cache.put("k2", "v2")
    time.sleep(0.02)
    assert len(cache) == 1


def test_hit_count_tracked():
    cache = TTLCache()
    cache.put("k1", "v1")
    cache.get("k1")
    cache.get("k1")
    cache.get("k1")
    entry = cache._entries["k1"]
    assert entry.hit_count == 3


def test_clear_resets_stats():
    cache = TTLCache()
    cache.put("k1", "v1")
    cache.get("k1")
    cache.get("missing")
    cache.clear()
    stats = cache.stats()
    assert stats.hits == 0
    assert stats.misses == 0
