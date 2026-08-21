# cache-ai

Prompt caching, TTL caching, and provider-specific cache hints for LLM applications. Zero external dependencies.

## Install

```bash
pip install "git+https://github.com/FlossWare/cache-ai.git"
```

## Quick Start

### Prompt Cache Policy

```python
from cache_ai import PromptCachePolicy

policy = PromptCachePolicy()

messages = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello"},
]

# Apply Anthropic-specific cache hints
annotated = policy.apply_cache_hints(messages, provider="anthropic")
# System messages get cache_control: {"type": "ephemeral"}

# Track hit/miss stats
stats = await policy.cache_stats()
print(f"Hit rate: {stats.hit_rate:.1%}")
```

### TTL Cache

```python
from cache_ai import TTLCache

cache = TTLCache(default_ttl=300, max_size=1000)

cache.put("key", "value")
result = cache.get("key")  # -> "value"

cache.put("temp", "data", ttl=60)  # expires in 60 seconds

stats = cache.stats()
print(f"Hits: {stats.hits}, Misses: {stats.misses}")
```

### Decorators

```python
from cache_ai import with_prompt_cache, cacheable

@with_prompt_cache(provider="anthropic")
async def chat(messages, *, model="default"):
    return await backend.chat(messages, model=model)

@cacheable(ttl=300)
def expensive_computation(x, y):
    return x ** y
```

## Features

- **PromptCachePolicy** -- content-hash hit/miss tracking with provider-specific cache hints
- **TTLCache** -- thread-safe in-memory cache with time-to-live expiry and max size eviction
- **Provider hints** -- Anthropic (ephemeral), Google/Gemini (cached_content), OpenAI (pass-through)
- **Decorators** -- `@with_prompt_cache` for LLM calls, `@cacheable` for general function caching
- **Protocols** -- `CachePolicy`, `CacheBackend`, `LLMBackend` for structural subtyping

## Standards

See [STANDARDS.md](STANDARDS.md) for FlossWare engineering standards compliance (ADR-0001, ADR-0006, ADR-0008, ADR-0009, ADR-0017, ADR-0020).

## License

MIT
