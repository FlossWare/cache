"""Tests for cache_ai.decorators."""

import time

import pytest

from cache_ai.cache import PromptCachePolicy
from cache_ai.decorators import cacheable, with_prompt_cache
from cache_ai.ttl_cache import TTLCache


@pytest.mark.asyncio
async def test_with_prompt_cache_applies_hints():
    policy = PromptCachePolicy()

    @with_prompt_cache(provider="anthropic", policy=policy)
    async def chat(messages, *, model="default"):
        return messages

    messages = [{"role": "system", "content": "sys"}, {"role": "user", "content": "hi"}]
    result = await chat(messages)
    assert result[0]["cache_control"] == {"type": "ephemeral"}


@pytest.mark.asyncio
async def test_with_prompt_cache_kwargs():
    policy = PromptCachePolicy()

    @with_prompt_cache(provider="anthropic", policy=policy)
    async def chat(*, messages, model="default"):
        return messages

    messages = [{"role": "system", "content": "sys"}]
    result = await chat(messages=messages)
    assert result[0]["cache_control"] == {"type": "ephemeral"}


@pytest.mark.asyncio
async def test_with_prompt_cache_tracks_stats():
    policy = PromptCachePolicy()

    @with_prompt_cache(provider="openai", policy=policy)
    async def chat(messages, *, model="default"):
        return messages

    msgs = [{"role": "user", "content": "hello"}]
    await chat(msgs)
    await chat(msgs)
    stats = await policy.cache_stats()
    assert stats.hits == 1
    assert stats.misses == 1


def test_with_prompt_cache_exposes_policy():
    policy = PromptCachePolicy()

    @with_prompt_cache(provider="openai", policy=policy)
    async def chat(messages):
        return messages

    assert chat._cache_policy is policy


def test_with_prompt_cache_default_policy():
    @with_prompt_cache(provider="openai")
    async def chat(messages):
        return messages

    assert hasattr(chat, "_cache_policy")
    assert isinstance(chat._cache_policy, PromptCachePolicy)


def test_cacheable_sync():
    call_count = 0

    @cacheable()
    def add(a, b):
        nonlocal call_count
        call_count += 1
        return a + b

    assert add(1, 2) == 3
    assert add(1, 2) == 3
    assert call_count == 1


@pytest.mark.asyncio
async def test_cacheable_async():
    call_count = 0

    @cacheable()
    async def add(a, b):
        nonlocal call_count
        call_count += 1
        return a + b

    assert await add(1, 2) == 3
    assert await add(1, 2) == 3
    assert call_count == 1


def test_cacheable_different_args_not_cached():
    call_count = 0

    @cacheable()
    def add(a, b):
        nonlocal call_count
        call_count += 1
        return a + b

    assert add(1, 2) == 3
    assert add(3, 4) == 7
    assert call_count == 2


def test_cacheable_with_ttl():
    @cacheable(ttl=0.01)
    def expensive():
        return "result"

    assert expensive() == "result"
    time.sleep(0.02)
    assert expensive() == "result"


def test_cacheable_with_custom_key_fn():
    call_count = 0

    @cacheable(key_fn=lambda x: str(x % 2))
    def parity(x):
        nonlocal call_count
        call_count += 1
        return x % 2

    parity(2)
    parity(4)
    assert call_count == 1


def test_cacheable_shared_cache():
    cache = TTLCache()

    @cacheable(cache=cache)
    def f(x):
        return x * 2

    f(5)
    stats = cache.stats()
    assert stats.misses == 1


def test_cacheable_exposes_cache():
    @cacheable()
    def f(x):
        return x

    assert hasattr(f, "_cache")
    assert isinstance(f._cache, TTLCache)
