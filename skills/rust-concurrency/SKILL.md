---
name: rust-concurrency
description: Design, implement, diagnose, and test Rust concurrency and parallelism with threads, Send and Sync, locks, atomics, channels, Tokio, Rayon, Crossbeam, bounded backpressure, actor ownership, task supervision, graceful shutdown, runtime diagnostics, and Loom model tests. Use when users ask about shared state, deadlocks, async tasks, CPU parallelism, high concurrency, daemon resource budgets, slow consumers, worker pools, lock-free structures, or concurrent correctness.
---

# Rust Concurrency

> Based on the standard library `std::thread`, `std::sync`, and `std::sync::atomic` modules, along with the Async Book. Use when designing, debugging, load-testing, or reviewing threaded and async Rust code; cancellation, task ownership, lock scope, runtime sizing, queues, overload management, message passing, hand basic ownership to rust-stable and unsafe invariants to rust-unsafe-ffi.

## Capability Boundaries

### ✅ Strengths
1. OS threads (`thread::spawn`, `Builder`, `join`, scoped threads, move closures)
2. Synchronization primitives (Mutex, RwLock, Barrier, Condvar, OnceLock, LazyLock)
3. Atomic types (AtomicBool/Isize/Usize, load/store/fetch_add/swap/compare_exchange, Ordering)
4. Channels (`mpsc`: multi-producer single-consumer, Receiver, Sender)
5. `Send` / `Sync` trait system (automatic derivation and manual implementation)
6. async/await syntax with the Future trait
7. Tokio runtime (`tokio::main`, `tokio::spawn`, select!, JoinSet)
8. Async I/O foundations (`tokio::fs`, `tokio::net`, `tokio::io`)
9. Bounded queues, backpressure, slow consumers, concurrency limits and overload strategies
10. Task supervision, connection lifecycles, cancellation safety and graceful shutdown
11. CPU-bound data parallelism and dedicated Rayon pools
12. Crossbeam channels, queues, work-stealing deques, and scoped threads
13. Read-heavy snapshots, sharded maps, caches, and alternative locks when measurements justify them
14. Loom model checking and Tokio runtime diagnostics

### ⚠️ Prerequisites
1. Understanding Rust ownership model (`rust-stable`)

### ❌ Inapplicable Scenarios
1. Unsafe code concurrent execution → use `rust-unsafe-ffi` skill
2. Basic ownership/borrowing → use `rust-stable` skill

## When to Use

- "Process data with multiple threads"
- "How to write async/await"
- "Tokio runtime usage"
- "Shared data between threads"
- "Avoid data races"
- "Rate limiting and graceful shutdown in high-concurrency services"
- "Tokio channel backlog or slow consumers"

## Data Privacy

This skill does not collect, store, or transmit any user data.

---

## I. OS Threads

```rust
use std::thread;

let handle = thread::spawn(move || {
    println!("Hello from thread!");
});
handle.join().unwrap();

// Thread with configuration
let builder = thread::Builder::new()
    .name("worker".into())
    .stack_size(1024 * 1024);
let handle = builder.spawn(move || { /* ... */ }).unwrap();

// scoped threads (1.63+)
let mut v = vec![1, 2, 3];
thread::scope(|s| {
    s.spawn(|| {
        v.push(4); // borrow, no move required
    });
});
println!("{v:?}"); // v remains usable
```

## II. Synchronization Primitives

```rust
use std::sync::{Arc, Mutex, RwLock, Barrier, OnceLock, LazyLock};

// Mutex (mutual exclusion lock)
let counter = Arc::new(Mutex::new(0));
let mut handles = vec![];

for _ in 0..10 {
    let counter = Arc::clone(&counter);
    handles.push(thread::spawn(move || {
        let mut num = counter.lock().unwrap();
        *num += 1;
    }));
}

// RwLock (read-write lock)
let data = Arc::new(RwLock::new(vec![1, 2, 3]));
{
    let read = data.read().unwrap();
    assert_eq!(read.len(), 3);
} // Drop the read guard before taking the write lock.
data.write().unwrap().push(4);

// OnceLock (thread-safe lazy initialization)
static CONFIG: OnceLock<String> = OnceLock::new();
let config = CONFIG.get_or_init(|| load_config());

// LazyLock
static CACHE: LazyLock<HashMap<String, Data>> = LazyLock::new(HashMap::new);
```

## III. Atomic Operations

```rust
use std::sync::atomic::{
    AtomicBool, AtomicU64, Ordering
};

static COUNTER: AtomicU64 = AtomicU64::new(0);
COUNTER.fetch_add(1, Ordering::SeqCst);

static READY: AtomicBool = AtomicBool::new(false);
READY.store(true, Ordering::Release);
let ready = READY.load(Ordering::Acquire);

// Ordering levels
// Relaxed — no ordering guarantees (only atomicity)
// Release — write visibility
// Acquire — read visibility
// AcqRel — both reads and writes visible
// SeqCst — global sequential order (strongest, but not automatically default; explicit Ordering required for atomic operations)
```

## IV. Channels

```rust
use std::sync::mpsc;

let (tx, rx) = mpsc::channel();
thread::spawn(move || {
    tx.send(1).unwrap();
    tx.send(2).unwrap();
});
for received in rx {
    println!("Got: {received}");
}

// Multi-producer scenario
let (tx, rx) = mpsc::channel();
let tx1 = tx.clone();
```

## V. async/await

```rust
use tokio::time;

async fn do_work(id: u32) -> &'static str {
    time::sleep(time::Duration::from_secs(1)).await;
    println!("Task {id} done");
    "ok"
}

#[tokio::main]
async fn main() {
    // Concurrent execution
    let (r1, r2) = tokio::join!(do_work(1), do_work(2));

    // select!
    tokio::select! {
        result = do_work(1) => println!("task1: {result}"),
        result = do_work(2) => println!("task2: {result}"),
    }

    // tokio::spawn
    let handle = tokio::spawn(do_work(3));
    handle.await.unwrap();
}
```

## VI. Send / Sync

```rust
// T is Send if its ownership can be transferred across threads
// &T is Sync if it can be shared references across threads

// Types that are both Send + Sync: Arc<Mutex<T>>, i32, &'static str
// !Send types: Rc<T>, *const T
// !Sync types: RefCell<T>, Cell<T>

// Manual implementations are unsafe contracts. Do not add them merely to
// satisfy a compiler error; prove aliasing, lifetime, and thread-safety first.
```

## VII. Select the Execution Model

| Workload | Default starting point | Avoid |
|---|---|---|
| Many readiness-driven network operations | Tokio tasks with bounded admission | One task or buffer per unbounded input |
| CPU-heavy independent items | Rayon parallel iterators or a dedicated pool | Running long CPU work on Tokio workers |
| Blocking filesystem, FFI, or legacy APIs | Bounded `spawn_blocking` submissions or a dedicated pool | Treating Tokio's blocking queue as backpressure |
| Synchronous MPMC messaging or work stealing | Crossbeam channels, queues, or deques | Selecting lock-free structures without measurement |
| Small shared state with short critical sections | `std::sync` locks | Holding guards across `.await` or callbacks |
| Read-mostly immutable snapshots | `ArcSwap` after profiling | A concurrent map for every read-heavy value |
| Shared keyed mutable state | Sharded ownership or `DashMap` after contention tests | Multi-key operations without an atomicity design |
| Expiring concurrent cache | Moka with explicit capacity and eviction policy | An unbounded map called a cache |

Tokio is primarily for I/O concurrency; Rayon is for CPU parallelism. Mixing them requires an explicit handoff, independent concurrency limits, and shutdown ownership. Read [Concurrency Tool Selection](references/concurrency-tool-selection.md) before introducing a third-party primitive.

## Workflow

1. **Classify the workload** — separate readiness-driven I/O, CPU parallelism, blocking calls, synchronization, and durable messaging before selecting a runtime or primitive.
2. **Write concurrency budgets** — define maximum connections, in-flight tasks, queue capacity, item size, timeouts, memory, CPU pools, and shutdown deadlines.
3. **Determine state ownership** — prefer partitioned or single-writer ownership; share state only with an explicit atomicity and lock-ordering contract.
4. **Select communication semantics** — choose bounded point-to-point, request/reply, latest-value, lossy broadcast, or durable replay deliberately; specify queue-full and receiver-lag behavior.
5. **Supervise execution** — retain task or thread handles, propagate failure, contain panic, prevent orphan work, and define caller-cancellation behavior.
6. **Design graceful shutdown** — stop admission, close producers, publish cancellation, join within a deadline, flush required state, and return unresolved failures.
7. **Measure before tuning** — record throughput, p50/p95/p99 latency, queue depth, saturation, task poll time, wakeups, lock wait, CPU, allocations, and RSS.
8. **Verify the model** — test overload and cancellation, use Loom for small synchronization state machines, and use tokio-console or tracing for runtime stalls. Read [Concurrency Testing and Diagnostics](references/concurrency-testing-and-diagnostics.md).

## Gotchas

1. Mutex::lock() returns a `MutexGuard`; do not await before dropping to avoid deadlocks
2. tokio::spawn's Future must be both Send and 'static; non-Send references will cause compilation errors
3. Async closures capture ownership differently than regular closures — use the move keyword explicitly for transfer of state
4. Cancelled Futures in select! branches do not execute cleanup logic directly before dropping
5. Atomic Ordering is not relational semantics; misuse of Relaxed can lead to unexpected memory ordering issues
6. broadcast lag is distinct from normal success paths; must choose between discarding, rebuilding snapshots, disconnecting slow consumers, or persistently replaying events
7. max_blocking_threads limits only the number of blocking threads and does not provide backpressure for submission queues; high-cost tasks require Semaphore or bounded queues
8. JoinSet returns results in completion order; if API requires input ordering, carry indices through to restore sequence during aggregation
9. `DashMap`, `parking_lot`, `ArcSwap`, and lock-free queues change semantics as well as performance; benchmarks do not replace invariant review
10. Loom sees only synchronization performed through Loom-aware types and can suffer state-space explosion; keep models small and deterministic
11. Rayon work may outlive the async caller unless cancellation and pool ownership are designed explicitly

## On-Demand Resources

- [Concurrency Examples](examples/examples.md)
- [Type & Tool Quick Reference](references/references.md)
- [Concurrency Tool Selection](references/concurrency-tool-selection.md): Read when choosing Tokio, Rayon, Crossbeam, locks, sharded maps, snapshots, or caches.
- [Concurrency Testing and Diagnostics](references/concurrency-testing-and-diagnostics.md): Read when proving synchronization correctness, diagnosing runtime stalls, or load-testing overload and shutdown.
- [Production Async Service Patterns](references/production-async-services.md): Read when designing actors, backpressure, slow consumers, task supervision, runtime configuration, and shutdown protocols.
- `examples/golden-threads/`: CI-built scoped thread examples

## Official References

- [std::thread Documentation](https://doc.rust-lang.org/std/thread/)
- [std::sync Documentation](https://doc.rust-lang.org/std/sync/)
- [std::sync::atomic Documentation](https://doc.rust-lang.org/std/sync/atomic/)
- [Async Book](https://rust-lang.github.io/async-book/)
- [Tokio Guide](https://tokio.rs/tokio/tutorial)
- [Rayon](https://docs.rs/rayon/)
- [Crossbeam](https://docs.rs/crossbeam/)
- [Loom](https://docs.rs/loom/)
