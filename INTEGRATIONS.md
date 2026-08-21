# cache-ai Integrations

Install from GitHub:

```bash
pip install "git+https://github.com/FlossWare/cache-ai.git"
```

---

## Claude Code

### CLAUDE.md Snippet

```markdown
## Prompt Caching (cache-ai)

This project uses `cache-ai` for prompt caching and provider-specific cache hints.

- Prompt cache: `from cache_ai import PromptCachePolicy, with_prompt_cache`
- TTL cache: `from cache_ai import TTLCache, cacheable`
- Provider hints: `from cache_ai import apply_anthropic_hints, apply_google_hints`
- Use `@with_prompt_cache(provider="anthropic")` to auto-apply cache hints
- Use `@cacheable(ttl=300)` to cache function results with TTL
- Zero external dependencies (stdlib only)
```

### Hook Example

Create `.claude/hooks/post-tool-edit.py` to track cache effectiveness:

```python
#!/usr/bin/env python3
"""Post-edit hook: report cache stats after edits."""
from __future__ import annotations

import sys


def main():
    if len(sys.argv) < 2:
        sys.exit(0)

    file_path = sys.argv[1]
    if "cache" in file_path.lower() or "llm" in file_path.lower():
        print("[cache-ai] Consider reviewing cache configuration:")
        print("  from cache_ai import PromptCachePolicy, TTLCache")
        print("  policy = PromptCachePolicy()")
        print("  stats = await policy.cache_stats()")


if __name__ == "__main__":
    main()
```

### Skill Example

Create `.claude/skills/cache-stats.md`:

```markdown
---
name: cache-stats
description: Check prompt cache hit/miss statistics
---

Use cache-ai to review caching effectiveness:

\```python
from cache_ai import PromptCachePolicy

policy = PromptCachePolicy()
# ... after some operations ...
stats = await policy.cache_stats()
print(f"Hit rate: {stats.hit_rate:.1%}")
print(f"Hits: {stats.hits}, Misses: {stats.misses}")
\```
```

---

## OpenAI Codex

### AGENTS.md Snippet

```markdown
## Prompt Caching

Use cache-ai for provider-specific prompt caching:
- Install: `pip install "git+https://github.com/FlossWare/cache-ai.git"`
- Prompt cache: `PromptCachePolicy()` with `apply_cache_hints(messages, provider="anthropic")`
- TTL cache: `TTLCache(default_ttl=300, max_size=1000)` for general caching
- Decorator: `@with_prompt_cache(provider="anthropic")` for automatic hint application
- Decorator: `@cacheable(ttl=300)` for function result caching
```

### Tool Definition

```python
from cache_ai import PromptCachePolicy, TTLCache

# Prompt caching with Anthropic
policy = PromptCachePolicy()
messages = [{"role": "system", "content": "You are helpful."}, {"role": "user", "content": "Hi"}]
annotated = policy.apply_cache_hints(messages, provider="anthropic")

# General TTL cache
cache = TTLCache(default_ttl=300)
cache.put("result_key", expensive_result)
cached = cache.get("result_key")
```

---

## Cursor

### .cursorrules Snippet

```
When working with LLM API calls, use cache-ai for prompt caching:

- Import: from cache_ai import PromptCachePolicy, TTLCache, with_prompt_cache, cacheable
- Prompt cache: PromptCachePolicy() applies provider-specific cache hints
- TTL cache: TTLCache(default_ttl=300) for in-memory result caching
- Decorator: @with_prompt_cache(provider="anthropic") for automatic hints
- Decorator: @cacheable(ttl=300) for function-level caching
- Zero dependencies - stdlib only
- Install: pip install "git+https://github.com/FlossWare/cache-ai.git"
```

---

## Crush

### Configuration

```python
# crush.config.py
from cache_ai import PromptCachePolicy, TTLCache, cacheable

# Shared prompt cache policy
prompt_cache = PromptCachePolicy()

# Shared result cache
result_cache = TTLCache(default_ttl=600, max_size=500)

@cacheable(cache=result_cache, ttl=300)
async def cached_llm_call(prompt: str, *, model: str = "default"):
    """LLM calls are automatically cached by prompt hash."""
    messages = [{"role": "user", "content": prompt}]
    annotated = prompt_cache.apply_cache_hints(messages, provider="anthropic")
    return await backend.chat(annotated, model=model)
```

---

## Generic Python Agent

### Prompt Caching

```python
from cache_ai import (
    PromptCachePolicy,
    TTLCache,
    apply_anthropic_hints,
    apply_google_hints,
    with_prompt_cache,
    cacheable,
)


# 1. Direct usage -- apply provider-specific hints
policy = PromptCachePolicy()
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain caching."},
]
annotated = policy.apply_cache_hints(messages, provider="anthropic")
# System messages now have cache_control: {"type": "ephemeral"}

# 2. Check cache statistics
import asyncio
stats = asyncio.run(policy.cache_stats())
print(f"Hit rate: {stats.hit_rate:.1%}")

# 3. TTL cache for expensive results
cache = TTLCache(default_ttl=300, max_size=1000)
cache.put("embedding:doc1", [0.1, 0.2, 0.3])
result = cache.get("embedding:doc1")  # -> [0.1, 0.2, 0.3]

# 4. Decorator-based caching
@cacheable(ttl=600)
def compute_embedding(text: str) -> list[float]:
    # expensive computation
    return [0.1, 0.2, 0.3]

# Second call returns cached result
compute_embedding("hello")  # computed
compute_embedding("hello")  # cached
```

### Decorator Pattern

```python
from cache_ai import with_prompt_cache, cacheable

@with_prompt_cache(provider="anthropic")
async def chat_with_cache(messages, *, model="default"):
    """Messages automatically get Anthropic cache hints."""
    return await backend.chat(messages, model=model)

@cacheable(ttl=300)
async def cached_analysis(document: str) -> dict:
    """Results cached for 5 minutes by document hash."""
    return await analyze(document)
```

---

## Cross-Package Integration

### cache-ai + resilience-ai

Cache with circuit breaking:

```python
from cache_ai import with_prompt_cache
from resilience_ai import with_retry, with_circuit_breaker

@with_prompt_cache(provider="anthropic")
@with_retry(max_attempts=3)
@with_circuit_breaker(provider="anthropic")
async def resilient_cached_chat(messages, *, model="default"):
    return await backend.chat(messages, model=model)
```

### cache-ai + observability-ai

Cache with telemetry:

```python
from cache_ai import with_prompt_cache
from observability_ai import track_execution

@track_execution(telemetry=t)
@with_prompt_cache(provider="anthropic")
async def observed_cached_chat(messages, *, model="default"):
    return await backend.chat(messages, model=model)
```

### Full Stack: All Packages

```python
from cache_ai import with_prompt_cache
from consensus_ai import with_consensus
from structured_output_ai import structured_output
from resilience_ai import with_retry, with_circuit_breaker
from observability_ai import track_execution

@structured_output(schema=SCHEMA)
@track_execution(telemetry=t)
@with_prompt_cache(provider="anthropic")
@with_consensus(models=models)
@with_retry(max_attempts=3)
@with_circuit_breaker(provider="llm")
async def production_query(prompt, *, model="default"):
    messages = [{"role": "user", "content": prompt}]
    return await backend.chat(messages, model=model)
```
