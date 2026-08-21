#!/usr/bin/env python3
"""Verify cache-ai installation and run a quick smoke test."""
import sys


def main():
    try:
        from cache_ai import (
            CacheBackend,
            CacheEntry,
            CachePolicy,
            CacheStats,
            ChatMessage,
            ChatResponse,
            LLMBackend,
            PromptCachePolicy,
            TTLCache,
            apply_anthropic_hints,
            apply_google_hints,
            apply_openai_hints,
            apply_provider_hints,
            cacheable,
            with_prompt_cache,
        )
    except ImportError as e:
        print(f"FAIL: Could not import cache_ai: {e}")
        print("Install: pip install 'git+https://github.com/FlossWare/cache-ai.git'")
        sys.exit(1)

    import cache_ai

    print(f"cache-ai v{cache_ai.__version__} installed successfully")
    print(f"Exports: {len(cache_ai.__all__)} public symbols")

    # Smoke test: prompt cache policy
    policy = PromptCachePolicy()
    msgs = [{"role": "system", "content": "sys"}, {"role": "user", "content": "hi"}]
    result = policy.apply_cache_hints(msgs, provider="anthropic")
    assert "cache_control" in result[0], "Anthropic hints not applied"
    print("Smoke test: PromptCachePolicy applies Anthropic hints")

    # Smoke test: TTL cache
    cache = TTLCache(default_ttl=60)
    cache.put("test", "value")
    assert cache.get("test") == "value", "TTL cache get/put failed"
    print("Smoke test: TTLCache put/get works")

    # Smoke test: decorators are callable
    assert callable(with_prompt_cache), "with_prompt_cache must be callable"
    assert callable(cacheable), "cacheable must be callable"
    print("Smoke test: decorators are callable")

    # Smoke test: protocol checking
    assert isinstance(policy, CachePolicy), "PromptCachePolicy must satisfy CachePolicy"
    assert isinstance(cache, CacheBackend), "TTLCache must satisfy CacheBackend"
    print("Smoke test: protocol conformance verified")

    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
