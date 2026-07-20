# Concurrency Testing and Diagnostics

Concurrency verification requires complementary evidence. Ordinary tests prove selected executions; model checking explores controlled schedules; tracing and load tests expose runtime behavior under realistic work.

## Deterministic contract tests

- Inject clocks, cancellation, queue capacities, and worker counts.
- Replace sleeps with explicit barriers, notifications, or paused time where supported.
- Assert task and waiter counts return to zero after success, failure, cancellation, disconnect, and shutdown.
- Test queue-full, receiver-drop, sender-drop, lag, timeout, partial completion, panic, and shutdown races.
- Run multi-thread and current-thread Tokio configurations when both are supported.

Avoid tests that repeatedly sleep and hope a race appears. They are slow, flaky, and weak evidence.

## Loom model checking

Use Loom for small synchronization state machines implemented with threads, atomics, mutexes, condition variables, or custom cells. Put interchangeable synchronization types behind a `cfg(loom)` module and run the model separately:

```bash
RUSTFLAGS="--cfg loom" cargo test --release --test loom_model
```

Keep the model deterministic and small. Loom cannot observe ordinary synchronization hidden behind non-Loom types, arbitrary system calls, external runtimes, or random input. Bound preemptions only after an exhaustive model becomes impractical, and record that reduced coverage.

## Async runtime diagnostics

Instrument Tokio tasks with `tracing` spans and enable the runtime's tracing support only in diagnostic builds where appropriate. Use `tokio-console` to inspect:

- tasks with long poll durations;
- tasks woken repeatedly without progress;
- resources with long waits;
- tasks that remain alive after their owners stop;
- blocking operations on async workers.

Treat instrumentation overhead and telemetry cardinality as production budgets. Do not expose payloads, tokens, or unbounded identifiers in span fields.

## Load and failure testing

Measure at and beyond the intended concurrency limit:

1. ramp admission until the first budget saturates;
2. hold slow consumers and stalled dependencies;
3. inject connection resets, timeouts, partial responses, and cancellation;
4. trigger graceful shutdown while queues are non-empty;
5. confirm bounded memory, bounded queue depth, stable latency, rejected-work metrics, and no surviving tasks.

Use Criterion for local CPU primitives and a service load generator for end-to-end behavior. A microbenchmark cannot prove scheduler fairness, overload control, or graceful shutdown.

## Race and memory tools

- Miri can detect some undefined behavior in unsafe concurrent code but is not a general data-race detector for all external operations.
- ThreadSanitizer is useful on supported nightly/platform combinations; document toolchain and target limitations.
- Sanitizers and model tests complement, rather than replace, safe API and invariant review.

## Upstream sources

- [Loom](https://docs.rs/loom/)
- [Tokio testing](https://tokio.rs/tokio/topics/testing)
- [Tokio tracing](https://tokio.rs/tokio/topics/tracing)
- [tokio-console](https://github.com/tokio-rs/console)
- [Rust sanitizers](https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html)
