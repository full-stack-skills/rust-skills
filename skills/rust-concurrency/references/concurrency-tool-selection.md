# Concurrency Tool Selection

Select a primitive from workload semantics and measured contention, not popularity. Inspect the locked crate version, enabled features, MSRV, supported targets, cancellation behavior, and maintenance status before adoption.

## Execution and scheduling

| Tool | Use it for | Required guardrails |
|---|---|---|
| `std::thread` and scoped threads | Bounded blocking work and borrowed parallel tasks | Join every thread; bound stack size and count |
| Tokio | Readiness-driven network and process I/O | Bound admission, queues, blocking submissions, and shutdown |
| Rayon | CPU-heavy divide-and-conquer and data parallelism | Use a dedicated pool when isolation or sizing matters |
| Crossbeam deque | Custom work-stealing schedulers | Define stealing, shutdown, panic, and memory-reclamation invariants |

Do not move CPU-heavy work to `spawn_blocking` without a submission limit. Tokio permits many queued blocking tasks; `max_blocking_threads` limits active threads, not queue growth. When an async service invokes Rayon, acquire an application-level permit before submitting work and return results through a cancellation-aware boundary.

## Channels and queues

| Requirement | Candidate | Notes |
|---|---|---|
| Async bounded MPSC | `tokio::sync::mpsc` | `.send().await` propagates backpressure; define close behavior |
| Async request/reply | Tokio `mpsc` plus `oneshot` | Treat either endpoint dropping as a protocol result |
| Latest configuration or status | `tokio::sync::watch` | Intermediate values may be skipped |
| Loss-tolerant fan-out | `tokio::sync::broadcast` | Handle `Lagged`; events must be discardable or reconstructible |
| Sync bounded MPMC | `crossbeam_channel::bounded` or a measured alternative | Bounded capacity is part of the API contract |
| Lock-free bounded queue | `crossbeam_queue::ArrayQueue` | Use only when non-blocking full/empty behavior is acceptable |
| Work-stealing queue | `crossbeam_deque` | Intended for scheduler-like ownership, not ordinary messaging |

Evaluate `flume` or `kanal` only when their synchronous/asynchronous semantics and measured behavior solve a concrete requirement. Do not choose a channel from microbenchmarks alone; cancellation, disconnect, fairness, select behavior, and memory bounds matter.

## Shared state

| State shape | Candidate | Boundary |
|---|---|---|
| Short critical section | `std::sync::Mutex` or `RwLock` | Never hold a guard across `.await`, callbacks, or slow I/O |
| Async critical section that must await | `tokio::sync::Mutex` | Prefer moving I/O outside the lock when possible |
| Lower-overhead synchronous locks | `parking_lot` | Recheck poisoning and fairness expectations |
| Read-mostly immutable snapshot | `arc-swap` | Writers replace whole snapshots; account for clone/update cost |
| Independent keyed mutations | `DashMap` | Multi-key operations and entry guards need explicit ordering |
| Concurrent cache | `moka` | Set maximum capacity, weights, TTL/TTI, and eviction observability |
| Counters and flags | atomics | Specify ordering and avoid split invariants across atomics |

Prefer partitioned ownership or an actor when an invariant spans multiple fields or keys. A faster lock cannot repair an invalid atomicity boundary.

## Selection evidence

Before replacing a primitive, capture a representative benchmark or load test with throughput, p95/p99 latency, allocation rate, queue depth, lock wait, CPU, and RSS. Include overload and shutdown behavior, not only steady-state throughput.

## Upstream sources

- [Tokio](https://tokio.rs/tokio/tutorial)
- [Rayon](https://docs.rs/rayon/)
- [Crossbeam](https://docs.rs/crossbeam/)
- [parking_lot](https://docs.rs/parking_lot/)
- [arc-swap](https://docs.rs/arc-swap/)
- [DashMap](https://docs.rs/dashmap/)
- [Moka](https://docs.rs/moka/)
