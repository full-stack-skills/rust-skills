---
name: rust-api-design
description: Design Rust library APIs that follow the Rust API Guidelines — naming (C-CASE, C-CONV, C-GETTER), interop traits (C-COMMON-TRAITS, C-CONVERT, C-ITER, C-SERDE), predictability (C-INTUITIVE, C-CONST), flexibility (C-GENERIC, C-NEWTYPE, C-EXT), type safety (C-BOOL, C-NONZERO, C-WRAPPER, C-STR), dependability (C-PANIC, C-UNWRAP), debuggability (C-DEBUG), and future-proofing (C-SEALED, C-STRUCT-FIELD, C-NON-EXHAUSTIVE). Use when users design a public crate API, choose between generics/concrete/newtype, decide trait bounds, hide implementation, avoid breakage, or ask "what is idiomatic Rust API design"; hand semver and publish workflow to rust-semver, lint config to rust-style-clippy, and in-crate layout to rust-module-layout.
---

# Rust API Design (Rust API Guidelines)

> Authority: [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/about.html) — the de-facto standard checklist of ~100 C-* rules used by std, tokio, serde, bevy. See [the full checklist](references/api-guidelines-checklist.md) for canonical wording of every rule.

This skill owns the **shape of a public Rust API**: types, traits, naming, conversions, and the boundaries that keep the API usable, ergonomic, and resistant to breakage. It does **not** own Cargo manifest (`rust-cargo-build`), workspace topology (`rust-workspace`), in-crate `src/` layout (`rust-module-layout`), or semver/publish (`rust-semver`).

## Capability Boundaries

### ✅ Strengths
1. Translating API Guidelines' ~100 C-* rules into concrete design decisions for a public crate
2. Naming types, functions, methods, and features to match std and ecosystem conventions
3. Choosing between generics, trait objects, concrete types, and the newtype pattern
4. Designing `From`/`Into`/`TryFrom`/`AsRef`/`Borrow` conversions (rejecting `Deref` polymorphism)
5. Picking which auto traits (`Debug`, `Clone`, `Eq`, `Hash`, `Send`, `Sync`) to derive
6. Sealing traits, marking `#[non_exhaustive]`, hiding struct fields — to reserve room to evolve
7. Replacing bool parameters with enums, raw integers with newtypes, `String` with `&str`
8. Designing iterators, `Extend`, `Default`, `Display`/`FromStr` correctly
9. Avoiding `panic!`/`unwrap`/`expect` in public APIs in favor of `Result`

### ⚠️ Prerequisites
1. Rust ownership, traits, lifetimes — see `rust-stable`
2. Module visibility and re-exports — see `rust-module-layout`
3. Cargo manifest for `[features]`, `optional = true` — see `rust-cargo-build`

### ❌ Out of Scope
1. Semver rules and publish workflow → `rust-semver`
2. Clippy lint configuration → `rust-style-clippy`
3. Doctests and rustdoc comments → `rust-documentation`
4. Workspace topology → `rust-workspace`

## Data Privacy

This skill does not collect, store, or transmit user data.

---

# The Eight Chapters (One Section Per API Guidelines Chapter)

The Guidelines are organized into 11 chapters. This skill owns 8 — the design chapters. Documentation, Macros, and Necessities live in `rust-documentation`, `rust-macros`, and `rust-cargo-build` respectively.

## 1. Naming (C-CASE, C-CONV, C-GETTER, C-NAMING)

### C-CASE — casing conventions

| Item | Case | Example |
|------|------|---------|
| Types (struct/enum/trait), modules, crates | `UpperCamelCase` | `HttpClient`, `tokio` |
| Functions, methods, locals, fields | `snake_case` | `send_request` |
| Constants, statics | `SCREAMING_SNAKE_CASE` | `MAX_RETRIES` |
| Generic types | single `UpperCamelCase` letter or short word | `T`, `K`, `V`, `Req` |
| Lifetimes | short `'a`/`'b` or descriptive `'src` | `'src` |
| Features | `kebab-case` (Cargo enforces) | `serde-json` |

Avoid ad-hoc abbreviations: `BufferedReader` is std-compliant; `BufRdr` is not.

### C-CONV — conversion method naming

| Conversion | Prefix | Borrows? | Example |
|-----------|--------|----------|---------|
| Cheap, borrowed | `as_` | Yes (`&self → &T`) | `as_slice`, `as_bytes` |
| Cheap, owned | `to_` (no alloc) / `into_` (consumes self) | Varies | `to_vec`, `into_bytes` |
| Expensive, returns new | `to_` | No (`&self → T`) | `to_lowercase` |
| Consuming | `into_` | No (`self → T`) | `into_string`, `into_iter` |
| Fallible | `TryFrom`/`TryInto` | — | `u32::try_from(byte)` |

Requirements: **(1)** A method named `as_X` that returns an owned `X` is wrong — rename to `to_X`. **(2)** The matched inverse for mutable borrows is `as_X_mut` / `X_mut`.

### C-GETTER — accessor naming

```rust
// ✅ C-GETTER compliant
pub struct Buffer { data: Vec<u8> }
impl Buffer {
    pub fn data(&self) -> &[u8] { &self.data }       // no get_ prefix
    pub fn data_mut(&mut self) -> &mut [u8] { &mut self.data }
    pub fn len(&self) -> usize { self.data.len() }   // not get_len
    pub fn is_empty(&self) -> bool { self.data.is_empty() }
}
```

Exceptions where `get_` is allowed: `Cell::get`, `Map::get` (genuine lookup semantics).

## 2. Interoperability (C-COMMON-TRAITS, C-CONVERT, C-ITER, C-SERDE)

### C-COMMON-TRAITS — derive the obvious traits

For every public type, ask: should this derive `Debug`, `Clone`, `PartialEq`, `Eq`, `PartialOrd`, `Ord`, `Hash`, `Default`?

| Trait | Default | Exception |
|-------|---------|-----------|
| `Debug` | Yes | Secrets → manual `Debug` that redacts |
| `Clone` | Yes if cheap | Expensive clone → omit + document |
| `Copy` | Only ≤16 bytes + lossless | — |
| `PartialEq`/`Eq` | Yes if total order | `f64` cannot be `Eq` |
| `Hash` | Yes if `Eq` | Must agree with `Eq` |
| `Default` | Yes if natural empty/zero | — |

### C-CONVERT — `From`/`Into`/`AsRef`/`Borrow`; reject `Deref` polymorphism

```rust
// ✅ Impl From<T> for U; Into comes for free
impl From<ErrorKind> for Error { fn from(k: ErrorKind) -> Self { Error::Kind(k) } }

// ✅ AsRef for borrowed views
impl AsRef<str> for Name { fn as_ref(&self) -> &str { &self.0 } }

// ✅ Borrow<str> if Eq/Hash should agree with str
impl Borrow<str> for Name { fn borrow(&self) -> &str { &self.0 } }
```

**Reject `Deref` as polymorphism**: `Deref` is for smart pointers (`Box`, `Rc`, `Arc`, `String` — std precedent). Using `Deref` to make `MyClient` transparent to `HttpClient` gives hidden method injection, breaks `&self` resolution, and is the **deref polymorphism anti-pattern**. Use `AsRef`, an explicit method, or composition.

### C-ITER — iterator design

```rust
// ✅ Provide IntoIterator for &T, &mut T, T when sensible
impl<'a> IntoIterator for &'a Grid {
    type Item = &'a Cell;
    type IntoIter = std::slice::Iter<'a, Cell>;
    fn into_iter(self) -> Self::IntoIter { self.cells.iter() }
}

impl Grid {
    pub fn iter(&self) -> impl Iterator<Item = &Cell> { /* */ }
    pub fn iter_mut(&mut self) -> impl Iterator<Item = &mut Cell> { /* */ }
}

impl Extend<Cell> for Grid { /* */ }
```

Rules: `iter()` borrows, `iter_mut()` mutably borrows, `into_iter()` consumes. Never return `Vec` from iteration methods — return `impl Iterator`.

### C-SERDE — serialization interop

- Use `#[serde(rename_all = "kebab-case")]` consistently within a type
- `#[non_exhaustive]` enums need `#[serde(other)]` for forward compat with unknown variants
- Re-export serde under a feature (`serde = ["dep:serde"]`) so downstream can opt out

## 3. Predictability (C-INTUITIVE, C-CONST, C-COMMON)

### C-INTUITIVE — naming reflects semantics

If the caller had to read the source to know what `read` does, the API is wrong. Don't surprise: a `read` method that panics on EOF is a defect.

### C-CONST — `const fn` where possible

```rust
pub const fn new(value: u32) -> Self { Self(value) }
const fn is_power_of_two(n: u32) -> bool { n != 0 && n & (n - 1) == 0 }
```

Every std lib API that can be `const fn` is a candidate. Enables `const MAX: UserId = UserId::new(1000);` in callers.

### C-COMMON — sensible defaults via `Default` and builder

```rust
impl Default for Config {
    fn default() -> Self {
        Config { retry_count: 3, timeout: Duration::from_secs(30) }
    }
}

// Builder for complex construction
let client = Client::builder().with_retry(3).with_timeout(Duration::from_secs(10)).build()?;
```

## 4. Flexibility (C-OVERLOAD, C-GENERIC, C-NEWTYPE, C-EXT)

### C-GENERIC — generics on input, concrete on output

```rust
// ✅ Generic over AsRef<str> — caller passes &str, String, Cow
pub fn parse(input: impl AsRef<str>) -> Result<Foo> { /* */ }

// ❌ Concrete &str — forces caller to borrow
pub fn parse(input: &str) -> Result<Foo> { /* */ }
```

Trade-off: more generics → longer compile, harder diagnostics. Generic on input types (`AsRef<str>`, `IntoIterator`); concrete on output.

### C-NEWTYPE — wrap primitives to prevent misuse

```rust
// ✅ Newtypes around raw primitives
pub struct UserId(pub u64);
pub struct Email(String);   // private inner — can't be constructed unsafely

fn delete_user(id: UserId) { /* */ }   // can't accidentally pass a PostId

// ❌ Plain primitives — confusion and argument-order bugs
fn delete_user(id: u64) { /* */ }
```

Zero-cost (compile to the underlying type), prevent argument-order bugs, and allow attaching methods (`UserId::is_anonymous()`).

### C-EXT — extension traits via `Ext` suffix

```rust
pub trait StringExt { fn slugify(&self) -> String; }
impl StringExt for str { fn slugify(&self) -> String { /* */ } }

// Caller opts in:
use my_crate::StringExt;
"Hello World".slugify();
```

Don't put methods directly on `String`/`Vec`/`HttpRequest` from other crates — use an `Ext` trait.

## 5. Type Safety (C-BOOL, C-NONZERO, C-STR, C-SIGNED, C-BITFLAG, C-WRAPPER, C-INTERVAL)

> Authority: [API Guidelines — Type Safety](https://rust-lang.github.io/api-guidelines/type-safety.html). See `references/api-guidelines-checklist.md` for canonical wording.

### C-BOOL — replace bool parameters with enums

```rust
// ✅ Enum — caller intent is explicit at call site
pub enum Trim { Whitespace, None }
pub fn parse(input: &str, trim: Trim) -> Result<Foo> { /* */ }
parse("  x  ", Trim::Whitespace);

// ❌ Bool — caller must remember what true means
pub fn parse(input: &str, trim: bool) -> Result<Foo> { /* */ }
parse("  x  ", true);   // true = ??
```

Two bool params compound: `f(true, false, true)` is incomprehensible. Two-arg enums are the floor. Set `clippy.toml` `max-fn-params-bools = 1` and `max-struct-bools = 1` to enforce mechanically.

### C-NONZERO — `NonZeroUsize` when zero is invalid

```rust
use std::num::NonZeroUsize;

// ✅ NonZeroUsize encodes "≥ 1" in the type
pub fn chunk_size(&self) -> NonZeroUsize { /* */ }
```

Enables niche optimization: `Option<NonZeroU32>` is the same size as `u32`. Use `NonZeroU8`/`NonZeroU16`/`NonZeroU32`/`NonZeroU64`/`NonZeroUsize` and the `NonZeroI*` variants.

### C-STR — `&str` not `&String`; `&[T]` not `&Vec<T>`

```rust
// ✅ Borrow slices for inputs
pub fn process(data: &[u8], name: &str) { /* */ }

// ❌ Forces caller to have owned collections
pub fn process(data: &Vec<u8>, name: &String) { /* */ }
```

### C-SIGNED — prefer unsigned types when values can't be negative

```rust
// ✅ u64 — semantically "count" can't be negative
pub struct Counter { count: u64 }

// ❌ i64 — implies negative values are valid (they aren't)
pub struct Counter { count: i64 }
```

For special ranges (e.g., `Age` 0..=150), use a newtype with validating constructor — let the type system prevent invalid values.

### C-BITFLAG — use the `bitflags!` macro for flag sets

```rust
use bitflags::bitflags;

bitflags! {
    #[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
    pub struct Permissions: u32 {
        const READ = 0b001;
        const WRITE = 0b010;
        const EXECUTE = 0b100;
    }
}

let p = Permissions::READ | Permissions::WRITE;   // type-checked composition
assert!(p.contains(Permissions::READ));            // built-in methods
```

Avoid raw `u32` for flag sets — lose type safety, lose `contains`/`insert`/`remove`/`intersects`.

### C-WRAPPER — newtype to give primitive types meaningful semantics

```rust
pub struct UserId(pub u64);
pub struct AccountId(pub u64);
pub struct OrderId(pub u64);

// Compiler rejects wrong-id bugs:
fn transfer(from: AccountId, to: AccountId, amount: Cents) { /* */ }
// transfer(UserId(1), UserId(2), Cents(100))  ← compile error
```

Zero-cost at runtime (compile to underlying type). Use `#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]` by default.

### C-INTERVAL — encode ranges as types, not loose pairs

```rust
// ✅ Dedicated range type with validating constructor
pub struct ChunkRange { start: u32, end: u32 }   // invariant: end >= start

impl ChunkRange {
    pub fn new(start: u32, end: u32) -> Result<Self, RangeError> {
        if end < start { return Err(RangeError::Inverted); }
        Ok(Self { start, end })
    }
    pub fn contains(&self, x: u32) -> bool { self.start <= x && x <= self.end }
}

// ❌ Loose pair — caller might pass end < start
pub fn process_chunk(start: u32, end: u32) { /* */ }
```

For std ranges, use `RangeInclusive`/`Range`/`RangeTo`. For domain ranges (pagination, time windows), wrap in a newtype.

### C-COMMENT-HIDDEN — `#[doc(hidden)]` does NOT exclude from public API

```rust
// ❌ Hides from rustdoc but is still semver-relevant
#[doc(hidden)]
pub mod unstable { /* */ }   // downstream can still `use crate::unstable::Foo;`

// ✅ For actually-unstable items, gate behind a feature
#[cfg(feature = "unstable")]
pub mod unstable { /* */ }
```

`#[doc(hidden)]` only hides from `cargo doc`. For semver/stability, use feature flags or module privacy.

For owned inputs, accept `String`/`Vec` or `impl Into<String>`/`impl IntoIterator`.

## 6. Dependability (C-PANIC, C-UNWRAP, C-TRANSMUTE)

### C-PANIC — panic only for unreachable invariants

```rust
// ✅ Documented, unreachable from public API
pub fn lookup(&self, id: UserId) -> &User {
    self.table.get(&id).expect("internal: index invariant broken")
}

// ❌ Panics on user input
pub fn divide(a: f64, b: f64) -> f64 {
    if b == 0.0 { panic!("division by zero") }
    a / b
}

// ✅ Return Result for fallible operations
pub fn divide(a: f64, b: f64) -> Result<f64, DivError> { /* */ }
```

Acceptable: programmer violated an invariant, or function documented infallible. Unacceptable: input-driven failure.

### C-UNWRAP — `unwrap`/`expect` forbidden in public paths

```rust
// ❌ Library code
pub fn parse(input: &str) -> Config {
    serde_json::from_str(input).unwrap()   // panics on bad input
}

// ✅ Propagate
pub fn parse(input: &str) -> Result<Config, ParseError> {
    Ok(serde_json::from_str(input)?)
}
```

`unwrap` is OK in tests, `const` contexts (no `?`), and proven-unreachable code. Use `expect("reason")` over bare `unwrap()` for diagnostics.

### C-TRANSMUTE — never `std::mem::transmute` for type punning

`transmute` reinterprets bits, bypassing the type system. Use `From`/`Into`/`TryFrom`, `bytemuck::cast`/`zerocopy` (verified byte-cast), `u64::from_ne_bytes`/`to_ne_bytes`, or `as` for widening. If you reach for `transmute`, route to `rust-unsafe-ffi`.

## 7. Debuggability (C-DEBUG)

Every public type implements `Debug`. Missing `Debug` blocks debugging; over-sharing in `Debug` leaks secrets.

```rust
#[derive(Debug)]
pub struct Client { /* */ }

// ✅ Manual Debug for secrets
impl std::fmt::Debug for Password {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str("Password(***)")
    }
}
```

## 8. Future-Proofing (C-SEALED, C-STRUCT-FIELD, C-NON-EXHAUSTIVE)

### C-SEALED — seal traits to prevent external impls

```rust
mod private { pub trait Sealed {} }

pub trait Serializer: private::Sealed {
    fn serialize(&self, v: &impl Serialize);
}

pub struct JsonSerializer;
impl private::Sealed for JsonSerializer {}
impl Serializer for JsonSerializer { /* */ }
```

Without sealing, anyone can `impl MyTrait for TheirType`, locking you out of adding methods (would be a breaking change). See `references/future-proofing.md`.

### C-STRUCT-FIELD — public struct fields are stable forever

```rust
// ✅ Private fields, public constructor — adding fields is non-breaking
pub struct Config { retry_count: u32, timeout: Duration }
impl Config {
    pub fn new(retry: u32, timeout: Duration) -> Self { Self { retry_count: retry, timeout } }
    pub fn builder() -> ConfigBuilder { /* */ }
}

// ❌ Pub fields + struct literal — adding a field breaks callers
let c = Config { retry_count: 3, timeout: Duration::from_secs(30) };
```

Rule: **pub field** = stable forever. **Private field** = evolvable.

### C-NON-EXHAUSTIVE — mark enums that will grow

```rust
#[non_exhaustive]
pub enum Error { Io(io::Error), Parse(ParseError) }

// Downstream must use a wildcard arm:
match err {
    Error::Io(e) => /* */,
    Error::Parse(e) => /* */,
    _ => /* unknown */,
}
```

Use on error/event/status enums you intend to extend, and on structs with public fields you may add to.

---

## Workflow

1. **Inventory the public surface** — `cargo doc --open` and list every `pub` item. That's the contract.
2. **Apply naming rules** (Section 1) — fix case, conversion prefixes (`as_`/`to_`/`into_`), drop `get_`.
3. **Apply interop rules** (Section 2) — derive `Debug`/`Clone`/etc., add `From`/`AsRef`, design iterators.
4. **Apply predictability + flexibility** (Sections 3-4) — `Default`, `const fn`, newtypes for primitives, `Ext` traits.
5. **Apply type safety** (Section 5) — bool→enum, `NonZero*`, `&str` over `&String`.
6. **Apply dependability** (Section 6) — remove `unwrap`/`panic!` from public paths; return `Result`.
7. **Apply future-proofing** (Section 8) — seal extensible traits, `#[non_exhaustive]` on growing enums, private struct fields.
8. **Hand off** — semver check → `rust-semver`; doctests → `rust-documentation`; lint config → `rust-style-clippy`.

## Decision Shortcuts

| Question | Answer |
|---------|--------|
| `Option` or `Result`? | `Option` for "may not exist"; `Result` for "may fail" |
| Trait or enum? | Trait if open (others add impls); enum if closed (you own variants) |
| Generic or concrete? | Generic on input, concrete on output |
| Field `pub`? | Default no. Only if struct-literal construction is intended |
| `&str` or `impl AsRef<str>`? | `AsRef<str>` for flexibility; `&str` for simplicity |
| Derive `Copy`? | Only if small (≤16 bytes) and bitwise copy is correct |
| Seal this trait? | Yes, unless third parties must add impls (rare) |
| `#[non_exhaustive]`? | Yes for error/event enums; yes for structs with pub fields that may grow |

## Anti-Pattern Catalog

1. **`Deref` polymorphism** — `Deref` to "inherit" methods. Use composition.
2. **`get_X` accessors** — drop `get_`. `fn data(&self) -> &[u8]`.
3. **Bool params** — `fn f(x: bool, y: bool)`. Use two enums.
4. **`unwrap` in public API** — propagates panics. Use `Result`.
5. **`String`/`Vec` in inputs** — forces ownership. Use `&str`/`&[T]`.
6. **Unsealed extension traits** — locks you out of future methods. Seal.
7. **`#[non_exhaustive]` missing on errors** — adding a variant breaks downstream.
8. **Newtype missing** — `fn transfer(amount: u64, from: u64, to: u64)` — argument order is a footgun.
9. **Generated `Debug` leaking secrets** — `#[derive(Debug)] struct ApiKey(String)`. Custom redact.
10. **`transmute` for casts** — use `From`/`as`/`from_ne_bytes`.

See `examples/anti-patterns.md` for before/after refactors of each.

## Resources

- [API Guidelines Checklist](references/api-guidelines-checklist.md) — the full ~100 C-* rules with examples
- [Naming and Conversions Deep Dive](references/naming-and-conversions.md)
- [Future-Proofing Patterns](references/future-proofing.md) — sealed traits, non_exhaustive, builder patterns
- [Anti-Pattern Catalog](examples/anti-patterns.md) — before/after refactors
- `examples/golden-api/` — a small crate that follows every rule, `cargo doc` + clippy passing

## Upstream Sources

- [Rust API Guidelines (About)](https://rust-lang.github.io/api-guidelines/about.html)
- [Rust API Guidelines (Checklist)](https://rust-lang.github.io/api-guidelines/checklist.html)
- [Rust API Guidelines (Naming)](https://rust-lang.github.io/api-guidelines/naming.html)
- [Rust API Guidelines (Type Safety)](https://rust-lang.github.io/api-guidelines/type-safety.html)
- [Rust API Guidelines (Future Proofing)](https://rust-lang.github.io/api-guidelines/future-proofing.html)
- [Effective Rust (D. Drysdale)](https://www.lurklurk.org/effective-rust/) — complementary viewpoint
