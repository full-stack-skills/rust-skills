# API Guidelines Checklist (Full Reference)

The canonical checklist of ~100 C-* rules from the [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/checklist.html). This file is the authoritative reference; `SKILL.md` summarizes the design decisions you make from each rule.

## How to read this file

Each rule has:
- **C-NAME** — the canonical identifier (e.g., C-CASE)
- **Rule** — one sentence summary
- **Example** — `✅` compliant, `❌` violation
- **Decision** — what to do when you encounter a violation

---

## 1. Naming

### C-CASE — Type conversions use consistent casing

| Item | Convention |
|------|-----------|
| Crates, modules, types, traits, enum variants | `UpperCamelCase` |
| Functions, methods, macros, fields, locals | `snake_case` |
| Constants, statics | `SCREAMING_SNAKE_CASE` |
| Type parameters | single `UpperCamelCase` (`T`, `Req`) |

### C-CONV — Conversion methods follow `as_` / `to_` / `into_` conventions

```rust
// ✅
fn as_bytes(&self) -> &[u8]              // cheap, borrowed
fn to_vec(&self) -> Vec<u8>              // expensive copy
fn into_bytes(self) -> Vec<u8>           // consumes self
fn try_into_bytes(self) -> Result<Vec<u8>, Self>  // fallible consuming
```

| Conversion | Prefix | Borrows? |
|-----------|--------|----------|
| Cheap, borrowed view | `as_` | Yes |
| Returns a new value from `&self` | `to_` | No |
| Consumes `self` | `into_` | No |
| Fallible consuming | `try_into_` | No |

Decision: rename any `as_X` returning an owned `X` to `to_X` or `into_X`.

### C-GETTER — `get_` prefix is forbidden on accessors

```rust
// ✅
pub fn data(&self) -> &[u8] { /* */ }
pub fn data_mut(&mut self) -> &mut [u8] { /* */ }

// ❌
pub fn get_data(&self) -> &[u8] { /* */ }
```

Exception: methods with lookup semantics (`HashMap::get`, `Cell::get`).

### C-NAMING — Ad-hoc abbreviations are rejected

```rust
// ❌
pub struct BufRdr;   // abbreviation
pub fn mk_conn() -> Connection;   // abbreviation

// ✅
pub struct BufReader;   // std precedent
pub fn new_connection() -> Connection;
```

---

## 2. Interoperability

### C-COMMON-TRAITS — Types eagerly implement common traits

Default for a public data type:

```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct UserId(pub u64);
```

Optional: `Copy` (small types), `PartialOrd`/`Ord` (sortable), `Default` (has zero).

### C-CONVERT — Conversions provide `From`, `TryFrom`, `AsRef`, `Borrow`

```rust
impl From<io::Error> for MyError { /* */ }
impl TryFrom<&str> for Email { type Error = EmailError; /* */ }
impl AsRef<str> for Email { /* */ }
impl Borrow<str> for Email { /* */ }   // so HashMap<Email, _> works with &str keys
```

Reject `Deref`/`DerefMut` for non-smart-pointer types — this is the deref-polymorphism anti-pattern.

### C-ITER — Collections implement `IntoIterator` for `&T`, `&mut T`, `T`

```rust
struct Grid { cells: Vec<Cell> }

impl Grid {
    pub fn iter(&self) -> impl Iterator<Item = &Cell> { self.cells.iter() }
    pub fn iter_mut(&mut self) -> impl Iterator<Item = &mut Cell> { self.cells.iter_mut() }
}

impl IntoIterator for Grid { /* */ }     // consumes
impl<'a> IntoIterator for &'a Grid { /* */ }
impl<'a> IntoIterator for &'a mut Grid { /* */ }
```

Also: `Extend<T>` for collections that grow.

### C-SERDE — Types implement `Serialize`/`Deserialize` (feature-gated)

```rust
#[cfg_attr(feature = "serde", derive(serde::Serialize, serde::Deserialize))]
#[cfg_attr(feature = "serde", serde(rename_all = "kebab-case"))]
pub struct Config { retry_count: u32 }
```

Rules:
- Wire format naming: `kebab-case` for HTTP/JSON, `snake_case` for YAML/config files
- Forward compat: `#[non_exhaustive]` enums need `#[serde(other)]`
- Optional: gate serde behind a feature so downstream can opt out

### C-COLLECT — Iterator adapters and `FromIterator`/`Extend`

If you write a collection, impl `FromIterator<T>` so `iter.collect::<MyColl>()` works.

---

## 3. Predictability

### C-INTUITIVE — Naming matches semantics

If a method is named `read`, it must do what `std::io::Read::read` does — return bytes read, never panic. A `read` that panics on EOF is wrong.

### C-CONST — `const fn` where possible

```rust
impl UserId {
    pub const fn new(value: u64) -> Self { Self(value) }
}

// Enables:
const ANONYMOUS: UserId = UserId::new(0);
```

### C-COMMON — Common operations work as expected

- `Default::default()` returns a useful empty/zero value, not a sentinel
- `clone()` returns an equivalent value, not a "new handle to the same thing"
- `PartialEq` is reflexive/symmetric/transitive

### C-SMART-PTR — Smart pointers behave like `Box`/`Rc`/`Arc`

If your type is a smart pointer:
- Impl `Deref`/`DerefMut` (legitimate here)
- Impl `AsRef<T>` for explicit access
- Don't impl `Deref` to fake inheritance on non-pointer types

---

## 4. Flexibility

### C-OVERLOAD — Functions accept `impl Trait` for ergonomic overloading

```rust
pub fn send<S: Into<String>>(&self, msg: S) { /* */ }

// Caller flexibility:
client.send("hello");
client.send(String::from("hello"));
client.send(format!("{}-{}", a, b));
```

### C-GENERIC — Generic on input, concrete on output

```rust
// ✅
pub fn parse<S: AsRef<str>>(input: S) -> Result<Foo> { /* */ }
pub fn build(&self) -> Foo { /* */ }   // concrete output

// ❌
pub fn parse(input: &str) -> Result<Foo> { /* */ }   // inflexible input
pub fn build<F: Into<Foo>>(&self) -> F { /* */ }     // over-generic output
```

### C-NEWTYPE — Newtypes around raw primitives

```rust
pub struct UserId(pub u64);
pub struct AccountId(pub u64);

// Compile-time safety:
fn transfer(from: AccountId, to: AccountId, amount: u64) { /* */ }
// Cannot accidentally call transfer(UserId(1), UserId(2), 100)
```

### C-EXT — Extension traits use the `Ext` suffix

```rust
pub trait IterExt: Iterator { fn chunked(self, n: usize) -> Chunks<Self> where Self: Sized; }
impl<T: Iterator> IterExt for T { /* */ }
```

### C-BUILDER — Complex types use a builder

```rust
Client::builder()
    .with_retry(3)
    .with_timeout(Duration::from_secs(10))
    .build()?
```

---

## 5. Type Safety

### C-BOOL — Boolean parameters are replaced with enums

```rust
// ✅
pub enum IncludeHidden { Yes, No }
pub fn list(&self, hidden: IncludeHidden) -> Vec<Entry> { /* */ }

// ❌
pub fn list(&self, hidden: bool) -> Vec<Entry> { /* */ }
```

Two or more bool params: `f(true, false, true)` is incomprehensible.

### C-NONZERO — `NonZero*` types where 0 is invalid

```rust
use std::num::{NonZeroU32, NonZeroUsize};

pub fn chunk_size(&self) -> NonZeroUsize { /* */ }

// Bonus: Option<NonZeroU32> is the same size as u32 (niche optimization)
```

### C-WRAPPER — Newtypes wrap, don't expose raw inner

```rust
pub struct Email(String);   // private inner — construct only via Email::parse

impl Email {
    pub fn parse(s: &str) -> Result<Email, EmailError> { /* */ }
    pub fn as_str(&self) -> &str { &self.0 }
}
```

### C-STR — `&str` over `&String`; `&[T]` over `&Vec<T>`

```rust
// ✅
pub fn process(input: &str, data: &[u8]) { /* */ }

// ❌
pub fn process(input: &String, data: &Vec<u8>) { /* */ }
```

### C-NUMERIC — Use the right numeric type

- Don't use `i64` for values that can't be negative — use `u64`
- Don't use `f64` for money — use a decimal type or integer cents
- Don't use `usize` for non-size quantities — use `u32`/`u64`

### C-BITFLAG — Use `bitflags!` for flag sets, not raw integers

```rust
use bitflags::bitflags;

bitflags! {
    #[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
    pub struct Permissions: u32 {
        const READ    = 0b001;
        const WRITE   = 0b010;
        const EXECUTE = 0b100;
    }
}

let p = Permissions::READ | Permissions::WRITE;
assert!(p.contains(Permissions::READ));   // built-in methods
```

Type-checked composition; rejects accidental mixing with unrelated `u32` values.

### C-INTERVAL — Encode ranges as types, not loose pairs

```rust
// ✅ Dedicated range with invariant enforced in constructor
pub struct ChunkRange { start: u32, end: u32 }   // invariant: end >= start

impl ChunkRange {
    pub fn new(start: u32, end: u32) -> Result<Self, RangeError> {
        if end < start { return Err(RangeError::Inverted); }
        Ok(Self { start, end })
    }
    pub fn contains(&self, x: u32) -> bool { (self.start..=self.end).contains(&x) }
}

// ❌ Loose pair — caller can pass end < start
pub fn process_chunk(start: u32, end: u32) { /* */ }
```

For std ranges use `RangeInclusive`/`Range`. For domain ranges wrap in a newtype.

### C-COMMENT-HIDDEN — `#[doc(hidden)]` does NOT exclude from public API

```rust
// ❌ Hides from rustdoc but is still semver-relevant public API
#[doc(hidden)]
pub mod unstable { /* */ }
// Downstream can still write `use crate::unstable::Foo;`

// ✅ For actually-unstable items, gate behind a feature
#[cfg(feature = "unstable")]
pub mod unstable { /* */ }
```

`#[doc(hidden)]` only hides from `cargo doc`. For semver/stability use feature flags or module privacy.

---

## 6. Dependability

### C-PANIC — No panics in public APIs for input-driven failures

```rust
// ✅ Result for fallible operations
pub fn lookup(&self, key: &str) -> Result<Value, LookupError> { /* */ }

// ✅ panic only for invariant violations
pub fn lookup_cached(&self, key: &str) -> &Value {
    self.cache.get(key).expect("cache populated by lookup()")
}

// ❌
pub fn divide(a: f64, b: f64) -> f64 {
    if b == 0.0 { panic!("zero") }
    a / b
}
```

### C-UNWRAP — No `unwrap`/`expect` in public paths

```rust
// ❌
pub fn parse(input: &str) -> Config {
    serde_json::from_str(input).unwrap()
}

// ✅
pub fn parse(input: &str) -> Result<Config, ParseError> {
    Ok(serde_json::from_str(input)?)
}
```

`unwrap` is OK in: tests, `const` contexts (no `?`), proven-unreachable code with `unreachable!()`.

### C-TRANSMUTE — No `std::mem::transmute` for type punning

Use safe alternatives:

| Need | Use |
|------|-----|
| Numeric conversion | `From`/`TryFrom`/`as` |
| Bytes ↔ numbers | `from_ne_bytes`/`to_ne_bytes` |
| Byte-level cast | `bytemuck::cast`/`zerocopy` |
| Type erasure | `Box<dyn Trait>` |
| Reinterpretation | Reconsider — likely unsound |

### C-DEBUG-EXPECT — `expect()` carries context, not just `unwrap()`

```rust
// ✅
let value = map.get(key).expect("key inserted on line 42");

// ❌
let value = map.get(key).unwrap();
```

---

## 7. Debuggability

### C-DEBUG — All public types impl `Debug`

```rust
#[derive(Debug)]
pub struct Config { /* */ }

// Secrets get manual Debug
impl fmt::Debug for ApiKey {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("ApiKey").field("value", &"***").finish()
    }
}
```

### C-DEBUG-FMT — `Debug` output is unambiguous

`Debug` should round-trip: `format!("{:?}", x)` should be parseable enough to reconstruct conceptually. For complex types, prefer `f.debug_struct("Name").field("a", &self.a).finish()`.

---

## 8. Future-Proofing

### C-SEALED — Traits that may grow are sealed

```rust
mod private { pub trait Sealed {} }

pub trait Serializer: private::Sealed {
    fn serialize(&self, v: &dyn std::any::Any);
}

// Public impls; downstream cannot add their own
pub struct JsonSerializer;
impl private::Sealed for JsonSerializer {}
impl Serializer for JsonSerializer { /* */ }
```

### C-STRUCT-FIELD — Public struct fields are stable forever

```rust
// ✅ Private fields, public constructor
pub struct Config {
    retry_count: u32,
    timeout: Duration,
}

impl Config {
    pub fn builder() -> ConfigBuilder { /* */ }
}

// ❌ Public fields — adding one is a breaking change
pub struct Config {
    pub retry_count: u32,
    pub timeout: Duration,
}
```

If callers do `Config { retry_count: 3, timeout: ... }`, you can never add a field without breaking them.

### C-NON-EXHAUSTIVE — Enums that may grow are marked

```rust
#[non_exhaustive]
pub enum Event { Login, Logout, Message(String) }

// Forces downstream to use a wildcard arm:
match event {
    Event::Login => /* */,
    Event::Logout => /* */,
    Event::Message(s) => /* */,
    _ => /* future variants */,
}
```

Also for structs:

```rust
#[non_exhaustive]
pub struct Options {
    pub verbose: bool,
}

// Downstream cannot do Options { verbose: true } struct-literal;
// must use Options::new() or builder.
```

### C-PRIVATE-FIELD — Fields are private by default; expose via accessor

```rust
pub struct Counter { count: u64 }   // private

impl Counter {
    pub fn value(&self) -> u64 { self.count }
}
```

This reserves the right to change the internal representation (e.g., switch to `AtomicU64`) without breaking callers.

---

## 9. Documentation (covered in `rust-documentation`)

For C-DOC, C-DOC-COMMENT, C-META, C-EXAMPLE, C-LINK — see `rust-documentation`.

## 10. Macros (covered in `rust-macros`)

For C-MACRO, C-MACRO-NAMES — see `rust-macros`.

## 11. Necessities (covered in `rust-cargo-build`)

For C-CRATE-DOC, C-METADATA, C-RELNOTES — see `rust-cargo-build` and `rust-semver`.

---

## Verification Commands

After applying the checklist, verify mechanically:

```bash
# All public types have Debug
cargo +nightly doc --document-private-items 2>&1 | grep -i missing

# Clippy with pedantic + API guidelines lints
cargo clippy --workspace --all-targets --all-features -- \
    -W clippy::pedantic \
    -W clippy::nursery \
    -A clippy::module_name_repetitions

# cargo-semver-checks (see rust-semver skill)
cargo semver-checks check-release

# Public API surface audit
cargo public-api  # optional tool
```

## Source

- [Rust API Guidelines Checklist](https://rust-lang.github.io/api-guidelines/checklist.html)
- Each chapter: [naming](https://rust-lang.github.io/api-guidelines/naming.html), [interoperability](https://rust-lang.github.io/api-guidelines/interoperability.html), [predictability](https://rust-lang.github.io/api-guidelines/predictability.html), [flexibility](https://rust-lang.github.io/api-guidelines/flexibility.html), [type-safety](https://rust-lang.github.io/api-guidelines/type-safety.html), [dependability](https://rust-lang.github.io/api-guidelines/dependability.html), [debuggability](https://rust-lang.github.io/api-guidelines/debuggability.html), [future-proofing](https://rust-lang.github.io/api-guidelines/future-proofing.html)
