# Metrics and Cardinality

## Instrument choice

| Instrument | Use |
|---|---|
| Counter | Monotonic totals such as requests, errors, retries, and bytes |
| Gauge | Current state such as queue depth, connections, tasks, or pool usage |
| Histogram | Distributions such as latency, payload size, and queue wait |

Use base units consistently and encode them in names or metadata according to the selected backend. Derive histogram buckets from SLO and operational thresholds rather than library defaults alone.

## Label budgets

Allow only bounded dimensions such as method, normalized route, status class, operation, error category, dependency, and region. Reject arbitrary paths, URLs, query strings, request IDs, user IDs, stack traces, messages, and unconstrained tenant labels.

Estimate worst-case series count before deployment:

```text
series = product(label_value_counts) * instances * instrument_variants
```

Review cardinality after every new label and alert on unexpected series growth.

## Operational metrics

For concurrent services, include admission, in-flight work, queue depth and wait, rejection, timeout, cancellation, retry, dependency latency, pool saturation, and shutdown duration. Pair rates with latency and saturation so operators can distinguish load from failure.

## Sources

- [metrics](https://docs.rs/metrics/)
- [metrics-exporter-prometheus](https://docs.rs/metrics-exporter-prometheus/)
- [OpenTelemetry metrics](https://opentelemetry.io/docs/languages/rust/instrumentation/#metrics)
