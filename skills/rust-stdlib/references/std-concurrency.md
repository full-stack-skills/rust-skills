# Std Concurrency — Threads, Channels, Sync Primitives

> Companion to `SKILL.md` Part 8. Canonical sources: [std::thread](https://doc.rust-lang.org/std/thread/index.html), [std::sync](https://doc.rust-lang.org/std/sync/index.html), [std::sync::mpsc](https://doc.rust-lang.org/std/sync/mpsc/index.html). For async, see the `rust-concurrency` skill.

## Threads

`thread::spawn` requires `'static` closures and `'static` captures, because the thread may outlive the caller.

```rust
use std::thread;
use std::time::Duration;

let handle = thread::spawn(|| {
    thread::sleep(Duration::from_millis(100));
    42
});
let r = handle.join().unwrap();   // blocks until done; Result<T, Box<dyn Any>>
```

`join()` blocks the caller. It returns `Result` because the child may have panicked — `unwrap()` propagates that panic to the parent.

## Scoped threads (Rust 1.63+) — borrow without 'static

`thread::scope` lets spawned threads borrow non-`'static` data; the scope blocks until all threads finish, so borrows are safe.

```rust
use std::thread;

let mut data = vec![0u32; 4];
thread::scope(|s| {
    for (i, chunk) in data.chunks_mut(2).enumerate() {
        s.spawn(move || {
            for x in chunk.iter_mut() { *x = i as u32 + 1; }
        });
    }
});   // joins all spawned threads here
assert_eq!(data, vec![1, 1, 2, 2]);
```

Use scoped threads whenever you would otherwise need `Arc` just to share borrowed data across threads.

## Channels — mpsc

| Channel | Bounded? | Consumers | Backpressure |
|---------|----------|-----------|--------------|
| `mpsc::channel()` | Unbounded | One | None (sender can flood) |
| `mpsc::sync_channel(n)` | Bounded (`n`) | One | Sender blocks when full |
| `crossbeam-channel::*` | Either | Many | Optional |

```rust
use std::sync::mpsc;
use std::thread;

let (tx, rx) = mpsc::channel();
for i in 0..3 {
    let tx = tx.clone();                 // multi-producer
    thread::spawn(move || tx.send(i).unwrap());
}
drop(tx);                                 // close so rx ends
while let Ok(v) = rx.recv() { println!("{v}"); }
```

`rx.recv()` blocks until a message arrives or all senders drop (then returns `Err`). `rx.try_recv()` is non-blocking; `rx.recv_timeout(d)` is timed.

`sync_channel(n)` is preferred when producers can outpace consumers: it provides backpressure.

## crossbeam-channel (third party)

[`crossbeam-channel`](https://docs.rs/crossbeam-channel) adds multi-consumer channels, selection over multiple channels, and slightly different performance characteristics. Use it when you need multiple receivers or `select!`-style behavior across channels.

## Sync primitives

| Primitive | Use |
|-----------|-----|
| `Arc<T>` | Atomic reference counting for shared read |
| `Mutex<T>` | Exclusive lock — one holder at a time |
| `RwLock<T>` | Many readers or one writer |
| `Barrier` | Wait until N threads reach a point, then release all |
| `Once` | Run initialization exactly once |
| `OnceLock<T>` | Lazy one-shot cell, returns `&T` (Rust 1.70+) |
| `Condvar` | Block until notified (paired with `Mutex`) |
| `AtomicU8/16/32/64/usize/isize/bool/ptr` | Lock-free primitives |

## Arc<Mutex<T>> and Arc<RwLock<T>>

```rust
use std::sync::{Arc, Mutex};
use std::thread;

let shared = Arc::new(Mutex::new(Vec::<i32>::new()));
let hs: Vec<_> = (0..4).map(|i| {
    let s = Arc::clone(&shared);
    thread::spawn(move || s.lock().unwrap().push(i))
}).collect();
for h in hs { h.join().unwrap(); }
assert_eq!(shared.lock().unwrap().len(), 4);
```

Guard returned by `lock()` releases the mutex on drop; derefs to `&mut T`. `RwLock::read` returns a read guard (multiple allowed), `write` returns an exclusive write guard.

## Atomics

For simple counters or flags, atomics beat `Mutex`.

```rust
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::thread;

let counter = Arc::new(AtomicUsize::new(0));
let hs: Vec<_> = (0..100).map(|_| {
    let c = Arc::clone(&counter);
    thread::spawn(move || { c.fetch_add(1, Ordering::Relaxed); })
}).collect();
for h in hs { h.join().unwrap(); }
assert_eq!(counter.load(Ordering::Relaxed), 100);
```

| Ordering | When |
|----------|------|
| `Relaxed` | No ordering needs beyond the atomic itself (counters) |
| `Acquire` / `Release` | Pair on the same atomic to publish/observe other memory |
| `AcqRel` | Read-modify-write that needs both |
| `SeqCst` | Strongest; rarely needed |

Default to `Relaxed` for counters; reach for `Acquire`/`Release` only when the atomic gates access to other data.

## Barrier, Once, Condvar

```rust
use std::sync::{Barrier, Condvar, Mutex};
use std::thread;

let barrier = Arc::new(Barrier::new(3));
for _ in 0..3 {
    let b = Arc::clone(&barrier);
    thread::spawn(move || { b.wait(); /* all start together */ });
}

let pair = Arc::new((Mutex::new(false), Condvar::new()));
let (lock, cvar) = &*pair;
let g = cvar.wait_while(lock.lock().unwrap(), |ready| !*ready).unwrap();
```

`Condvar` always pairs with a `Mutex` guarding the predicate.

## Poison recovery

If a thread panics while holding a `Mutex`, the lock is poisoned. Subsequent `lock()` calls return `Err(PoisonError)`. Recover the inner value if you can tolerate inconsistent state:

```rust
let guard = match m.lock() {
    Ok(g) => g,
    Err(p) => p.into_inner(),    // recover despite possible corruption
};
```

## When to graduate to async

Std threads are OS threads — each costs stack space (default 2 MiB on Linux, 8 MiB on macOS) and a context switch. Reach for an async runtime (Tokio, async-std) when:

- You have tens of thousands of concurrent waiters (network servers).
- Most work is I/O-bound and you would otherwise burn threads on `sleep` / `recv`.
- You need timers, cancellation, or structured concurrency across many tasks.

For CPU-bound parallelism, rayon (data parallelism) or std scoped threads remain the right choice — async adds nothing.

## Gotchas

| Pitfall | Fix |
|---------|-----|
| `Rc<T>` shared across threads | Use `Arc<T>` |
| Forgetting to `drop(tx)` in producer-consumer | Receiver loops forever |
| Deadlock from locking two mutexes in different orders | Always lock in a fixed global order |
| `Mutex` around a hot counter | `AtomicUsize` |
| `thread::spawn` with a borrowed local | Use `thread::scope` or `Arc` |
| Blocking `recv` on the same thread that should send | Use `try_recv` or scoped threads |

## Reference

- [std::thread](https://doc.rust-lang.org/std/thread/index.html)
- [std::sync::mpsc](https://doc.rust-lang.org/std/sync/mpsc/index.html)
- [std::sync::Mutex](https://doc.rust-lang.org/std/sync/struct.Mutex.html) / [RwLock](https://doc.rust-lang.org/std/sync/struct.RwLock.html) / [Arc](https://doc.rust-lang.org/std/sync/struct.Arc.html)
- [std::sync::atomic](https://doc.rust-lang.org/std/sync/atomic/index.html)
- [Scoped threads (Rust 1.63+)](https://doc.rust-lang.org/std/thread/fn.scope.html)
- [Rust Standard Library](https://doc.rust-lang.org/std/)
