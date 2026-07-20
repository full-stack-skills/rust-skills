# Asynchronous Service Mode Production

This resource uses the `rmux` local daemon/SDK as a case study, without treating its constants or crate versions as generic defaults. The current snapshot is `3e4eabd8534aab145523de9fe97e4ad164a75ac4`; design conclusions must be measured on the target project before deployment.

## Write Resource Budgets First

Before selecting an API, answer:

| Resource | Must Define |
|---|---|
| Connection | Max authenticated/unauthenticated connections; requests in transit per connection |
| Task | Who creates them, who waits for completion, failure propagation, cancellation and timeout limits |
| Queue | Capacity, max element size, queue full behavior, close behavior |
| Subscription | Per-connection/per-resource limit, TTL (time-to-live), slow consumer handling, reconnection strategy |
| Runtime | Async worker, blocking worker, CPU isolation strategies |
| Memory | `frame`/body limits; per-connection buffers; worst-case global values |

Using "Tokio" alone does not constitute high-concurrency design. Concurrency comes from controlled workload, short polling intervals, explicit state ownership, and recoverable tasks.

## Select Channels by Semantics

| Requirement | Common Tool | Design Requirements |
|---|---|---|
| Bounded producer request queue | `tokio::sync::mpsc` (bounded) | Use `.send().await` to induce backpressure; record capacity limits |
| Single-request/response pair | `oneshot` | Both sender and receiver drop are protocol results; do not unwrap |
| Global close or latest config | `watch` | Guarantees only the latest value; handle sender drops gracefully |
| Multi-subscription instantaneous events | `broadcast` | Receiver may be `Lagged`; events must be either discardable or reconstructible |
| Synchronous thread bridging | `std::sync::mpsc` / dedicated threads | Do not block `.recv()` on async workers in synchronous contexts |

The `rmux` SDK transport uses bounded `mpsc` channels to receive commands and creates a new `oneshot` per call. A single actor serializes socket writes, pairing responses via FIFO ordering. The benefit is that protocol state has only one writer; the cost includes head-of-line blocking on producers and strict response order guarantees required by single-connection protocols.

## Actor Supervision and Task Management

An **actor** model suits scenarios where:
- A resource requires a strict sequence (e.g., socket writes, state machines, device handles);
- Many callers exist but state changes must be serialized;
- Commands and results can be modeled as enums;
- Clear error conditions are defined for queue fullness, actor exit, and pending requests.

**Checklist:**
1. Command queues are bounded;
2. When an actor exits, all pending replies fail;
3. New commands are rejected after shutdown;
4. Reader/writer sub-tasks are saved and aborted/joined on exit;
5. Terminal failures are cached for subsequent calls to ensure fast failure paths;
6. Best-effort `Drop` cleanup does not mimic strong consistency semantics.

When managing similar tasks using `JoinSet`, results return in completion order. If the API must preserve input ordering (e.g., broadcasting like `rmux`), carry input indices through and sort during aggregation. When target counts are untrusted or potentially large, add a `Semaphore` for batching; note that `JoinSet` itself does not limit concurrency levels.

## Slow Consumers and Backpressure

Explicit strategies must be chosen before applying them safely:
- **Blocking producers**: Reliable but introduces latency; suitable when requests cannot be dropped;
- **Discard and reconstruct snapshots**: Suitable for UI/render/status states where merging is acceptable;
- **Disconnect slow consumers**: Suitable for real-time streams, returning diagnostic reasons on failure;
- **Persistent replay**: Suitable for business events that must not be lost;
- **Pause upstream then resume**: Set high/low watermarks to avoid jitter near thresholds.

The `rmux` case study combined event coalescing, subscription limits/TTLs, output age caps, and low-watermark recovery. This demonstrates that "bounded channels" alone are insufficient: item size limits, subscription base sizes, and retention times must also be constrained.

## Shared State and Locking
- Large state should be partitioned by lifecycle and contention patterns; do not bundle all responsibilities under a single global `Mutex<AppState>`.
- Pure counters or flags can use atomic types, but first clarify ordering semantics and cross-variable invariants.
- Extract owned snapshots/commands from locks before releasing guards and awaiting them: `.await` after dropping the guard.
- Background tasks hold `Weak<T>`; they naturally stop when their owner releases it, avoiding circular references with `Arc`.
- Use `std::sync::Mutex` for critical sections that are extremely short and do not span await points. Use Tokio mutexes only when cross-scheduling waits are required by the async runtime.
- Do not mechanically choose between `RwLock` based on "read-heavy, write-light"; first measure lock duration and fairness characteristics.

## Runtime Is Not Larger Than Necessary

The `rmux` daemon fixed its multi-threaded runtime's async worker count to 1 because the primary workload is readiness-driven I/O; render/status operations have been merged into a single thread. Adding more workers would increase cross-thread wakeups and resident memory usage. This is not a universal constant but an architecture decision validated through measurement.

**Checklist:**
1. Identify blocking workloads: file descriptors, DNS lookups, `stdio`, CPU-intensive tasks, FFI calls;
2. Move these to `spawn_blocking` or dedicated pools;
3. Ensure the outer bounded channel/Semaphore protects potentially unbounded blocking queues/pools;
4. Compare throughput (p95/p99), wakeups, RSS against default core counts and candidate values for worker count/stack size/blocking limits via configuration tests or benchmarks.

## Close Protocol Recommendation

Recommended sequence:
```text
Stop accepting new connections / acceptors
  -> Publish shutdown signal
  -> Allow current safe points on connections/workers to terminate gracefully
  -> Cancel unnecessary tasks
  -> Join all supervised tasks
  -> Flush and release resources
  -> Return explicit failure after timeout
```

The peer's disconnection should also participate in cancellation. Long-waiting requests must not permanently occupy server-side waiters even if the client disconnects; test coverage must include "count zero after disconnect" and "no background tasks surviving shutdown."
