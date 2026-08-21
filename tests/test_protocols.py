"""Tests for cache_ai.protocols."""

from cache_ai.cache import PromptCachePolicy
from cache_ai.protocols import CacheBackend, CachePolicy, LLMBackend
from cache_ai.ttl_cache import TTLCache


def test_prompt_cache_policy_satisfies_cache_policy():
    policy = PromptCachePolicy()
    assert isinstance(policy, CachePolicy)


def test_ttl_cache_satisfies_cache_backend():
    cache = TTLCache()
    assert isinstance(cache, CacheBackend)


def test_custom_backend_satisfies_llm_backend():
    class MockLLM:
        async def chat(self, messages, *, model=""):
            return {"content": "ok"}

    mock = MockLLM()
    assert isinstance(mock, LLMBackend)


def test_non_conforming_does_not_satisfy():
    class NotACache:
        pass

    assert not isinstance(NotACache(), CacheBackend)
    assert not isinstance(NotACache(), CachePolicy)
    assert not isinstance(NotACache(), LLMBackend)
