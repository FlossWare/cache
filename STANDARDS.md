# FlossWare Engineering Standards Compliance

This package adheres to the following ADRs from [FlossWare/engineering-standards](https://github.com/FlossWare/engineering-standards):

## ADR-0001: Explicit Opt-In

Caching never activates automatically. All capabilities require explicit instantiation or decorator application by the developer.

- `PromptCachePolicy` must be instantiated and methods called explicitly.
- `TTLCache` must be instantiated with desired configuration (TTL, max size).
- `@with_prompt_cache` and `@cacheable` decorators are opt-in.
- When no cache is configured, decorators create isolated per-function instances.

## ADR-0006: Cross-Cutting Decorators

Convenience decorators in `cache_ai.decorators`:

- `@with_prompt_cache(provider="anthropic")` -- applies provider-specific cache hints to LLM messages before forwarding.
- `@cacheable(ttl=300)` -- caches function results by content hash with optional TTL.

## ADR-0008: Free-First

Zero external dependencies at runtime. The package uses only the Python standard library (`hashlib`, `json`, `threading`, `time`, `functools`, `asyncio`, `dataclasses`, `typing`).

Development dependencies (pytest, pytest-asyncio) are optional.

## ADR-0009: Core Principles

- **Modular**: Each concern (prompt caching, TTL caching, provider hints) is a separate module.
- **Composable**: Components can be used independently or combined.
- **Contracts over implementations**: The `CachePolicy` and `CacheBackend` Protocols define interfaces; any conforming object works.

## ADR-0017: Agent-Neutral

The package works with any agent runtime. The `LLMBackend` Protocol is the only integration point -- any agent framework that can provide an async `chat()` method is compatible.

No assumptions are made about the calling agent's architecture, event loop, or lifecycle.

## ADR-0020: Capability-Protocol Separation

Cache capabilities are transport-independent:

- `CachePolicy` Protocol defines what is needed (hint application, stats), not how it is delivered.
- `CacheBackend` Protocol defines generic key-value operations.
- No HTTP, gRPC, or other transport assumptions baked in.
- The same caching logic works whether the backend is a local dict, Redis, or an agent-internal store.
