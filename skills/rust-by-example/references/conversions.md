# Type Conversions

> Concrete code patterns for `From`/`Into`, `TryFrom`/`TryInto`, `as`, `Deref`, `FromStr`, `Default`, and `transmute`. For std API selection rules (`AsRef` vs `Into` vs `to_*`), see `rust-stable`.

## 1. `From` / `Into` — lossless, infallible

Implement `From` once; `Into` comes for free via a blanket impl.

```rust
struct Celsius(f64);

impl From<f64> for Celsius {
    fn from(v: f64) -> Self { Self(v) }
}

fn main() {
    let c1: Celsius = Celsius::from(36.6);
    let c2: Celsius = 36.6.into();      // Into comes for free
    assert_eq!(c1.0, c2.0);
}
```

**When to use:** newtype construction, semantic-preserving casts (e.g. `i32` → `i64`), wrapping for domain types.

## 2. `TryFrom` / `TryInto` — fallible

When conversion can fail, return a `Result`.

```rust
struct Age(u8);

#[derive(Debug)]
struct AgeError;

impl std::convert::TryFrom<i32> for Age {
    type Error = AgeError;
    fn try_from(value: i32) -> Result<Self, Self::Error> {
        if !(0..=150).contains(&value) {
            return Err(AgeError);
        }
        Ok(Age(value as u8))
    }
}

fn main() {
    let ok: Result<Age, _> = Age::try_from(42);
    let bad: Result<Age, _> = 200.try_into();
    assert!(ok.is_ok() && bad.is_err());
}
```

## 3. `as` keyword — numeric casts (can lose data)

```rust
fn main() {
    let big: i64 = 1_000_000_000_000;
    let small: i32 = big as i32;            // silent truncation!
    assert_eq!(small, -727379968);

    let f = 3.7_f64;
    let n = f as i32;                       // truncates toward zero
    assert_eq!(n, 3);
}
```

`as` works for: numeric types, `bool` → integer, `char` → integer (`u8` errors if non-ASCII), enum with `repr`, raw pointers. It does NOT work for `String` → `&str` (use `Deref`) or between structs (use `From`).

**Warning:** `as` on `i64 → i32` and `f64 → i32` silently truncates. Prefer `TryFrom` for business logic; reserve `as` for known-safe widening or bit-level FFI.

## 4. `Deref` coercion — smart pointers, NOT polymorphism

`Deref` lets `&T` auto-coerce to `&T::Target`. This is a convenience for ergonomic APIs (`&String` → `&str`), not for runtime polymorphism.

```rust
use std::ops::Deref;

struct Buffer(Vec<u8>);

impl Deref for Buffer {
    type Target = [u8];
    fn deref(&self) -> &Self::Target { &self.0 }
}

fn main() {
    let b = Buffer(vec![1, 2, 3]);
    let slice: &[u8] = &b;                  // Deref coercion
    assert_eq!(slice.len(), 3);
}
```

Do NOT use `Deref` to fake inheritance between unrelated types — it confuses readers and breaks `auto`-deref in method resolution.

## 5. `FromStr` — string → type

```rust
use std::str::FromStr;

struct Port(u16);

#[derive(Debug)]
struct ParsePortError;

impl FromStr for Port {
    type Err = ParsePortError;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        s.parse::<u16>().map(Port).map_err(|_| ParsePortError)
    }
}

fn main() {
    let p: Result<Port, _> = "8080".parse();
    assert!(p.is_ok());
}
```

## 6. `impl Default` — for constructors

```rust
struct Config {
    retries: u32,
    timeout_ms: u64,
}

impl Default for Config {
    fn default() -> Self {
        Self { retries: 3, timeout_ms: 5_000 }
    }
}

fn main() {
    let c = Config { retries: 5, ..Default::default() };
    assert_eq!(c.timeout_ms, 5_000);
}
```

Or just `#[derive(Default)]` if every field is `Default`.

## 7. `transmute` — unsafe, avoid

Reinterprets bits. Almost always a footgun — prefer `bytemuck` / `zerocopy` for safe casts.

```rust
fn main() {
    let bytes: [u8; 4] = [0x78, 0x56, 0x34, 0x12];
    // BAD: reinterpret bytes as i32 (endian-unsafe, alignment-sensitive).
    let n = unsafe { std::mem::transmute::<[u8; 4], i32>(bytes) };
    println!("{n}");
}
```

Prefer `i32::from_le_bytes(bytes)` — same result, no unsafe.

## Decision matrix

| Need | Use |
|------|-----|
| Lossless wrap / newtype | `From` / `Into` |
| Can fail (e.g. out of range) | `TryFrom` / `TryInto` |
| Numeric widening (known safe) | `From` or `TryFrom` |
| Numeric narrowing | `TryFrom` (never silent `as`) |
| `&String` → `&str`, smart pointers | `Deref` coercion |
| String parse | `FromStr` / `str::parse` |
| Sensible defaults | `Default` |
| Bit reinterpret | `from_le_bytes` / `bytemuck` (not `transmute`) |

## Reference

- [Rust by Example — Casting](https://doc.rust-lang.org/rust-by-example/types/cast.html)
- [Rust by Example — From & Into](https://doc.rust-lang.org/rust-by-example/conversion/from_into.html)
- [std::convert](https://doc.rust-lang.org/std/convert/)
- [std::str::FromStr](https://doc.rust-lang.org/std/str/trait.FromStr.html)
