# cache

Reusable caching primitives for FlossWare.

This repository provides generic cache contracts and implementations, including TTL caching and provider-specific prompt-cache mechanics.

## Architectural boundary

Caching is a cross-cutting capability. It does not own model invocation, routing, orchestration, Knowledge, or application workflow.

Prompt caching is **integrated and owned semantically by `model-gateway`**. The gateway may use this repository for cache mechanics and provider-specific implementations.

```text
Worker -> model-gateway -> cache capability -> provider/model
```

Generic caches remain independently usable by other capabilities.

## Status

Active supporting capability. Keep provider credentials, cache authorization, prompt identity, and provider semantics in `model-gateway`; keep reusable cache mechanics here.

## License

MIT
