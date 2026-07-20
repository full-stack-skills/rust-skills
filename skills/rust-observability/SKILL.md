---
name: rust-observability
description: Instrument, operate, and review Rust applications with tracing spans and events, structured logs, metrics, OpenTelemetry context propagation, Prometheus export, sampling, correlation, redaction, cardinality control, tokio-console diagnostics, and graceful telemetry shutdown. Use when users ask for logging, distributed traces, service metrics, request correlation, async task diagnosis, SLO evidence, or production observability architecture.
---

# Rust Observability

Design telemetry from operational questions and failure modes. Logs explain discrete events, traces connect work across boundaries, metrics quantify behavior over time, and profiles diagnose resource consumption. Do not emit all data to all signals.

## Scope and Routing

Use this skill for `tracing`, subscribers, structured logs, metrics, OpenTelemetry, context propagation, sampling, exporters, request correlation, async runtime diagnostics, redaction, and shutdown flushing.

Route concurrency correctness to `rust-concurrency`, HTTP middleware to `rust-web`, security event policy to `rust-web-security`, performance profiling to `rust-performance`, and dependency features to `rust-cargo-build`.

## Workflow

### 1. Start from decisions and SLOs

List the questions operators must answer: request rate and latency, error categories, saturation, queue depth, retries, dependency health, task leaks, resource usage, and deployment identity. Define service name, environment, version, instance attributes, ownership, retention, access control, and cost budgets before selecting exporters.

### 2. Establish structured tracing

Use `tracing` spans for operations with duration and nested work; use events for facts occurring at a point in time.

```rust
use tracing::{info, instrument};

#[instrument(skip(payload), fields(job.id = job_id))]
async fn process(job_id: u64, payload: &[u8]) {
    info!(payload.len = payload.len(), outcome = "accepted");
}
```

- Name spans and fields consistently using domain meaning.
- Skip secrets, bodies, credentials, raw SQL values, and large payloads.
- Record stable error categories and outcomes instead of only formatted messages.
- Ensure instrumented futures are entered during polling, not by holding a span guard across `.await` incorrectly.
- Configure filtering and formatting at the application boundary, not inside libraries.

Read [Tracing and Structured Logs](references/tracing-and-logs.md).

### 3. Design bounded metrics

Choose counters for totals, gauges for current state, and histograms for distributions. Record throughput, latency, errors, saturation, queue wait, retries, rejections, and resource pools using stable low-cardinality labels.

Never use user IDs, request IDs, URLs with raw paths, SQL text, arbitrary error messages, or unbounded tenant IDs as metric labels. Define histogram units and buckets from SLOs. Read [Metrics and Cardinality](references/metrics-and-cardinality.md).

### 4. Propagate distributed context

Extract remote trace context only from trusted transport formats, create server or consumer spans, and inject current context into outbound requests or messages. Preserve causal relationships across spawned tasks deliberately; detached background work may need a link rather than an inherited parent.

Use OpenTelemetry only when interoperability or vendor-neutral export is required. Check signal maturity, crate versions, runtime requirements, batch behavior, and exporter compatibility. Read [OpenTelemetry and Context](references/opentelemetry-and-context.md).

### 5. Configure pipelines and shutdown

- Compose subscribers and layers once at process startup.
- Make filters reloadable only with authenticated and audited controls.
- Bound exporter queues and define drop or backpressure behavior.
- Sample traces with an explicit policy; keep errors and rare paths observable without making success traffic unaffordable.
- Flush or shut down telemetry providers within the service shutdown deadline.
- Avoid recursive telemetry from exporters using the same instrumented network path.

### 6. Validate telemetry behavior

Test field names, levels, error categories, context propagation, redaction, cardinality, disabled-subscriber behavior, exporter failure, queue saturation, and shutdown flushing. Use a test subscriber or in-memory exporter rather than asserting unstable formatted lines.

Use `tokio-console` in diagnostic builds to find long polls, resource waits, and leaked tasks; do not expose its control endpoint publicly. Read [Runtime and Operations](references/runtime-and-operations.md).

## Completion Criteria

- Tie every signal to an operational question or SLO.
- Use structured spans and events with stable fields and explicit redaction.
- Keep metric labels bounded and histogram units defined.
- Propagate trace context across supported inbound, outbound, and messaging boundaries.
- Bound exporter cost, queues, sampling, and shutdown time.
- Test telemetry as behavior without coupling to one text formatter or vendor.

## Resources

- [Tracing and Structured Logs](references/tracing-and-logs.md)
- [Metrics and Cardinality](references/metrics-and-cardinality.md)
- [OpenTelemetry and Context](references/opentelemetry-and-context.md)
- [Runtime and Operations](references/runtime-and-operations.md)
- [Execution Scenarios](examples/examples.md)
- `examples/golden-observability/`: a compiled custom tracing layer contract.

## Upstream Sources

- [tracing](https://docs.rs/tracing/)
- [tracing-subscriber](https://docs.rs/tracing-subscriber/)
- [OpenTelemetry Rust](https://opentelemetry.io/docs/languages/rust/)
- [metrics](https://docs.rs/metrics/)
- [tokio-console](https://github.com/tokio-rs/console)

## Data Privacy

This skill does not collect, store, or transmit user data. Telemetry changes can transmit production data; confirm authorization, destinations, retention, redaction, and access controls before enabling exporters.
