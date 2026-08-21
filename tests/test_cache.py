"""Tests for cache_ai.cache."""

import pytest

from cache_ai.cache import PromptCachePolicy, _content_hash


def test_content_hash_deterministic():
    msgs = [{"role": "user", "content": "hello"}]
    h1 = _content_hash(msgs)
    h2 = _content_hash(msgs)
    assert h1 == h2


def test_content_hash_key_order_invariant():
    msgs1 = [{"content": "hello", "role": "user"}]
    msgs2 = [{"role": "user", "content": "hello"}]
    assert _content_hash(msgs1) == _content_hash(msgs2)


def test_content_hash_different_messages():
    msgs1 = [{"role": "user", "content": "hello"}]
    msgs2 = [{"role": "user", "content": "world"}]
    assert _content_hash(msgs1) != _content_hash(msgs2)


@pytest.mark.asyncio
async def test_policy_first_call_is_miss():
    policy = PromptCachePolicy()
    msgs = [{"role": "user", "content": "test"}]
    policy.apply_cache_hints(msgs, provider="openai")
    stats = await policy.cache_stats()
    assert stats.misses == 1
    assert stats.hits == 0


@pytest.mark.asyncio
async def test_policy_second_call_same_messages_is_hit():
    policy = PromptCachePolicy()
    msgs = [{"role": "user", "content": "test"}]
    policy.apply_cache_hints(msgs, provider="openai")
    policy.apply_cache_hints(msgs, provider="openai")
    stats = await policy.cache_stats()
    assert stats.hits == 1
    assert stats.misses == 1
    assert stats.hit_rate == 0.5


@pytest.mark.asyncio
async def test_policy_different_messages_are_misses():
    policy = PromptCachePolicy()
    policy.apply_cache_hints([{"role": "user", "content": "a"}], provider="openai")
    policy.apply_cache_hints([{"role": "user", "content": "b"}], provider="openai")
    stats = await policy.cache_stats()
    assert stats.misses == 2
    assert stats.hits == 0


def test_policy_applies_anthropic_hints():
    policy = PromptCachePolicy()
    msgs = [{"role": "system", "content": "sys"}, {"role": "user", "content": "hi"}]
    result = policy.apply_cache_hints(msgs, provider="anthropic")
    assert result[0]["cache_control"] == {"type": "ephemeral"}
    assert "cache_control" not in result[1]


def test_policy_applies_openai_hints():
    policy = PromptCachePolicy()
    msgs = [{"role": "system", "content": "sys"}]
    result = policy.apply_cache_hints(msgs, provider="openai")
    assert "cache_control" not in result[0]


@pytest.mark.asyncio
async def test_policy_empty_stats():
    policy = PromptCachePolicy()
    stats = await policy.cache_stats()
    assert stats.hits == 0
    assert stats.misses == 0
    assert stats.hit_rate == 0.0


@pytest.mark.asyncio
async def test_policy_multiple_hits():
    policy = PromptCachePolicy()
    msgs = [{"role": "user", "content": "repeat"}]
    for _ in range(5):
        policy.apply_cache_hints(msgs, provider="openai")
    stats = await policy.cache_stats()
    assert stats.hits == 4
    assert stats.misses == 1
    assert stats.hit_rate == 0.8
