# Large Crate Layout — 50-File Worked Example

How a large Rust crate (10k+ LOC, 50+ source files) is organized. The example is a fictional async runtime crate, but the structure applies to any large library.

---

## Design Principles

1. **`lib.rs` is a thin facade** — 50–80 lines max. Only `mod` declarations and curated `pub use`.
2. **Each top-level directory is a subdomain** — runtime, net, buffer, etc. Each has its own `mod.rs` (or modern `<name>.rs`) acting as a sub-facade.
3. **Depth matches complexity** — simple subdomains stay flat (`net.rs`); complex ones nest (`runtime/scheduler/task.rs`).
4. **Privacy is the default** — the public API surface is < 5% of the codebase.
5. **No vague module names** — every name answers "what's inside?"

---

## Complete Tree

```text
my_runtime/
├── Cargo.toml
├── src/
│   ├── lib.rs                      # 60 lines: mod decls + facade
│   ├── error.rs                    # crate-wide error type
│   │
│   ├── runtime.rs                  # modern layout: runtime.rs + runtime/
│   ├── runtime/
│   │   ├── scheduler.rs            # task scheduler
│   │   ├── scheduler/              # nest deeper when one file overflows
│   │   │   ├── queue.rs
│   │   │   └── timer.rs
│   │   ├── task.rs                 # task abstraction
│   │   ├── waker.rs
│   │   └── metrics.rs              # internal — pub(crate)
│   │
│   ├── net.rs                      # modern layout: net.rs + net/
│   ├── net/
│   │   ├── tcp.rs                  # TCP listener / stream
│   │   ├── tcp/                    # TCP internals
│   │   │   ├── listener.rs
│   │   │   └── stream.rs
│   │   ├── udp.rs
│   │   └── dns.rs                  # DNS resolver
│   │
│   ├── buffer/
│   │   ├── mod.rs                  # legacy layout (mixed is bad — pick one)
│   │   ├── read.rs
│   │   ├── write.rs
│   │   └── codec.rs                # encoder/decoder traits
│   │
│   ├── time.rs                     # single file — small enough
│   │
│   └── util/                       # internal helpers
│       ├── mod.rs
│       ├── hash.rs
│       └── trace.rs
│
├── tests/
│   ├── integration.rs              # integration tests — only public API
│   └── common/                     # shared test helpers
│       └── mod.rs
│
├── benches/
│   ├── scheduler.rs                # Criterion benchmarks
│   └── tcp.rs
│
└── examples/
    ├── hello.rs                    # usage examples — public API only
    └── echo_server.rs
```

---

## `lib.rs` — The Facade

```rust
//! # my_runtime
//!
//! An async runtime with networking and scheduling.
//!
//! ## Quick start
//!
//! ```rust
//! use my_runtime::{Runtime, TcpListener};
//!
//! let rt = Runtime::new()?;
//! let listener = rt.bind_tcp("127.0.0.1:8080")?;
//! ```

mod error;
mod runtime;
mod net;
mod buffer;
mod time;

// Internal — never exposed
mod util;

// ── Curated public facade ──────────────────────────────────────────
// Keep this list short (< 30 items). Every item here is a semver promise.

pub use error::{Error, Result};

// Runtime domain
pub use runtime::{Runtime, RuntimeBuilder, JoinHandle};

// Networking domain — flat types for ergonomics
pub use net::{TcpListener, UdpSocket};
// Advanced users can reach into the namespace
pub mod net {
    //! Low-level networking primitives.
    pub use crate::net::tcp::{TcpStream, TcpListener as Inner};
    pub use crate::net::udp::UdpSocket as UdpInner;
    pub use crate::net::dns::{Resolver, DnsError};
}

// Buffer types — only the most common
pub use buffer::{ReadBuffer, WriteBuffer};

// Time — single type
pub use time::Instant;
```

---

## `runtime.rs` — Sub-Facade

```rust
// src/runtime.rs
//! Task scheduler and runtime entry point.

mod scheduler;
mod task;
mod waker;

pub(crate) mod metrics;          // internal-only

pub use scheduler::Scheduler;
pub use task::{Task, JoinHandle};
pub use waker::Waker;

pub struct Runtime { /* ... */ }

impl Runtime {
    pub fn new() -> Result<Self, Error> { /* ... */ unimplemented!() }
    pub fn builder() -> RuntimeBuilder { RuntimeBuilder::default() }
    pub fn block_on<F: std::future::Future>(&self, fut: F) -> F::Output { /* ... */ unimplemented!() }
    pub fn spawn<F>(&self, fut: F) -> JoinHandle<F::Output>
    where F: std::future::Future + Send + 'static { /* ... */ unimplemented!() }
    pub fn bind_tcp(&self, addr: &str) -> Result<crate::TcpListener, Error> { /* ... */ unimplemented!() }
}

pub struct RuntimeBuilder { /* ... */ }

impl Default for RuntimeBuilder {
    fn default() -> Self { Self { /* ... */ } }
}

impl RuntimeBuilder {
    pub fn worker_threads(mut self, n: usize) -> Self { /* ... */ self }
    pub fn build(self) -> Result<Runtime, Error> { /* ... */ unimplemented!() }
}
```

---

## `runtime/scheduler.rs` — Deep Nesting

When `scheduler.rs` itself grows, promote it to a directory:

```text
runtime/
├── scheduler.rs                    # modern: scheduler.rs + scheduler/
├── scheduler/
│   ├── queue.rs                    # task queue
│   └── timer.rs                    # timer wheel
├── task.rs
└── waker.rs
```

```rust
// src/runtime/scheduler.rs
mod queue;
mod timer;

pub(crate) use queue::TaskQueue;
pub(crate) use timer::TimerWheel;

pub struct Scheduler {
    queue: TaskQueue,
    timer: TimerWheel,
}

impl Scheduler {
    pub(crate) fn new() -> Self { /* ... */ unimplemented!() }
    pub(crate) fn schedule(&self, task: super::Task) { /* ... */ }
}
```

---

## When to Promote a File to a Directory

Decision rule:

| File size | Concern count | Action |
|-----------|---------------|--------|
| < 300 lines | 1 | Keep as a file |
| 300–500 lines | 1 | Keep as a file, but watch for growth |
| 500+ lines | 1 | Promote to a directory *only if* the file is hard to navigate |
| 300+ lines | 2+ concerns | Promote to a directory, one file per concern |
| Any | Mixed concerns | Promote immediately |

---

## When to Promote a Crate Member to a Workspace Member

| Signal | Action |
|--------|--------|
| Subdomain has its own stability trajectory (one part is 1.0, another is 0.1) | Promote |
| Subdomain has a different dependency footprint (one pulls in tokio, another doesn't) | Promote |
| Subdomain is independently useful (users might want just `my-crate-types`) | Promote |
| Subdomain's code is large but tightly coupled with the rest | Keep in-crate |
| Subdomain's types appear in every other module's signatures | Keep in-crate |

See `rust-workspace` for the workspace-level decision.

---

## Testing Layout

```text
tests/
├── integration_runtime.rs       # tests Runtime::new() and block_on()
├── integration_tcp.rs           # tests TcpListener bind/accept
├── common/
│   └── mod.rs                   # shared test helpers (mod tests_common)
```

```rust
// tests/integration_runtime.rs
mod common;

#[test]
fn runtime_starts() {
    let rt = my_runtime::Runtime::new().unwrap();
    // ...
}
```

```rust
// tests/common/mod.rs
pub fn test_port() -> u16 { /* ... */ 0 }
```

Tests can only access **public** API of the crate. If you need to test internals, use unit tests in `#[cfg(test)] mod tests { ... }` inside each module.

---

## Doc Tests

```rust
// src/runtime.rs
/// Spawns a future onto the runtime.
///
/// # Example
///
/// ```
/// use my_runtime::Runtime;
///
/// let rt = Runtime::new().unwrap();
/// let handle = rt.spawn(async { 42 });
/// ```
pub fn spawn<F>(&self, fut: F) -> JoinHandle<F::Output>
where F: std::future::Future + Send + 'static { /* ... */ }
```

Doc tests are compiled and run by `cargo test`. They only see the public API, so they double as API examples.

---

## Cargo.toml for the Example Crate

```toml
[package]
name = "my_runtime"
version = "0.1.0"
edition = "2021"

[lib]
name = "my_runtime"
path = "src/lib.rs"

[dependencies]
# ...

[dev-dependencies]
criterion = "0.5"

[[bench]]
name = "scheduler"
harness = false
```

---

## Verification

```bash
cargo check                       # compiles
cargo test                        # unit + integration + doc tests pass
cargo doc --no-deps --open        # docs are clean and navigable
cargo +nightly udeps              # (optional) unused dependencies
cargo bloat --release             # (optional) binary size analysis
```

A large crate that follows this layout will have:
- `lib.rs` under 100 lines
- No file over 500 lines (split when exceeded)
- Every public item reachable via the curated facade
- Internal modules private and unreachable externally
- Clear naming — no 2-letter abbreviations, no junk drawers
