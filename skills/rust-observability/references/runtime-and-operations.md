# Runtime and Operations

## Tokio diagnostics

Use runtime-aware tracing and tokio-console in controlled diagnostic environments to inspect task poll time, wakeups, resource waits, and task lifetime. Instrumentation requires compatible Tokio features and build configuration; measure its overhead before production enablement.

Long poll time often indicates blocking work or excessive computation on an async worker. Frequent wakes without progress indicate notification or select-loop problems. Long-lived tasks are not automatically leaks; compare them with explicit lifecycle ownership.

## Exporter failure

Telemetry infrastructure must not take down the application by default. Bound memory, retries, threads, sockets, and shutdown time. Expose exporter drop and failure counters through an independent minimal path when possible.

## Validation and rollout

1. Test locally with an in-memory subscriber or exporter.
2. Load-test instrumentation overhead and cardinality.
3. Deploy to a small environment and verify trace joins, metric units, labels, redaction, and retention.
4. Exercise collector outage, queue saturation, configuration reload, and process shutdown.
5. Document dashboards, alerts, ownership, and rollback.

## Sources

- [Tokio tracing topic](https://tokio.rs/tokio/topics/tracing)
- [tokio-console](https://github.com/tokio-rs/console)
- [tracing-appender](https://docs.rs/tracing-appender/)
