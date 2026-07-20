# Rust Observability Execution Scenarios

## Instrument an HTTP service

User request:

> Add structured logs, request traces, and Prometheus metrics to this axum service.

Define normalized operations and SLO signals, instrument middleware and application boundaries, propagate outbound context, keep labels bounded, redact secrets, and test fields plus exporter failure. Route handler and middleware mechanics to `rust-web`.

## Diagnose stuck Tokio tasks

User request:

> Requests stop completing under load although CPU remains low.

Combine queue and saturation metrics with tracing spans and a controlled tokio-console diagnostic build. Look for long resource waits, blocked async workers, wake loops, lost cancellation, and leaked task ownership before changing worker counts.

## Adopt OpenTelemetry

User request:

> Export traces and metrics to our OTLP collector.

Verify current crate and signal maturity, define propagation and sampling, bound batch queues and exporter retries, test collector outage and shutdown flush, and confirm retention plus sensitive-data policy before enabling production export.
