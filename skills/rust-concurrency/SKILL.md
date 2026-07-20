---
name: rust-concurrency
description: Design, implement, diagnose, and test Rust concurrency with threads, Send and Sync, mutexes, atomics, channels, async runtimes, cancellation, bounded backpressure, actor ownership, task supervision, graceful shutdown, and overload control. Use when users ask about shared state, deadlocks, async tasks, Tokio, high concurrency, daemon resource budgets, slow consumers, worker pools, or concurrent correctness.
---

# Rust Concurrency Programming

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
let read = data.read().unwrap();
let write = data.write().unwrap();

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

// Manual implementation (requires unsafe)
struct MyType(*const u8);
unsafe impl Send for MyType {}
unsafe impl Sync for MyType {}
```

## Workflow

1. **Write concurrency budget** — define maximum connections, in-flight tasks, queue capacity, per-item timeouts, memory budgets, and shutdown timelines.
2. **Determine state ownership priorities** — prefer single-writer/actor patterns; if sharing is required, split locks by responsibility while distinguishing between synchronous locks, asynchronous locks, and atomic states.
3. **Select communication semantics** — use bounded `mpsc + oneshot` for requests/responses, `watch` for latest status updates, reserve `broadcast` only when multiple subscribers are allowed to lose events; clearly specify queue fullness, shutdown strategies, lag handling.
4. **Supervise tasks** — save `JoinHandle`s or `JoinSet`, define how subtasks fail, panic, and respond to caller cancellation and parent task exit without orphaned spawns.
5. **Design graceful shutdown sequence** — stop accepting new work, broadcast closure signals, cancel pending tasks, wait for bounded duration, release resources, and aggregate errors.
6. **Measure runtime after adjustments** — determine worker count based on ready drivers, CPU utilization, blocking call counts, and wake costs; isolate blocking work to `spawn_blocking` or dedicated thread pools with individual submission limits.
7. **Validate failure paths** — cover full queue saturation, slow consumers, out-of-order completion, partial failures, peer disconnection, timeouts, cancellation scenarios, race conditions during shutdown, task leaks.

## Gotchas

1. Mutex::lock() returns a `MutexGuard`; do not await before dropping to avoid deadlocks
2. tokio::spawn's Future must be both Send and 'static; non-Send references will cause compilation errors
3. Async closures capture ownership differently than regular closures — use the move keyword explicitly for transfer of state
4. Cancelled Futures in select! branches do not execute cleanup logic directly before dropping
5. Atomic Ordering is not relational semantics; misuse of Relaxed can lead to unexpected memory ordering issues
6. broadcast lag is distinct from normal success paths; must choose between discarding, rebuilding snapshots, disconnecting slow consumers, or persistently replaying events
7. max_blocking_threads limits only the number of blocking threads and does not provide backpressure for submission queues; high-cost tasks require Semaphore or bounded queues
8. JoinSet returns results in completion order; if API requires input ordering, carry indices through to restore sequence during aggregation

## On-Demand Resources

- [Concurrency Examples](examples/examples.md)
- [Type & Tool Quick Reference](references/references.md)
- [Production Async Service Patterns](references/production-async-services.md): Read when designing actors, backpressure, slow consumers, task supervision, runtime configuration, and shutdown protocols.
- `examples/golden-threads/`: CI-built scoped thread examples

## Official References

- [std::thread Documentation](https://doc.rust-lang.org/std/thread/)
- [std::sync Documentation](https://doc.rust-lang.org/std/sync/)
- [std::sync::atomic Documentation](https://doc.rust-lang.org/std/sync/atomic/)
- [Async Book](https://rust-lang.github.io/async-book/)
- [Tokio Guide](https://tokio.rs/tokio/tutorial)
