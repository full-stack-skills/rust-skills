---
name: rust-stdlib
description: Select and compose Rust standard-library APIs — collections (HashMap/BTreeMap/Vec/VecDeque/LinkedList/BinaryHeap), smart pointers (Box/Rc/Arc/RefCell/Mutex/OnceLock/LazyLock), string types (String/&str/OsString/PathBuf/Cow), interior mutability (Cell/RefCell/OnceCell/OnceLock), I/O streams (Read/Write/BufRead), iterators, Option/Result combinators, threads and mpsc channels, time (Duration/Instant/SystemTime), paths, env, process, fs, net, and module selection decisions. Use when users ask "which std type should I use", compare collection/pointer/string alternatives, design Option/Result chains, choose Cell vs RefCell vs Mutex, work with std threads/channels, or pick the right std module for a task; hand async runtime to rust-concurrency, language semantics to rust-stable, and application-layer concerns to domain skills.
---

# Rust Standard Library — API Selection and Composition

> Authority: [Rust Standard Library](https://doc.rust-lang.org/std/) — the canonical reference. Read `references/std-module-index.md` for the full module map.

This skill owns **choosing and composing std APIs**: which collection, which smart pointer, which string type, which I/O trait, which iterator pattern. It does not own language semantics (`rust-stable`), async runtime (`rust-concurrency`), or application-layer concerns (the domain skills).

## Capability Boundaries

### ✅ Strengths
1. Picking the right collection (HashMap vs BTreeMap vs Vec vs VecDeque vs LinkedList vs BinaryHeap)
2. Choosing the right smart pointer (Box vs Rc vs Arc vs RefCell vs Mutex vs OnceLock)
3. Selecting the right string type (String vs &str vs OsString vs PathBuf vs Cow)
4. Choosing interior mutability primitive (Cell vs RefCell vs OnceCell vs OnceLock vs LazyLock)
5. Designing Option/Result combinator chains (map, and_then, unwrap_or_else, ok_or, transpose)
6. Selecting I/O trait (Read vs Write vs BufRead vs Seek vs AsyncRead)
7. Choosing iterator pattern (iter vs into_iter vs owning iterator, lazy vs collect)
8. Using std concurrency primitives (thread, mpsc, barrier, Once, scoped threads)
9. Selecting time API (Duration vs Instant vs SystemTime vs TryFromFloat)
10. Cross-platform path handling (Path vs PathBuf, fs, env, process::Command)

### ⚠️ Prerequisites
1. Rust ownership and lifetimes — see `rust-stable`
2. Cargo and project structure — see `rust-cargo-build`, `rust-workspace`

### ❌ Out of Scope
1. Async runtime (Tokio, async-std) → `rust-concurrency`
2. Language semantics (ownership, traits, lifetimes) → `rust-stable`
3. Application-layer concerns (CLI, web, database) → domain skills
4. Unsafe and FFI → `rust-unsafe-ffi`

## Data Privacy

This skill does not collect, store, or transmit user data.

---

# Part 1: Collections

## Decision tree

```
Need a collection?
│
├─ Key-value lookup?
│   ├─ Order doesn't matter, fast lookup → HashMap<K, V>
│   ├─ Need sorted iteration / range queries → BTreeMap<K, V>
│   └─ Tiny (<20 entries), linear scan OK → Vec<(K, V)> with .iter().find()
│
├─ Sequence?
│   ├─ Append/pop from end → Vec<T>
│   ├─ Push/pop from both ends → VecDeque<T>
│   ├─ Insert/remove from middle frequently → LinkedList<T> (rare; usually Vec is better)
│   └─ Priority queue / always-min-first → BinaryHeap<T>
│
├─ Set?
│   ├─ Fast membership, no order → HashSet<T>
│   └─ Sorted iteration → BTreeSet<T>
│
└─ No collection needed — use Vec<T>
```

## Quick reference

| Type | Order | Lookup | Insert | When |
|------|-------|---------|--------|------|
| `Vec<T>` | insertion | O(n) by value, O(1) by index | O(1) amortized push | Default sequence |
| `VecDeque<T>` | insertion | O(1) front/back | O(1) front/back | Queue, sliding window |
| `LinkedList<T>` | insertion | O(n) | O(1) anywhere with cursor | Almost never; prefer Vec |
| `BinaryHeap<T>` | priority | O(1) peek | O(log n) push/pop | Priority queue |
| `HashMap<K,V>` | none | O(1) avg | O(1) avg | Fast lookup, no order |
| `BTreeMap<K,V>` | sorted | O(log n) | O(log n) | Ordered keys, range queries |
| `HashSet<T>` | none | O(1) avg | O(1) avg | Membership |
| `BTreeSet<T>` | sorted | O(log n) | O(log n) | Sorted membership |

See `references/collections.md` for allocation behavior, hasher selection (`BuildHasherDefault`/`FxHashMap`), and entry API patterns.

## Entry API — avoid double lookup

```rust
use std::collections::HashMap;

let mut counts: HashMap<&str, u32> = HashMap::new();
for word in text.split_whitespace() {
    *counts.entry(word).or_insert(0) += 1;   // single hash, no double lookup
}
```

---

# Part 2: Smart Pointers

## Decision tree

```
Need shared/indirected ownership?
│
├─ Single owner, heap-allocated → Box<T>
│
├─ Multiple readers, single thread → Rc<T>
│   └─ Need to mutate through shared ref → Rc<RefCell<T>>
│
├─ Multiple readers, multiple threads → Arc<T>
│   └─ Need to mutate through shared ref → Arc<Mutex<T>> or Arc<RwLock<T>>
│
├─ Need lazy one-time init → OnceLock<T> (sync) or once_cell::Lazy
│
└─ Need interior mutability (no shared ownership)?
    ├─ Copy type, simple → Cell<T>
    ├─ Non-Copy, complex → RefCell<T> (single thread)
    └─ Multi-thread → Mutex<T> or RwLock<T>
```

## Quick reference

| Type | Ownership | Thread-safe | Mutability | Use |
|------|-----------|-------------|------------|-----|
| `Box<T>` | Single | Yes | Direct (owned) | Heap allocation, recursive types |
| `Rc<T>` | Shared | **No** | Immutable only | Reference counting, single-threaded |
| `Arc<T>` | Shared | Yes | Immutable only | Atomic RC, multi-threaded |
| `Cell<T>` | Single | **No** | Interior (Copy only) | Simple mutable state |
| `RefCell<T>` | Single | **No** | Interior (borrow check at runtime) | Mutation behind shared ref |
| `Mutex<T>` | Single | Yes | Interior (lock) | Shared mutable state, sync |
| `RwLock<T>` | Single | Yes | Interior (read/write lock) | Many readers, few writers |
| `OnceLock<T>` | Single | Yes | One-time init | Lazy globals, `std::sync::OnceLock` |
| `LazyLock<T>` | Single | Yes | One-time init, transparent deref | Const-ish globals (Rust 1.80+) |

See `references/smart-pointers.md` for trade-offs, drop ordering, and `Weak<T>` for cycles.

---

# Part 3: String Types

## Decision tree

```
Working with text?
│
├─ Function parameter → &str (always)
├─ Owned, mutable, UTF-8 → String
├─ Borrowed, UTF-8, with mixed owned/borrowed → Cow<'a, str>
├─ OS path (Windows/Unix native) → OsString (owned) / OsStr (borrowed)
├─ Filesystem path → PathBuf (owned) / Path (borrowed)
└─ Bytes that might not be UTF-8 → Vec<u8> / &[u8]
```

## Quick reference

| Type | Encoding | Owned? | Use |
|------|----------|--------|-----|
| `&str` | UTF-8 | No | Function params, string literals |
| `String` | UTF-8 | Yes | Owned mutable UTF-8 text |
| `OsString`/`OsStr` | Platform-native | Yes/No | Environment, process args |
| `PathBuf`/`Path` | Platform-native | Yes/No | Filesystem paths |
| `Cow<'a, str>` | UTF-8 | Maybe | Zero-copy when possible, owned when needed |
| `Vec<u8>`/`&[u8]` | Bytes | Yes/No | Binary data, non-UTF-8 |

See `references/string-types.md` for conversion (`.to_string()` vs `.to_owned()` vs `.into()`), `Cow` usage, and `&str` slicing safety (`is_char_boundary`).

---

# Part 4: Interior Mutability

## Cell vs RefCell vs OnceCell

```rust
use std::cell::{Cell, RefCell, OnceCell};

// Cell: only for Copy types, no borrow checking
let counter = Cell::new(0);
counter.set(counter.get() + 1);

// RefCell: for non-Copy types, runtime borrow check (panics on double borrow)
let cache = RefCell::new(HashMap::new());
cache.borrow_mut().insert("k", 42);

// OnceCell: one-time initialization
static CONFIG: OnceCell<Config> = OnceCell::new();
let cfg = CONFIG.get_or_init(|| Config::load());
```

| Type | Sync? | Use |
|------|-------|-----|
| `Cell<T>` | No | Copy types only, simple mutation |
| `RefCell<T>` | No | Non-Copy types, single-thread |
| `OnceCell<T>` | No | One-time lazy init |
| `OnceLock<T>` | **Yes** | One-time lazy init, multi-thread (std 1.70+) |
| `LazyLock<T>` | **Yes** | Transparent lazy init (std 1.80+) |

See `references/interior-mutability.md` for panic-safety (RefCell double-borrow), choose-Cell-vs-RefCell, and `Atomic*` for multi-thread.

---

# Part 5: Option and Result Combinators

## Option combinators

```rust
// map: transform inner value
name.map(|n| n.to_uppercase())                    // Option<String>

// and_then: chain fallible operations
id.and_then(|i| db.lookup(i))                     // Option<User>

// unwrap_or / unwrap_or_else: provide default
port.unwrap_or(8080)
port.unwrap_or_else(|| env::var("PORT").unwrap_or("8080").parse().unwrap())

// ok_or / ok_or_else: convert Option to Result
user.ok_or(Error::NotFound)?
user.ok_or_else(|| Error::UserMissing(id))?

// filter, is_some, is_some_and
age.filter(|&a| a >= 18)
opt.is_some_and(|x| x > 0)

// transpose: swap Option<Result> → Result<Option>
let x: Result<Option<i32>, _> = Some("5").parse::<i32>().map(Some);
```

## Result combinators

```rust
// ? for propagation (prefer over explicit match)
fn load() -> Result<Config, Error> { Ok(parse(file_read()?)?) }

// map_err: convert error type
file_read().map_err(|e| Error::Io(e))?

// map: transform success value
parse(s).map(|n| n * 2)

// and_then: chain fallible
validate(input).and_then(process)

// or_else / or: fallback on error
primary.or_else(|_| fallback())
```

## Common patterns

| Pattern | Code |
|---------|------|
| Try parsing, fallback to default | `s.parse().unwrap_or(default)` |
| Early return on error | `let x = result?;` |
| Convert Option to Result | `opt.ok_or(Error::Missing)?` |
| Collect all Results | `results.collect::<Result<Vec<_>, _>>()` |
| Try all, return first success | `opts.into_iter().find_map(|o| o.try_it().ok())` |

See `references/option-result-combinators.md` for the full combinator table and refactor patterns.

---

# Part 6: I/O Streams

## Trait hierarchy

```
Read ────┐
         ├─ BufRead (adds buffering, lines())
Write ───┘
Seek (random access)
```

## Choosing

| Need | Use |
|------|-----|
| Read bytes from a source | `impl Read` (File, Cursor, stdin) |
| Buffered reading (lines, until) | `impl BufRead` (BufReader wrapping) |
| Write bytes to a destination | `impl Write` (File, stdout, Vec) |
| Random access | `impl Seek` (File) |
| Async I/O | `tokio::io::AsyncRead`/`AsyncWrite` (rust-concurrency) |

```rust
use std::io::{BufRead, BufReader, Read, Write};
use std::fs::File;

let f = File::open("log.txt")?;          // impl Read
let reader = BufReader::new(f);          // wrap for BufRead
for line in reader.lines() {             // BufRead::lines
    println!("{}", line?);
}
```

See `references/io-streams.md` for `Cursor<Vec<u8>>`, error handling (`io::Result`), and converting between sync and async.

---

# Part 7: Iterators

## Choosing

| Need | Use |
|------|-----|
| Borrow elements | `.iter()` → `Iterator<Item = &T>` |
| Mutably borrow | `.iter_mut()` → `Iterator<Item = &mut T>` |
| Consume | `.into_iter()` → `Iterator<Item = T>` |
| Index pairs | `.iter().enumerate()` |
| Filter | `.filter(\|x\| *x > 0)` |
| Transform | `.map(\|x\| x * 2)` |
| Flat | `.flat_map(\|x\| x.iter())` |
| Collect to Vec | `.collect::<Vec<_>>()` |
| Collect to HashMap | `.collect::<HashMap<_, _>>()` (from `(K, V)` tuples) |
| First match | `.find(\|x\| *x == 5)` |
| Any/all | `.any(\|x\| *x > 0)`, `.all(\|x\| *x > 0)` |
| Group/sum | `.sum::<i32>()`, `.product()`, `.fold(0, \|a, b\| a + b)` |

```rust
// Borrowed iteration is the default
let v = vec![1, 2, 3];
for x in &v { /* x: &i32 */ }      // .iter()
for x in &mut v { /* x: &mut i32 */ }
for x in v { /* x: i32, v consumed */ }
```

See `references/iterators.md` for custom iterators (impl `Iterator`), lazy evaluation, and zero-cost abstractions.

---

# Part 8: Std Concurrency

The standard library provides threads, channels, and sync primitives. For async, see `rust-concurrency`.

## Threads

```rust
use std::thread;
use std::time::Duration;

let handle = thread::spawn(|| {
    thread::sleep(Duration::from_millis(500));
    "result"
});
let r = handle.join().unwrap();   // wait, get result
```

## Scoped threads (Rust 1.63+) — borrow without `'static`

```rust
let mut data = vec![1, 2, 3];
thread::scope(|s| {
    s.spawn(|| { data[0] += 1; });
    s.spawn(|| { data[1] += 1; });
});   // all threads joined here; data borrow ends
```

## mpsc channels

```rust
use std::sync::mpsc;
use std::thread;

let (tx, rx) = mpsc::channel();
thread::spawn(move || {
    tx.send(42).unwrap();
});
println!("{}", rx.recv().unwrap());
```

## Sync primitives

| Primitive | Use |
|-----------|-----|
| `Mutex<T>` | Exclusive lock, sync interior mutability |
| `RwLock<T>` | Many readers, few writers |
| `Arc<T>` | Atomic reference counting |
| `Barrier` | Synchronize multiple threads at a point |
| `Once` | One-time initialization |
| `Condvar` | Wait/notify |
| `Atomic*` (AtomicUsize, AtomicBool, ...) | Lock-free counters, flags |

See `references/std-concurrency.md` for `Arc<Mutex<T>>` patterns, poison recovery, and when to graduate to Tokio.

---

# Part 9: Time, Path, Process

## Time

```rust
use std::time::{Duration, Instant, SystemTime};

let start = Instant::now();
expensive_op();
println!("took {:?}", start.elapsed());   // Duration

let five_secs = Duration::from_secs(5);
let mixed = Duration::new(5, 500_000_000);  // 5.5s

let now = SystemTime::now();
let since_epoch = now.duration_since(SystemTime::UNIX_EPOCH)?;
```

- `Duration` — span of time (no specific moment)
- `Instant` — monotonic moment, for measuring elapsed
- `SystemTime` — wall-clock, for timestamps (can go backwards!)

## Path

```rust
use std::path::{Path, PathBuf};

let p = Path::new("/usr/bin/foo");
let stem = p.file_stem();      // "foo"
let ext = p.extension();       // "foo" → None; "foo.txt" → "txt"

let joined = PathBuf::from("/usr").join("bin").join("foo");
let parent = p.parent();       // "/usr/bin"
```

Always use `Path`/`PathBuf` for filesystem paths — never `String`. Cross-platform safe.

## Process

```rust
use std::process::Command;

let output = Command::new("ls")
    .arg("-l")
    .arg("/")
    .output()?;          // waits, returns Output
println!("{}", String::from_utf8_lossy(&output.stdout));

// Stream stdin/stdout
use std::process::Stdio;
let mut child = Command::new("cat")
    .stdin(Stdio::piped())
    .stdout(Stdio::piped())
    .spawn()?;
```

See `references/process-and-fs.md` for `Command` exit codes, signal handling, and `fs` module (`read`, `write`, `create_dir`, metadata).

---

## Workflow

1. **Identify the need** — collection, pointer, string, I/O, iterator, or system interface?
2. **Apply decision tree** — pick from the relevant Part above
3. **Check MSRV** — some APIs (`OnceLock` 1.70, `LazyLock` 1.80, scoped threads 1.63) need recent stable
4. **Compose with combinators** — prefer `Option`/`Result` chains over explicit `match`
5. **Verify** — `cargo check`, `cargo test`, `cargo clippy`
6. **Hand off** — async runtime → `rust-concurrency`; unsafe → `rust-unsafe-ffi`; application concerns → domain skills

## Decision Shortcuts

| Question | Answer |
|---------|--------|
| Default collection? | `Vec<T>` |
| Need key-value lookup? | `HashMap` (unordered) or `BTreeMap` (sorted) |
| Shared ownership? | `Rc` (single-thread) or `Arc` (multi-thread) |
| Mutable shared state? | `RefCell` (single) or `Mutex`/`RwLock` (multi) |
| String parameter? | `&str` always |
| File path? | `Path` / `PathBuf` |
| Lazy global? | `OnceLock` (1.70+) or `LazyLock` (1.80+) |
| Iterate borrowed? | `.iter()` |
| Two-way queue? | `VecDeque` |
| Priority queue? | `BinaryHeap` |

## Resources

- [Collections Deep Dive](references/collections.md)
- [Smart Pointers](references/smart-pointers.md)
- [String Types](references/string-types.md)
- [Option/Result Combinators](references/option-result-combinators.md)
- [I/O Streams](references/io-streams.md)
- [Iterators](references/iterators.md)
- [Std Concurrency](references/std-concurrency.md)
- [Process and Filesystem](references/process-and-fs.md)
- [Interior Mutability](references/interior-mutability.md)
- [Std Module Index](references/std-module-index.md)
- `examples/golden-stdlib/`: a crate exercising collections, pointers, channels, and iterators

## Upstream Sources

- [Rust Standard Library](https://doc.rust-lang.org/std/)
- [std::collections](https://doc.rust-lang.org/std/collections/index.html)
- [std::sync](https://doc.rust-lang.org/std/sync/index.html)
- [std::cell](https://doc.rust-lang.org/std/cell/index.html)
- [std::io](https://doc.rust-lang.org/std/io/index.html)
- [std::path](https://doc.rust-lang.org/std/path/index.html)
- [std::process](https://doc.rust-lang.org/std/process/index.html)
- [std::thread](https://doc.rust-lang.org/std/thread/index.html)
