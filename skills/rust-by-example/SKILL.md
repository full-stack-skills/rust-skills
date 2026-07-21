---
name: rust-by-example
description: Show Rust patterns through short compilable examples — type conversions (From/Into/TryFrom/as/Deref), flow control (if let/while let/match/loop), functions and closures (Fn/FnMut/FnOnce, captures), modules (mod/use/pub/super/self), generics and traits (bounds/associated types/trait objects), error handling (?/Result/thiserror/anyhow), attributes (derive/cfg/inline/allow), unsafe (raw pointers/unions/ABI), procedural macros (derive/attribute/function-like), and inline asm. Use when users ask "how do I write X in Rust", need a concrete pattern with copy-pasteable code, or are migrating from Java/Python/Go/C++ and want the Rust equivalent; hand architecture decisions to rust-api-design/rust-workspace, std API selection to rust-stdlib, and async runtime to rust-concurrency.
---

# Rust by Example — Patterns Through Compilable Snippets

> Authority: [Rust by Example](https://doc.rust-lang.org/rust-by-example/) — the official example-driven tutorial. This skill condenses its 24 chapters into a routing layer that points to topic-specific reference files.

This skill owns **"how do I write X"** patterns with concrete code. It does not own architectural decisions (`rust-api-design`, `rust-workspace`), language semantics (`rust-stable`), or std API selection (`rust-stdlib`).

## Capability Boundaries

### ✅ Strengths
1. Converting between types — `From`/`Into`/`TryFrom`/`as`/`Deref`/`transmute`
2. Flow control idioms — `if let`, `while let`, `match`, `loop` with labels, `?`
3. Functions, methods, closures (`Fn`/`FnMut`/`FnOnce`), capture modes
4. Modules, `use`, `pub`, `super`/`self`/`crate`, file-based module resolution
5. Generics — functions, structs, methods, impl blocks, `where` clauses
6. Traits — definition, default methods, associated types, trait objects, object safety
7. Error handling — `?`, `Result`, `Option`, custom errors with `thiserror`, `anyhow`
8. Attributes — `#[derive]`, `#[cfg]`, `#[inline]`, `#[allow]`, `#[non_exhaustive]`
9. Unsafe — raw pointers, dereferences, `unsafe fn`/`unsafe impl`, unions, ABI
10. Procedural macros — derive, attribute, function-like (high-level routing to `rust-macros`)
11. Inline assembly — `core::arch::asm!` (rare but supported)

### ⚠️ Prerequisites
1. Basic Rust syntax — see `rust-stable`
2. Project structure — see `rust-workspace`, `rust-module-layout`

### ❌ Out of Scope
1. API design decisions → `rust-api-design`
2. Workspace / module layout → `rust-workspace`, `rust-module-layout`
3. Std API selection (which collection, which pointer) → `rust-stdlib`
4. Async runtime → `rust-concurrency`
5. Deep unsafe / FFI → `rust-unsafe-ffi`
6. Authoring complex procedural macros → `rust-macros`

## Data Privacy

This skill does not collect, store, or transmit user data.

---

# Topic Map (One Section per Pattern Category)

Each section has a short example inline; deeper patterns live in the linked reference file.

## 1. Type Conversions

```rust
// From / Into (lossless)
impl From<i32> for Wrapped { fn from(v: i32) -> Self { Self(v) } }
let w: Wrapped = 42.into();   // Into comes for free

// TryFrom (fallible)
impl TryFrom<&str> for Email {
    type Error = EmailError;
    fn try_from(s: &str) -> Result<Self, Self::Error> { /* */ }
}

// as (numeric widening/narrowing — can lose data)
let big: i64 = 1_000_000;
let small: i32 = big as i32;       // ❌ silent truncation possible

// Deref (smart-pointer coercion, NOT polymorphism)
let s: String = "hi".to_string();
let s_ref: &str = &s;              // Deref<Target=str> kicks in
```

See `references/conversions.md` for `as` vs `From` vs `TryFrom`, when each is correct.

## 2. Flow Control

```rust
// if let — single-pattern destructure
if let Some(x) = opt { /* */ }

// while let — loop until None
while let Some(line) = reader.lines().next() { /* */ }

// match with @-binding
match point {
    Point { x: 0, y } => println!("on y-axis at {y}"),
    Point { x, y: 0 } => println!("on x-axis at {x}"),
    p @ Point { x: 10..=20, .. } => println!("in x-band: {p:?}"),
    _ => {}
}

// loop with label
'outer: loop {
    loop { break 'outer; }
}
```

See `references/flow-control.md` for `match` ergonomics, guards, ranges, and when to prefer `if let`.

## 3. Functions and Closures

```rust
// Closure captures by ref/move based on use
let v = vec![1, 2, 3];
let print = || println!("{:?}", v);       // borrows
let consume = move || { v.into_iter().sum() };  // moves

// Fn / FnMut / FnOnce — how a closure borrows its environment
fn apply(f: impl Fn()) { f() }            // can be called multiple times, immutable capture
fn apply_mut(mut f: impl FnMut()) { f() } // mutable capture
fn apply_once(f: impl FnOnce() -> i32) -> i32 { f() }  // consumes captured
```

See `references/closures.md` for `move` keyword, return-type inference, and `Fn`/`FnMut`/`FnOnce` trait bounds.

## 4. Modules

```rust
// src/lib.rs
pub mod network;                  // src/network.rs OR src/network/mod.rs
pub use network::Client;          // re-export

// src/network.rs
pub struct Client { /* */ }
pub fn connect() { /* */ }
```

```rust
// Using items
use std::collections::HashMap;
use std::io::{self, Read};        // io module + Read trait
use crate::network::Client;       // absolute
use super::helper;                 // parent
use self::inner::Item;            // current
```

See `references/modules.md` for `pub`/`pub(crate)`/`pub(super)`, file-based vs `mod.rs`, and crate root re-exports. For deep layout work, route to `rust-module-layout`.

## 5. Generics

```rust
// Generic function with bound
fn first<T>(xs: &[T]) -> Option<&T> { xs.first() }

// Generic with where clause
fn sum<T>(xs: &[T]) -> T where T: Default + std::ops::AddAssign + Copy {
    let mut acc = T::default();
    for x in xs { acc += *x; }
    acc
}

// Generic struct
struct Pair<A, B> { a: A, b: B }

impl<A: Clone, B: Clone> Pair<A, B> {
    fn swapped(&self) -> Pair<B, A> { Pair { a: self.b.clone(), b: self.a.clone() } }
}
```

See `references/generics-traits.md` for monomorphization cost, when to use generics vs trait objects, and associated types vs generics.

## 6. Traits

```rust
// Definition with default method
pub trait Summary {
    fn summarize(&self) -> String;
    fn default_summary(&self) -> String { format!("(no summary)") }
}

// Trait object (dynamic dispatch)
fn print_summary(item: &dyn Summary) { println!("{}", item.summarize()); }

// Generic (static dispatch)
fn print_summary_generic<T: Summary>(item: &T) { println!("{}", item.summarize()); }

// Associated type
trait Container { type Item; fn first(&self) -> Option<&Self::Item>; }
```

Object safety rules: no `Self` in method signatures, no generic methods, sized receivers. See `references/generics-traits.md`.

## 7. Error Handling

```rust
use std::fs;
use std::io;
use std::num::ParseIntError;

// ? propagates with From conversion
fn read_count() -> Result<i32, io::Error> {
    let s: String = fs::read_to_string("count.txt")?;
    Ok(s.trim().parse().unwrap_or(0))   // or proper error mapping
}

// Custom error with thiserror
#[derive(thiserror::Error, Debug)]
enum Error {
    #[error("io: {0}")] Io(#[from] io::Error),
    #[error("parse: {0}")] Parse(#[from] ParseIntError),
    #[error("not found: {key}")] NotFound { key: String },
}

// Application-layer catch-all with anyhow
fn main() -> anyhow::Result<()> {
    let x: i32 = "5".parse()?;
    Ok(())
}
```

See `references/error-handling.md` for `?` with `From`, thiserror vs anyhow, and custom error design.

## 8. Attributes

```rust
#[derive(Debug, Clone, PartialEq)]   // generate traits
struct User { id: u32 }

#[cfg(target_os = "linux")]          // conditional compilation
fn setup() { /* */ }

#[inline]                            // hint to inline (rarely matters)
fn fast() {}

#[allow(dead_code)]                  // suppress warning
struct Unused;

#[non_exhaustive]                    // allow adding variants
enum Event { Login }
```

See `references/attributes.md` for the full attribute catalog, `cfg` expressions, and when `#[inline]` actually helps.

## 9. Unsafe

```rust
// Raw pointer dereference
let x = 42;
let ptr: *const i32 = &x;
let val = unsafe { *ptr };

// Splitting a slice (needs unsafe for non-overlapping aliasing)
let mut v = vec![1, 2, 3, 4];
let (left, right) = v.split_at_mut(2);   // safe wrapper

// Calling C ABI
extern "C" { fn abs(input: i32) -> i32; }
let a = unsafe { abs(-5) };

// Union (unsafe to read)
#[repr(C)]
union Value { i: i32, f: f32 }
```

See `references/unsafe.md` for safety contracts, the four unsafe superpowers, and when to reach for it. For deep FFI, route to `rust-unsafe-ffi`.

## 10. Procedural Macros (overview only)

```rust
// Derive (most common)
#[derive(Debug, Clone, serde::Serialize)]
struct Config { /* */ }

// Attribute macro
#[tokio::main]
async fn main() { /* */ }

// Function-like macro
let html = html! { <div>Hello</div> };
```

Authoring these is complex — route to `rust-macros`. This skill only covers using them.

See `references/procedural-macros-overview.md` for the three flavors and when each applies.

## 11. Inline Assembly

```rust
#[cfg(target_arch = "x86_64")]
fn halt() {
    unsafe { std::arch::asm!("hlt", options(nostack)); }
}
```

See `references/inline-asm.md` for `asm!` syntax, clobbers, and when to use it (kernel/embedded only).

---

## Workflow

1. **Identify the question** — "how do I write X" → this skill; "which type" → `rust-stdlib`; "how to architect" → `rust-api-design`.
2. **Find the matching reference** — Sections 1-11 above, or the file in `references/`.
3. **Read the minimal example** — copy the pattern, adapt to your code.
4. **Verify** — `cargo check`, `cargo clippy`.
5. **Hand off** — deeper questions route to specialized skills.

## Decision Shortcuts

| Question | Where |
|---------|-------|
| How do I convert types? | `references/conversions.md` |
| How do I write `if let`/`match`? | `references/flow-control.md` |
| How do closures capture? | `references/closures.md` |
| How do `mod`/`use`/`pub` work? | `references/modules.md` |
| Generic fn/struct/impl? | `references/generics-traits.md` |
| Trait object vs generic? | `references/generics-traits.md` |
| How do I propagate errors? | `references/error-handling.md` |
| What `#[derive]`/`#[cfg]` are there? | `references/attributes.md` |
| When is `unsafe` OK? | `references/unsafe.md` |
| How do I write a procedural macro? | `rust-macros` skill |
| What does `asm!` look like? | `references/inline-asm.md` |

## Coming From Another Language

| Pattern in... | ...becomes in Rust |
|--------------|-------------------|
| Java interface + impl | Rust trait + impl block |
| Java generics `<T extends Foo>` | Rust `<T: Foo>` or `where T: Foo` |
| Java `Optional<T>` | Rust `Option<T>` |
| Java try/catch | Rust `?` + `Result` |
| Python `with` | Rust `Drop` (RAII) |
| Python decorators | Rust attribute macros |
| Go `goroutine` | Rust `thread::spawn` or async task |
| Go `interface{}` | Rust `dyn Trait` or generics |
| C++ RAII destructor | Rust `Drop` trait |
| C++ `reinterpret_cast` | Rust `unsafe { transmute }` (avoid) |

See `references/migrating-from-other-languages.md` for a fuller mapping.

## Resources

- [Type Conversions](references/conversions.md)
- [Flow Control](references/flow-control.md)
- [Closures](references/closures.md)
- [Modules](references/modules.md)
- [Generics and Traits](references/generics-traits.md)
- [Error Handling](references/error-handling.md)
- [Attributes](references/attributes.md)
- [Unsafe](references/unsafe.md)
- [Procedural Macros Overview](references/procedural-macros-overview.md)
- [Inline Assembly](references/inline-asm.md)
- [Migrating From Other Languages](references/migrating-from-other-languages.md)
- `examples/golden-by-example/`: a crate exercising each pattern

## Upstream Sources

- [Rust by Example](https://doc.rust-lang.org/rust-by-example/)
- [The Rust Book](https://doc.rust-lang.org/book/)
- [Rust Reference](https://doc.rust-lang.org/reference/)
- [Rust Standard Library](https://doc.rust-lang.org/std/)
- [The Rustonomicon (unsafe)](https://doc.rust-lang.org/nomicon/)
- [thiserror](https://docs.rs/thiserror/) and [anyhow](https://docs.rs/anyhow/)
