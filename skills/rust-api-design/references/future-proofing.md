# Future-Proofing Patterns

Companion to `SKILL.md` §8. Covers sealed traits, `#[non_exhaustive]`, builder patterns, and the semver implications of each.

> For the *mechanical* side of semver (version bumping, `cargo-semver-checks`, yank), see `rust-semver`.

## 1. Sealed Traits

### The Pattern

```rust
// 1. Define Sealed in a private module
mod private {
    pub trait Sealed {}
}

// 2. Supertrait your public trait with Sealed
pub trait Encoder: private::Sealed {
    fn encode(&self, buf: &mut Vec<u8>);
}

// 3. Impl Sealed only for the types you want
pub struct JsonEncoder;
pub struct YamlEncoder;

impl private::Sealed for JsonEncoder {}
impl private::Sealed for YamlEncoder {}

impl Encoder for JsonEncoder { fn encode(&self, buf: &mut Vec<u8>) { /* */ } }
impl Encoder for YamlEncoder { fn encode(&self, buf: &mut Vec<u8>) { /* */ } }
```

Downstream can use `Encoder` (call methods, take `impl Encoder`), but cannot impl it for their own types — they'd need to impl `private::Sealed`, which they can't reach.

### Why seal?

Without sealing, anyone can `impl MyTrait for TheirType`. Once they do, **adding any method to `MyTrait` is a breaking change** — it breaks their impl. Sealing preserves your ability to extend the trait.

### When NOT to seal

- `std::iter::Iterator` — intentionally open, downstream crates impl it for their own iterators
- `serde::Serialize`/`Deserialize` — open, downstream impls them for every type
- Any trait whose primary use is for users to implement

### Variants

**Marker-style seal** (most common):

```rust
mod private { pub trait Sealed {} }
pub trait My: private::Sealed { /* */ }
```

**Lifetime seal** (advanced):

```rust
pub trait My: SealedLifetime<'static> { /* */ }
pub trait SealedLifetime<'a> {}
```

Prefer the simple form.

## 2. `#[non_exhaustive]`

### On enums

```rust
#[non_exhaustive]
pub enum Error {
    Io(io::Error),
    Parse(ParseError),
    Network(NetworkError),
}
```

Effect: downstream `match` on `Error` must have a `_` wildcard arm. You can add `Error::Timeout` later without breaking them.

Caveat: `#[non_exhaustive]` is **ignored within the defining crate**. Your own `match` doesn't need the wildcard.

### On structs

```rust
#[non_exhaustive]
pub struct Config {
    pub retry_count: u32,
    pub timeout: Duration,
}
```

Effect: downstream cannot use struct-literal syntax `Config { retry_count: 3, timeout: ... }`. They must use `Config::new()` or a builder. You can add fields later.

### When to use

| Type | Use `#[non_exhaustive]`? |
|------|--------------------------|
| Error enums | Yes — almost always grow |
| Event types | Yes — new events arrive over time |
| Status enums | Yes — new statuses added |
| Public struct with pub fields | Yes — fields will grow |
| Public struct with private fields | No — already evolvable |
| Closed enum (rare) | No — e.g., `Option`, `Result` |

### Migration: adding `#[non_exhaustive]` is itself breaking

Existing downstream `match` without wildcard will fail to compile. Announce in CHANGELOG as a breaking change.

## 3. Builder Pattern

For types with many configuration options:

```rust
pub struct Client {
    url: String,
    timeout: Duration,
    retries: u32,
    headers: Vec<(String, String)>,
}

pub struct ClientBuilder {
    url: Option<String>,
    timeout: Option<Duration>,
    retries: Option<u32>,
    headers: Vec<(String, String)>,
}

impl Client {
    pub fn builder() -> ClientBuilder {
        ClientBuilder {
            url: None,
            timeout: Some(Duration::from_secs(30)),   // default
            retries: Some(3),
            headers: Vec::new(),
        }
    }
}

impl ClientBuilder {
    pub fn url(mut self, url: impl Into<String>) -> Self {
        self.url = Some(url.into());
        self
    }
    pub fn timeout(mut self, t: Duration) -> Self {
        self.timeout = Some(t);
        self
    }
    pub fn build(self) -> Result<Client, ClientError> {
        Ok(Client {
            url: self.url.ok_or(ClientError::MissingUrl)?,
            timeout: self.timeout.unwrap(),
            retries: self.retries.unwrap(),
            headers: self.headers,
        })
    }
}

// Usage:
let client = Client::builder()
    .url("https://api.example.com")
    .timeout(Duration::from_secs(10))
    .build()?;
```

### Why builders

- Adding a `with_X` method is **non-breaking** (just an additional method)
- Adding a `pub field` to a struct-literal config is **breaking**
- Forces explicit construction (no half-built states)
- Validates invariants in `build()`

### Builder libraries

- [`derive_builder`](https://docs.rs/derive_builder) — derive macro
- [`typed-builder`](https://docs.rs/typed_builder) — type-state (required fields enforced at compile time)
- Hand-rolled — most flexible, most code

For public APIs, hand-rolled is often preferred — full control, no extra deps.

## 4. Private Fields + Accessor Pattern

```rust
pub struct Counter { count: u64 }   // private field

impl Counter {
    pub fn new() -> Self { Self { count: 0 } }
    pub fn get(&self) -> u64 { self.count }
    pub fn increment(&mut self) { self.count += 1; }
}
```

Today the field is `u64`. Tomorrow it could be `AtomicU64`, `Cell<u64>`, or computed from a more complex structure. Callers only see `get()` and `increment()`, so they don't care.

### When pub field is OK

```rust
pub struct Point { pub x: f64, pub y: f64 }
```

`Point` is a pure data type — the fields ARE the type. No invariant to enforce.

Rule: if removing the field makes sense, keep it private. If the field is essential identity, pub is fine.

## 5. Visibility Tricks

### `pub(crate)` for internal sharing

```rust
pub struct Api {
    inner: ApiInner,
}

struct ApiInner { /* */ }   // private to crate — never exposed

impl Api {
    pub(crate) fn internal_method(&self) { /* */ }
}
```

`pub(crate)` lets you share across modules in your crate without leaking to downstream.

### `pub(in path)` for scoped visibility

```rust
mod network {
    pub struct Client { /* */ }

    impl Client {
        pub(in crate::network) fn send(&self) { /* */ }   // only network module
    }
}
```

### Re-export at crate root for the public API

```rust
// src/lib.rs
mod client;
mod config;

pub use client::Client;
pub use config::Config;

// Downstream does `use my_crate::Client;`, not `use my_crate::client::Client;`
```

This is the **facade pattern** — internal modules are private, crate root re-exports only the stable API. See `rust-module-layout` skill.

## 6. The Five Pillars of Evolvability

To make a Rust crate's public API evolvable without major-version bumps:

1. **Sealed traits** — you can always add methods
2. **`#[non_exhaustive]` on enums and pub-field structs** — you can always add variants/fields
3. **Private fields + accessors** — you can always change representation
4. **Builders instead of multi-arg constructors** — you can always add `with_X`
5. **Feature-gated extensions** — `#[cfg(feature = "X")]` lets you ship optional API without breaking core users

All five are non-breaking by construction. Use them by default on any crate that may evolve.

## Source

- [Rust API Guidelines — Future Proofing](https://rust-lang.github.io/api-guidelines/future-proofing.html)
- [Sealed traits pattern](https://rust-lang.github.io/api-guidelines/future-proofing.html#c-sealed)
- [`#[non_exhaustive]` RFC 2008](https://rust-lang.github.io/rfcs/2008-non-exhaustive.html)
- [Typestate builder pattern (typed-builder)](https://docs.rs/typed-builder)
