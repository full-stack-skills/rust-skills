# Error Handling Patterns

> Based on `library/core/src/result.rs` and `library/core/src/ops/try_trait.rs` (official rust-lang/rust).

## Result Combinators

```rust
// Mapping
result.map(|val| transform(val));
result.map_err(|err| wrap(err));
result.and_then(|val| maybe_ok(val));          // flat_map for Result
result.or_else(|err| maybe_alternative(err));  // recover from error

// Unwrapping
result.unwrap();                    // panics on Err
result.expect("msg");               // panics with message
result.unwrap_or(default);          // Err → default
result.unwrap_or_else(fn);          // Err → fn(err)
result.unwrap_or_default();         // Err → Default::default()

// Converting
result.ok();                        // Result → Option (discards error)
result.err();                       // Result → Option (discards ok value)
result.transpose();                 // Result<Option<T>, E> → Option<Result<T, E>>
result.flatten();                   // Result<Result<T, E>, E> → Result<T, E>

// Conditional
result.is_ok();
result.is_err();
result.is_ok_and(|v| condition(v));
result.is_err_and(|e| condition(e));
```

## Custom Error Type Pattern

```rust
use std::error::Error;
use std::fmt;

#[derive(Debug)]
enum MyError {
    Io(std::io::Error),
    Parse { field: String, value: String },
    NotFound(String),
}

impl fmt::Display for MyError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            MyError::Io(e) => write!(f, "IO error: {e}"),
            MyError::Parse { field, value } => write!(f, "parse error: {field}={value}"),
            MyError::NotFound(name) => write!(f, "not found: {name}"),
        }
    }
}

impl Error for MyError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            MyError::Io(e) => Some(e),
            _ => None,
        }
    }
}

impl From<std::io::Error> for MyError {
    fn from(e: std::io::Error) -> Self { MyError::Io(e) }
}

// Usage with ?
fn process() -> Result<(), MyError> {
    let f = File::open("data.txt")?;     // auto-converts via From
    Ok(())
}
```

## Combinator Chain Pattern

```rust
fn parse_and_validate(input: &str) -> Result<i32, String> {
    input
        .parse::<i32>()
        .map_err(|_| format!("not a number: '{input}'"))
        .and_then(|n| {
            if n < 0 { Err("must be positive".into()) }
            else { Ok(n) }
        })
}
```
