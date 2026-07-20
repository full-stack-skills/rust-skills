# OpenTelemetry and Context

Use OpenTelemetry when telemetry must cross process boundaries or export through a standard protocol. Keep domain instrumentation on stable `tracing` and metrics abstractions where practical, and isolate SDK/exporter setup at the application boundary.

## Propagation

1. Extract an allowed propagator from inbound headers or message metadata.
2. Validate transport trust and do not treat trace fields as authentication.
3. Attach remote context to the new server or consumer span.
4. Inject current context into approved outbound requests.
5. Preserve baggage only through an allowlist with size and sensitivity limits.

Trace IDs are correlation data, not security credentials. Attackers can supply them; validate syntax and never use them for authorization or tenancy.

## Pipeline design

- Check version compatibility across `opentelemetry`, SDK, OTLP exporter, tracing bridge, and runtime.
- Bound batch queues and export timeouts.
- Decide whether telemetry is dropped or blocks when the collector is unavailable.
- Prevent exporter retry storms and recursive instrumentation.
- Shut down providers explicitly and fit flushing inside the process deadline.

OpenTelemetry Rust signal maturity can change independently for traces, metrics, and logs. Verify the current upstream status before making a production commitment.

## Sampling

Head sampling controls cost early but lacks outcome knowledge. Tail sampling can retain errors and slow traces but requires collector capacity and delayed decisions. Document sampling location, rates, inherited decisions, and how operators investigate unsampled failures.

## Sources

- [OpenTelemetry Rust](https://opentelemetry.io/docs/languages/rust/)
- [opentelemetry crate](https://docs.rs/opentelemetry/)
- [tracing-opentelemetry](https://docs.rs/tracing-opentelemetry/)
