#!/bin/bash
# Add cache-ai integration to your CLAUDE.md
set -e

CLAUDE_MD="${CLAUDE_MD:-./CLAUDE.md}"

if [ ! -f "$CLAUDE_MD" ]; then
    echo "Creating $CLAUDE_MD"
    touch "$CLAUDE_MD"
fi

cat >> "$CLAUDE_MD" << 'EOF'

## Prompt Caching (cache-ai)

This project uses [cache-ai](https://github.com/FlossWare/cache-ai) for prompt caching and provider-specific cache hints.

**Install:** `pip install "git+https://github.com/FlossWare/cache-ai.git"`

**Key imports:**
```python
from cache_ai import PromptCachePolicy, TTLCache, with_prompt_cache, cacheable
```

**Usage patterns:**
- Prompt cache: `PromptCachePolicy()` with `apply_cache_hints(messages, provider="anthropic")`
- TTL cache: `TTLCache(default_ttl=300, max_size=1000)`
- Decorator: `@with_prompt_cache(provider="anthropic")` for automatic hint application
- Decorator: `@cacheable(ttl=300)` for function result caching
- Zero external dependencies (stdlib only)
EOF

echo "Added cache-ai integration to $CLAUDE_MD"
