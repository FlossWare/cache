"""Convenience decorators for cache-ai (ADR-0006: Cross-Cutting Decorators).

Provides ``@with_prompt_cache`` and ``@cacheable`` decorators that wrap
functions with prompt-cache hint application and result caching.

Users must explicitly opt in by applying the decorator and configuring
the cache (ADR-0001: Explicit Opt-In).
"""

from __future__ import annotations

import functools
import hashlib
import inspect
import json
from typing import Any, Callable

from cache_ai.cache import PromptCachePolicy
from cache_ai.ttl_cache import TTLCache


def with_prompt_cache(
    *,
    provider: str = "anthropic",
    policy: PromptCachePolicy | None = None,
) -> Callable:
    """Decorator that applies provider-specific cache hints to LLM calls.

    The decorated function must accept ``messages: list[dict]`` as its
    first positional argument (or keyword argument).  Cache hints are
    applied to the messages before forwarding to the wrapped function.

    Parameters
    ----------
    provider:
        The LLM provider name (``"anthropic"``, ``"openai"``,
        ``"google"``).
    policy:
        An optional :class:`PromptCachePolicy` instance.  If ``None``,
        a new policy is created per decorated function.
    """
    _per_decorator_policy = policy if policy is not None else PromptCachePolicy()

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if args:
                messages = args[0]
                annotated = _per_decorator_policy.apply_cache_hints(
                    messages, provider=provider
                )
                return await fn(annotated, *args[1:], **kwargs)
            elif "messages" in kwargs:
                messages = kwargs["messages"]
                annotated = _per_decorator_policy.apply_cache_hints(
                    messages, provider=provider
                )
                kwargs["messages"] = annotated
                return await fn(*args, **kwargs)
            return await fn(*args, **kwargs)

        wrapper._cache_policy = _per_decorator_policy  # type: ignore[attr-defined]
        return wrapper

    return decorator


def cacheable(
    *,
    cache: TTLCache | None = None,
    ttl: float | None = None,
    key_fn: Callable[..., str] | None = None,
) -> Callable:
    """Decorator that caches function results by content hash.

    Works with both sync and async functions.  Results are cached in a
    :class:`TTLCache` instance, keyed by a SHA-256 hash of the
    serialized arguments.

    Parameters
    ----------
    cache:
        An optional :class:`TTLCache` instance.  If ``None``, a new
        cache is created per decorated function.
    ttl:
        Time-to-live in seconds for cached results.  ``None`` means
        entries never expire (unless the cache has a default TTL).
    key_fn:
        Optional callable to generate a custom cache key from the
        function arguments.  If ``None``, a hash of ``(args, kwargs)``
        is used.
    """
    resolved_cache = cache if cache is not None else TTLCache()

    def decorator(fn: Callable) -> Callable:
        def _make_key(*args: Any, **kwargs: Any) -> str | None:
            if key_fn is not None:
                return key_fn(*args, **kwargs)
            try:
                raw = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
            except (TypeError, ValueError):
                return None
            return hashlib.sha256(raw.encode()).hexdigest()  # noqa: S324

        if inspect.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                key = _make_key(*args, **kwargs)
                if key is None:
                    return await fn(*args, **kwargs)
                cached = resolved_cache.get(key)
                if cached is not None:
                    return cached
                result = await fn(*args, **kwargs)
                resolved_cache.put(key, result, ttl=ttl)
                return result

            async_wrapper._cache = resolved_cache  # type: ignore[attr-defined]
            return async_wrapper
        else:

            @functools.wraps(fn)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                key = _make_key(*args, **kwargs)
                if key is None:
                    return fn(*args, **kwargs)
                cached = resolved_cache.get(key)
                if cached is not None:
                    return cached
                result = fn(*args, **kwargs)
                resolved_cache.put(key, result, ttl=ttl)
                return result

            sync_wrapper._cache = resolved_cache  # type: ignore[attr-defined]
            return sync_wrapper

    return decorator
