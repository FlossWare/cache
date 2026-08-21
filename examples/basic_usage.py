#!/usr/bin/env python3
"""Basic cache-ai usage: prompt caching and TTL caching."""
from __future__ import annotations

from cache_ai import PromptCachePolicy, TTLCache, cacheable


def main():
    # 1. Prompt cache with provider-specific hints
    policy = PromptCachePolicy()

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain prompt caching."},
    ]

    # Apply Anthropic-specific hints
    annotated = policy.apply_cache_hints(messages, provider="anthropic")
    print("Anthropic annotated:")
    for msg in annotated:
        print(f"  role={msg['role']}, cache_control={msg.get('cache_control', 'none')}")

    # Second call with same messages -- tracked as cache hit
    policy.apply_cache_hints(messages, provider="anthropic")

    # 2. TTL cache
    cache = TTLCache(default_ttl=300, max_size=100)
    cache.put("embedding:doc1", [0.1, 0.2, 0.3])
    cache.put("embedding:doc2", [0.4, 0.5, 0.6])

    result = cache.get("embedding:doc1")
    print(f"\nTTL Cache: get('embedding:doc1') = {result}")

    stats = cache.stats()
    print(f"Cache stats: hits={stats.hits}, misses={stats.misses}")

    # 3. Cacheable decorator
    call_count = 0

    @cacheable(ttl=60)
    def expensive_computation(x: int, y: int) -> int:
        nonlocal call_count
        call_count += 1
        return x ** y

    result1 = expensive_computation(2, 10)
    result2 = expensive_computation(2, 10)  # cached
    print(f"\n@cacheable: 2^10 = {result1}")
    print(f"  Call count: {call_count} (should be 1 -- second call was cached)")

    # 4. Google provider hints
    google_annotated = policy.apply_cache_hints(messages, provider="google")
    print(f"\nGoogle annotated:")
    for msg in google_annotated:
        print(f"  role={msg['role']}, cached_content={msg.get('cached_content', 'none')}")


if __name__ == "__main__":
    main()
