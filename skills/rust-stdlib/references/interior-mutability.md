# Interior Mutability — Cell, RefCell, OnceCell, OnceLock, Mutex, RwLock

> Companion to `SKILL.md` Part 4. Canonical source: [std::cell](https://doc.rust-lang.org/std/cell/index.html), [std::sync](https://doc.rust-lang.org/std/sync/index.html).

## What interior mutability is

The borrow checker enforces "one writer XOR many readers" at compile time, even when only one thread is involved. Interior mutability moves the check to runtime, so you can mutate through a `&T`. The trade-off is a small runtime cost and (for some types) a possible panic instead of a compile error.

## Decision matrix

| Type | Sync? | `T: Copy`? | Init | Use |
|------|-------|-----------|------|-----|
| `Cell<T>` | No | Yes | eager | Simple mutable state behind `&T` |
| `RefCell<T>` | No | No | eager | Borrow-check-at-runtime complex types |
| `OnceCell<T>` | No | No | lazy, once | Single-threaded lazy field |
| `OnceLock<T>` | Yes | No | lazy, once | Multi-threaded lazy global (Rust 1.70+) |
| `LazyLock<T>` | Yes | No | lazy, transparent | Const-declared lazy global (Rust 1.80+) |
| `Mutex<T>` | Yes | No | eager | Blocking shared mutation |
| `RwLock<T>` | Yes | No | eager | Many readers, few writers |

## Cell<T> — Copy types only

```rust
use std::cell::Cell;

let flag = Cell::new(false);
flag.set(true);                       // mutation through &Cell
let v = flag.get();                   // copies out
flag.replace(false);                  // set + return old
```

`Cell` does not give out `&mut T`; it only `get`s and `set`s copies. Zero runtime cost beyond the field itself. Use it for flags, counters, and small enums.

## RefCell<T> — runtime borrow check

```rust
use std::cell::RefCell;
use std::collections::HashMap;

let cache = RefCell::new(HashMap::<&str, i32>::new());
cache.borrow_mut().insert("a", 1);    // mutable borrow
let snap = cache.borrow();             // shared borrow
assert_eq!(snap.get("a"), Some(&1));
// drop(snap) before another borrow_mut, or panic at runtime
```

`borrow()` returns `Ref<T>`; `borrow_mut()` returns `RefMut<T>`. Borrows are tracked at runtime and must release before a conflicting borrow starts.

## RefCell panic safety

```rust
use std::cell::RefCell;

let c = RefCell::new(0);
let _m = c.borrow_mut();
let m2 = c.borrow_mut();   // PANICS: already borrowed mutably
```

| Panic trigger | Cause |
|---------------|-------|
| `borrow_mut` while `borrow` alive | Two mutable borrows attempted |
| `borrow_mut` while `borrow_mut` alive | Same |
| `borrow` while `borrow_mut` alive | Reader during writer |

Use `try_borrow` / `try_borrow_mut` to handle gracefully:

```rust
if let Ok(mut g) = cache.try_borrow_mut() {
    g.insert("b", 2);
}
```

## RefCell borrow tracking cost

`RefCell` stores a borrow counter (`isize`). Each `borrow`/`borrow_mut` increments/decrements it. Cost is tiny but non-zero — do not wrap every field in `RefCell`; wrap a single struct that needs interior mutation.

## OnceCell<T> — single-threaded lazy

```rust
use std::cell::OnceCell;

let cfg: OnceCell<Vec<String>> = OnceCell::new();
let loaded = cfg.get_or_init(|| load_config());   // runs once
let again  = cfg.get_or_init(|| load_config());   // returns existing, init never re-runs
```

`OnceCell` lets you initialize a field after construction but only once. Useful for struct fields that are filled lazily.

## OnceLock<T> — thread-safe lazy (Rust 1.70+)

```rust
use std::sync::OnceLock;

static CONFIG: OnceLock<Vec<String>> = OnceLock::new();

fn config() -> &'static Vec<String> {
    CONFIG.get_or_init(|| load_config())   // returns &'static, initialized once
}
```

`OnceLock` is `Sync` and replaces most uses of the external `once_cell::sync::Lazy` or `lazy_static!`.

## LazyLock<T> — transparent lazy (Rust 1.80+)

```rust
use std::sync::LazyLock;

static ROOTS: LazyLock<Vec<String>> = LazyLock::new(|| {
    std::env::var("ROOTS").unwrap_or_default().split(',').map(String::from).collect()
});

fn main() {
    println!("{}", ROOTS.len());   // initialized on first deref
}
```

`LazyLock` derefs to `&T` transparently, so callers use it as if it were the value. Prefer it over `OnceLock` for globals declared in `static`.

## Mutex<T> — blocking multi-thread

```rust
use std::sync::Mutex;

let state = Mutex::new(0i32);
{
    let mut g = state.lock().unwrap();   // blocks until exclusive
    *g += 1;
}                                         // guard drops, lock released
```

`Mutex` is the multi-threaded analogue of `RefCell`. The guard releases on drop. See `std-concurrency.md` for poison recovery and patterns.

## RwLock<T> — many readers

```rust
use std::sync::RwLock;

let data = RwLock::new(vec![1, 2, 3]);
{
    let r1 = data.read().unwrap();
    let r2 = data.read().unwrap();    // multiple readers OK
    assert_eq!(*r1, *r2);
}
{
    let mut w = data.write().unwrap(); // exclusive
    w.push(4);
}
```

Use `RwLock` when reads vastly outnumber writes and the critical section is non-trivial; otherwise `Mutex` is simpler and often faster.

## Choose table

| Situation | Pick |
|-----------|------|
| `Copy` type, simple mutation | `Cell<T>` |
| Single-thread, complex mutation behind `&T` | `RefCell<T>` |
| Single-thread, lazy struct field | `OnceCell<T>` |
| Multi-thread, lazy global, manual init | `OnceLock<T>` (1.70+) |
| Multi-thread, lazy global, transparent | `LazyLock<T>` (1.80+) |
| Multi-thread, exclusive mutation | `Mutex<T>` |
| Multi-thread, read-heavy | `RwLock<T>` |
| Multi-thread, simple counter | `AtomicUsize` |

## Common pitfalls

| Pitfall | Fix |
|---------|-----|
| `RefCell` sent across threads | It is `!Sync`; use `Mutex` or `RwLock` |
| Hidden double borrow in helper called while holding `borrow_mut` | Restructure so helpers take `&T` not `&RefCell<T>`, or use `try_borrow_mut` |
| `OnceLock::get_or_init` returning `&'static` from non-static | Only `static` bindings give `'static`; locals give a borrow scoped to the cell |
| Wrapping every field in `Cell`/`RefCell` | Wrap the whole struct once |
| `Mutex::lock().unwrap()` panicking after a panic | Recover with `e.into_inner()` if you accept the risk |

## Reference

- [std::cell](https://doc.rust-lang.org/std/cell/index.html) — [Cell](https://doc.rust-lang.org/std/cell/struct.Cell.html) / [RefCell](https://doc.rust-lang.org/std/cell/struct.RefCell.html) / [OnceCell](https://doc.rust-lang.org/std/cell/struct.OnceCell.html)
- [std::sync::OnceLock (Rust 1.70+)](https://doc.rust-lang.org/std/sync/struct.OnceLock.html) / [LazyLock (Rust 1.80+)](https://doc.rust-lang.org/std/sync/struct.LazyLock.html)
- [std::sync::Mutex](https://doc.rust-lang.org/std/sync/struct.Mutex.html) / [RwLock](https://doc.rust-lang.org/std/sync/struct.RwLock.html)
- [Rust Standard Library](https://doc.rust-lang.org/std/)
