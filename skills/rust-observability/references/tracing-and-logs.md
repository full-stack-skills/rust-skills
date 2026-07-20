# Tracing and Structured Logs

## Signal shape

Use spans for operations with duration and parent-child relationships. Use events for state changes, decisions, retries, and failures. Libraries emit structured telemetry but should not install a global subscriber.

Recommended stable fields include service operation, protocol method, normalized route, status class, error category, retry attempt, queue name, and outcome. Record request or trace identifiers in logs when needed for correlation, but never use them as metric labels.

## Async instrumentation

Instrument futures so a span is active when the future is polled. Holding an entered span guard across `.await` can produce incorrect traces and may make futures non-`Send`; use `#[instrument]`, `.instrument(span)`, or `in_scope` for synchronous work.

Spawned tasks need an explicit ownership decision:

- child work may inherit the current span;
- queued work may continue from extracted context;
- detached maintenance tasks generally start from a service-level root;
- fan-in or fan-out may require links rather than a single misleading parent.

## Logging policy

- `ERROR`: failed operation requiring attention or violating an invariant;
- `WARN`: degraded but handled state;
- `INFO`: low-volume lifecycle and business milestones;
- `DEBUG` and `TRACE`: diagnostic detail gated by filters and cost budgets.

Avoid logging the same error at every layer. Add context while propagating, then record once at the boundary that owns the outcome.

## Sensitive data

Skip credentials, cookies, authorization headers, payloads, personal data, secrets, raw query values, and cryptographic material. Redact at instrumentation sites and exporter processors; formatting filters alone are insufficient.

## Sources

- [tracing](https://docs.rs/tracing/)
- [tracing attributes](https://docs.rs/tracing/latest/tracing/attr.instrument.html)
- [tracing-subscriber](https://docs.rs/tracing-subscriber/)
