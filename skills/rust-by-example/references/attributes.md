# Attributes

> Concrete catalog of common built-in attributes: `#[derive]`, `#[cfg]`, `#[cfg_attr]`, `#[inline]`, `#[allow]`/`#[deny]`/`#[warn]`, `#[non_exhaustive]`, `#[must_use]`, `#[deprecated]`, `#[doc]`. For lints and clippy rules, see `rust-style-clippy`.

## 1. `#[derive(...)]` — auto-generate trait impls

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Default)]
pub struct UserId(pub u64);

#[derive(Debug, Clone, PartialEq)]
pub struct User {
    pub id: UserId,
    pub name: String,
}

fn main() {
    let a = UserId(1);
    let b = a;                                  // Copy
    assert_eq!(a, b);
    let u = User::default();                    // UserId(0), name = ""
    println!("{:?}", u);
}
```

Common derives: `Debug`, `Clone`, `Copy` (only if all fields are `Copy`), `PartialEq`/`Eq`, `PartialOrd`/`Ord`, `Hash`, `Default`. External crates add more: `serde::Serialize`/`Deserialize`, `thiserror::Error`, `clap::Parser`.

## 2. `#[cfg(...)]` — conditional compilation

```rust
#[cfg(target_os = "linux")]
fn syscall_setup() { /* linux-specific */ }

#[cfg(feature = "tls")]
fn tls_enabled() -> bool { true }

#[cfg(debug_assertions)]
fn trace(msg: &str) { eprintln!("[trace] {msg}"); }

#[cfg(all(target_arch = "wasm32", feature = "web"))]
fn wasm_web_path() {}
```

Predicates: `target_os`, `target_arch`, `feature`, `debug_assertions`, `test`, plus combinators `all(...)`, `any(...)`, `not(...)`.

## 3. `#[cfg_attr(...)]` — conditional attribute

```rust
// Applies `#[inline(always)]` only on release builds.
#[cfg_attr(not(debug_assertions), inline(always))]
fn hot_loop(x: u64) -> u64 { x.wrapping_mul(0x9E3779B97F4A7C15) }
```

Equivalent to `#[cfg(...)]` plus the inner attribute — keeps a single declaration rather than mirroring the item twice.

## 4. `#[inline]`, `#[inline(always)]`, `#[inline(never)]`

```rust
#[inline]            // hint: inline across crate boundaries
pub fn small(x: i32) -> i32 { x + 1 }

#[inline(always)]    // force: rarely worth it
pub fn trivial(x: i32) -> i32 { x }

#[inline(never)]     // force not inlined (useful for cold error paths)
pub fn report() { eprintln!("cold path"); }
```

`#[inline]` mostly matters for cross-crate inlining of generic-free functions. `always`/`never` should be rare; benchmark before adding. The compiler already inlines within a crate.

## 5. `#[allow(...)]`, `#[deny(...)]`, `#[warn(...)]` — lint control

```rust
#[allow(dead_code)]
struct UnusedPlaceholder;

#[deny(unsafe_code)]                    // forbid unsafe in this item
mod safe_only { pub fn f() {} }

#[warn(clippy::pedantic)]               // requires clippy attribute
mod strict { pub fn g() {} }

fn main() {
    let _x = 5;                          // `_` prefix silences unused warning
}
```

`deny` makes a warning into an error; `allow` suppresses it; `warn` is the default. `#![forbid(...)]` at crate level cannot be relaxed.

## 6. `#[non_exhaustive]` — future-proof enum/struct

```rust
#[non_exhaustive]
pub enum Event { Login, Logout }

#[non_exhaustive]
pub struct Config { pub retries: u32 }

fn handle(e: Event) {
    match e {
        Event::Login => {}
        Event::Logout => {}
        _ => {}                          // required even if currently exhaustive
    }
}

fn main() {
    // External crates cannot do `Config { retries: 3 }`; must use `..Default::default()`.
}
```

Allows adding variants/fields later without a breaking change for downstream matchers and constructors.

## 7. `#[must_use]` — flag ignored return values

```rust
#[must_use = "the new String is the transformed value"]
pub fn upper(s: &str) -> String { s.to_uppercase() }

#[must_use]
pub fn is_valid(&self) -> bool { true }

fn main() {
    let s = String::from("hi");
    upper(&s);                            // warning: unused must_use
    let _ = upper(&s);                    // ok
}
```

`Result`, `Option`, and `Iterator` are already `#[must_use]`.

## 8. `#[deprecated]` — mark for removal

```rust
#[deprecated(since = "1.2.0", note = "use `new_name` instead")]
pub fn old_api() -> u32 { 42 }

pub fn new_name() -> u32 { 42 }

fn main() {
    let _ = old_api();                    // warning: deprecated
}
```

## 9. `#[doc = "..."]` and `///`

```rust
/// Short summary shown in search.
///
/// Longer description. Supports Markdown.
///
/// # Examples
///
/// ```
/// let x = 5;
/// assert_eq!(x, 5);
/// ```
pub fn documented() {}

// The `///` sugar is equivalent to:
#[doc = "Short summary shown in search."]
pub fn sugar_equivalent() {}
```

Doc comments become attributes under the hood. `//!` (inner doc) documents the enclosing module or crate.

## Attribute cheat sheet

| Attribute | Effect |
|-----------|--------|
| `#[derive(…)]` | Auto-generate trait impls |
| `#[cfg(…)]` | Compile this item only if predicate holds |
| `#[cfg_attr(c, attr)]` | Apply `attr` if `c` holds |
| `#[inline]` | Cross-crate inline hint |
| `#[allow(deny warn)]` | Lint control |
| `#[non_exhaustive]` | Future-proof enums/structs |
| `#[must_use]` | Warn if return ignored |
| `#[deprecated]` | Warn at call sites |
| `#[doc = "…"]` | Rustdoc text |
| `#[repr(C)]` | C-compatible layout (see `unsafe.md`) |

## Common pitfalls

| Symptom | Fix |
|--------|-----|
| `Copy` not derivable | Some field is not `Copy` (e.g. `String`, `Vec`) — drop `Copy`, keep `Clone` |
| `#[cfg(feature = "x")]` ignored | Add `x` to `[features]` in `Cargo.toml` |
| `#[inline(always)]` makes code slower | Remove it; trust the optimizer |
| `non_exhaustive` cannot be constructed externally | Use `Default` / a constructor method |

## Reference

- [Rust by Example — Attributes](https://doc.rust-lang.org/rust-by-example/attribute.html)
- [Rust by Example — derive](https://doc.rust-lang.org/rust-by-example/trait/derive.html)
- [Rust by Example — cfg](https://doc.rust-lang.org/rust-by-example/attribute/cfg.html)
- [The Rust Reference — Attributes](https://doc.rust-lang.org/reference/attributes.html)
- [The rustc book — Conditional compilation](https://doc.rust-lang.org/rustc/reference/conditional-compilation.html)
