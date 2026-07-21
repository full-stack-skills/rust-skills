# Error Handling

> Concrete patterns for `Result`/`Option`, `?`, `unwrap`/`expect`, custom error enums, `thiserror`, `anyhow`, `map_err`/`and_then`, and fallible `collect`. For std combinator catalog, see `rust-stdlib`.

## 1. `Result<T, E>` and `Option<T>`

```rust
fn lookup(xs: &[i32], idx: usize) -> Option<i32> {
    xs.get(idx).copied()
}

fn parse_port(s: &str) -> Result<u16, std::num::ParseIntError> {
    s.parse::<u16>()
}

fn main() {
    assert_eq!(lookup(&[10, 20], 1), Some(20));
    assert!(parse_port("70000").is_err());
}
```

`Option` is for "value or nothing"; `Result` is for "value or error". Never encode errors as `None` if the failure reason matters.

## 2. The `?` operator (with `From` conversion)

```rust
use std::fs;
use std::io;
use std::num::ParseIntError;

fn read_count(path: &str) -> Result<i32, AppError> {
    let s: String = fs::read_to_string(path)?;        // io::Error -> AppError
    let n: i32 = s.trim().parse()?;                   // ParseIntError -> AppError
    Ok(n)
}

#[derive(Debug)]
enum AppError {
    Io(io::Error),
    Parse(ParseIntError),
}
impl From<io::Error> for AppError { fn from(e: io::Error) -> Self { Self::Io(e) } }
impl From<ParseIntError> for AppError { fn from(e: ParseIntError) -> Self { Self::Parse(e) } }
```

`?` unwraps `Ok`, returns early on `Err`, and converts the error via `From`. Same operator works on `Option` (returns `None`).

## 3. `unwrap` / `expect` — when acceptable

```rust
fn main() {
    // Acceptable: literal or constant that obviously succeeds.
    let n: i32 = "42".parse().expect("hardcoded literal parses");

    // Acceptable: test code, where panicking is the failure mode.
    #[cfg(test)]
    fn t() { let v: Vec<i32> = vec![1,2,3]; assert_eq!(v.first().unwrap(), &1); }

    // NOT acceptable in libraries: panics on user input.
    // fn bad(s: &str) -> i32 { s.parse().unwrap() }    // don't
}
```

`expect("msg")` is preferred over bare `unwrap()` — the message documents the invariant. In production code, return `Result`.

## 4. Custom error enums

```rust
use std::fmt;

#[derive(Debug)]
pub enum ParseError {
    Empty,
    Invalid(String),
}

impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Empty => write!(f, "empty input"),
            Self::Invalid(s) => write!(f, "invalid: {s}"),
        }
    }
}

impl std::error::Error for ParseError {}

fn parse_nonempty(s: &str) -> Result<String, ParseError> {
    let t = s.trim();
    if t.is_empty() { return Err(ParseError::Empty); }
    if !t.chars().all(|c| c.is_ascii_alphabetic()) {
        return Err(ParseError::Invalid(t.to_string()));
    }
    Ok(t.to_string())
}
```

Every error type should implement `Debug` (for logs), `Display` (for users), and `std::error::Error`.

## 5. `thiserror::Error` derive

```rust
// Cargo.toml: thiserror = "1"
use thiserror::Error;

#[derive(Debug, Error)]
pub enum AppError {
    #[error("io: {0}")]     Io(#[from] std::io::Error),
    #[error("parse: {0}")]  Parse(#[from] std::num::ParseIntError),
    #[error("not found: {key}")] NotFound { key: String },
    #[error("invalid state")] Invalid,
}

fn run() -> Result<(), AppError> {
    let _n: i32 = std::fs::read_to_string("x")?.trim().parse()?;
    Ok(())
}
```

`#[from]` generates both `From` and the `Error` message; `#[error("...")]` provides `Display`. Use thiserror for **library** error types.

## 6. `anyhow::Result` for application layer

```rust
// Cargo.toml: anyhow = "1"
use anyhow::{Result, Context};

fn main() -> Result<()> {
    let text = std::fs::read_to_string("config.toml")
        .context("failed to read config.toml")?;
    let n: i32 = text.trim().parse()?;
    println!("n = {n}");
    Ok(())
}
```

`anyhow::Error` is a boxed, opaque error with a backtrace and `.context(...)`. Use it in **binaries** and integration glue where you only need to surface "what failed" — not in library public APIs.

## 7. `map_err` and `and_then`

```rust
fn main() {
    let r: Result<i32, String> = "x".parse::<i32>()
        .map_err(|e: std::num::ParseIntError| e.to_string());

    let chain: Result<i32, &'static str> = "5".parse::<i32>()
        .and_then(|n| if n > 0 { Ok(n * 2) } else { Err("non-positive") });

    assert!(r.is_err());
    assert_eq!(chain, Ok(10));
}
```

`map_err` converts the error; `and_then` chains fallible steps without nested `match`.

## 8. Collecting errors

`Iterator<Item = Result<T, E>>` collects into `Result<Vec<T>, E>`, short-circuiting on the first error.

```rust
fn parse_all(args: &[&str]) -> Result<Vec<i32>, std::num::ParseIntError> {
    args.iter().map(|s| s.parse::<i32>()).collect()
}

fn main() {
    assert_eq!(parse_all(&["1", "2", "3"]), Ok(vec![1, 2, 3]));
    assert!(parse_all(&["1", "x", "3"]).is_err());
}
```

## thiserror vs anyhow

| | thiserror | anyhow |
|--|-----------|--------|
| Use in | Library public API | Application code, glue |
| Error type | Concrete enum | Opaque boxed |
| Pattern matching on error | Yes (callers can `match`) | Awkward (use `downcast_ref`) |
| Adds `context()` | No | Yes |
| Compile time | Small | Larger |

## Common pitfalls

| Symptom | Fix |
|--------|-----|
| `?` won't convert errors | Add `From<E1> for E2` or use `thiserror` `#[from]` |
| `Box<dyn Error>` everywhere | Switch to `anyhow::Result` or a concrete enum |
| `unwrap` panic in prod | Return `Result` or use `?` |
| Cannot inspect error variant | Don't use `anyhow` for public library APIs |

## Reference

- [Rust by Example — Error handling](https://doc.rust-lang.org/rust-by-example/error.html)
- [Rust by Example — ? operator](https://doc.rust-lang.org/rust-by-example/error/option_unwrap/question_mark.html)
- [thiserror docs](https://docs.rs/thiserror/)
- [anyhow docs](https://docs.rs/anyhow/)
- [std::error::Error](https://doc.rust-lang.org/std/error/trait.Error.html)
- [The Rust Book — Recovering from Errors](https://doc.rust-lang.org/book/ch09-02-recovering-from-errors-with-result.html)
