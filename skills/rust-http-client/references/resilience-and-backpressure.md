# Resilience and Backpressure

## Total request budget

Derive every attempt, delay, and body-read timeout from one caller deadline. A retry policy that can exceed the caller's budget creates abandoned work and latency amplification.

## Retry decision

Retry only when all are true:

1. the failure is classified as transient;
2. the operation is idempotent or has an accepted idempotency key;
3. the request body can be replayed safely;
4. attempts and total time remain within budget;
5. the retry does not violate provider rate limits or overload policy.

Use jittered backoff and cap both delay and attempts. Parse `Retry-After` defensively. Do not retry invalid input, authentication, authorization, most conflict responses, certificate failures, or deterministic decoding errors.

## Concurrency and overload

Apply an admission semaphore or Tower concurrency limit before expensive request construction. Keep queues bounded and expose saturation as a typed error or load-shed result. Track in-flight requests, queue wait, attempts, final status class, latency, timeout, cancellation, and rejected work without recording sensitive bodies or high-cardinality URLs.

Middleware order changes semantics. For example, a timeout outside retry bounds the full operation, while a timeout inside retry bounds each attempt. Document and test the intended order.

## Circuit breakers and hedging

Add a circuit breaker only with a defined rolling signal, open duration, half-open probes, and per-origin isolation. Hedging duplicates work and load; restrict it to idempotent operations with measured tail-latency benefit.

## Sources

- [Tower retry](https://docs.rs/tower/latest/tower/retry/)
- [Tower limit](https://docs.rs/tower/latest/tower/limit/)
- [Tower load shed](https://docs.rs/tower/latest/tower/load_shed/)
- [Tower timeout](https://docs.rs/tower/latest/tower/timeout/)
