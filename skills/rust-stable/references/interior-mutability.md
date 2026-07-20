# Internal Mutability

| Type | Thread Safety Checkpoint | Use Case |
|---|---|---|
| `Cell<T>` | Single-threaded | No runtime borrowing; Copy value or replace entire content. |
| `RefCell<T>` | Single-threaded | Runtime borrowing; Dynamic borrowing, test harnesses. |
| `OnceCell<T>` | Single-threaded | Single initialization; Lazy or deferred initialization. |
| `OnceLock<T>` | Multi-threaded | Single initialization; Global or shared state. |
| `Mutex<T>` | Multi-threaded | Runtime locking for exclusive modification. |
| `RwLock<T>` | Multi-threaded | Runtime locking when read-heavy and measured. |

Rules:

- Move compile-time errors to runtime by reducing encapsulation boundaries.
  Do not cross `.await` with `std::sync` locks; defer async concurrency workloads to the [`rust-concurrency`](https://docs.rs/rust-concurrency/) crate instead.
- Avoid executing user callbacks, blocking I/O operations, or long-running computations inside locked regions.
- Prevent borrow checker panics in `RefCell`; minimize guard lifetimes where possible.

Official Sources:

- https://doc.rust-lang.org/std/cell/
  https://doc.rust-lang.org/std/sync/
