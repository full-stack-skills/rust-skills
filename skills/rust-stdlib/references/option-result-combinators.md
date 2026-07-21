# Option and Result Combinators

> Companion to `SKILL.md` Part 5. Canonical sources: [std::option::Option](https://doc.rust-lang.org/std/option/enum.Option.html), [std::result::Result](https://doc.rust-lang.org/std/result/enum.Result.html).

## Option combinators

| Method | Signature (essence) | Use |
|--------|---------------------|-----|
| `map` | `F(T) → U` | Transform the inner value |
| `and_then` | `F(T) → Option<U>` | Chain fallible steps |
| `or` | `Option<T>` | Replace if `None` |
| `or_else` | `F() → Option<T>` | Lazy fallback |
| `xor` | `Option<T>` | Exactly one is `Some` |
| `filter` | `F(&T) → bool` | Keep if predicate |
| `unwrap_or` | `T` | Default value |
| `unwrap_or_else` | `F() → T` | Lazy default |
| `unwrap_or_default` | — | `Default` |
| `map_or` | `default, F(T)→U` | map with default |
| `map_or_else` | `F()→U, F(T)→U` | lazy default + map |
| `ok_or` | `E` | Convert to `Result` |
| `ok_or_else` | `F()→E` | Lazy error |
| `is_some` / `is_none` | — | Predicate |
| `is_some_and` | `F(T)→bool` | Some + predicate |
| `take` | → `Option<T>` | Move out, leave `None` |
| `replace` | `T` → `Option<T>` | Swap, return old |
| `zip` | `Option<U>` → `Option<(T,U)>` | Pair two Options |
| `unzip` | → `(Option<T>, Option<U>)` | Split pairs |
| `transpose` | → `Result<Option<T>, E>` | Swap Option/Result |
| `flatten` | `Option<Option<T>>` | Collapse nesting |
| `copied` / `cloned` | → `Option<T>` | Copy/clone inner |
| `as_ref` / `as_mut` | → `Option<&T>` | Borrow without moving |
| `as_deref` / `as_deref_mut` | → `Option<&T::Target>` | Deref inner |
| `get_or_insert` | `T` → `&mut T` | Insert if missing |
| `get_or_insert_with` | `F()→T` → `&mut T` | Lazy insert |

## Result combinators

| Method | Signature (essence) | Use |
|--------|---------------------|-----|
| `map` | `F(T)→U` | Transform success |
| `map_err` | `F(E)→F` | Convert error |
| `and_then` | `F(T)→Result<U,E>` | Chain fallible |
| `or` | `Result<T,F>` | Fallback result |
| `or_else` | `F(E)→Result<T,F>` | Lazy fallback |
| `unwrap_or` / `unwrap_or_else` / `unwrap_or_default` | — | Default on err |
| `is_ok` / `is_err` | — | Predicate |
| `ok` | → `Option<T>` | Drop error |
| `err` | → `Option<E>` | Drop success |
| `transpose` | → `Option<Result<T,E>>` | Swap Result/Option |
| `as_ref` / `as_mut` | → `Result<&T,&E>` | Borrow |
| `?` operator | propagates `Err` | Early return |

## Refactor: nested match → combinator chain

Before:

```rust
fn label(opt: Option<u32>) -> String {
    match opt {
        Some(n) => match checked(n) {
            Some(c) => format!("ok-{c}"),
            None    => "bad".to_string(),
        },
        None => "missing".to_string(),
    }
}
```

After:

```rust
fn label(opt: Option<u32>) -> String {
    opt.and_then(checked)
       .map(|c| format!("ok-{c}"))
       .unwrap_or_else(|| if opt.is_none() { "missing" } else { "bad" }.to_string())
}
```

A simpler version when the "missing vs bad" distinction is not needed:

```rust
fn label(opt: Option<u32>) -> String {
    opt.and_then(checked).map_or("missing".into(), |c| format!("ok-{c}"))
}
```

## collect fallible iteration

`Iterator<Item = Result<T, E>>` can be collected into `Result<Vec<T>, E>` — short-circuiting on the first error.

```rust
fn parse_all(args: &[&str]) -> Result<Vec<i32>, std::num::ParseIntError> {
    args.iter().map(|s| s.parse::<i32>()).collect()
}
assert!(parse_all(&["1", "x", "3"]).is_err());
```

This avoids an explicit `for` loop with `?` and is idiomatic.

## The ? operator and From

`?` propagates errors after converting them via `From`. Define a single error enum and let `?` massage subsystem errors into it.

```rust
use std::{fs, io, num::ParseIntError};

#[derive(Debug)]
enum AppError {
    Io(io::Error),
    Parse(ParseIntError),
}

impl From<io::Error> for AppError { fn from(e: io::Error) -> Self { Self::Io(e) } }
impl From<ParseIntError> for AppError { fn from(e: ParseIntError) -> Self { Self::Parse(e) } }

fn load_count(path: &str) -> Result<u32, AppError> {
    let text = fs::read_to_string(path)?;        // io::Error → AppError
    let n: u32 = text.trim().parse()?;           // ParseIntError → AppError
    Ok(n)
}
```

## Custom errors with thiserror pattern

```rust
// Requires the `thiserror` crate.
use thiserror::Error;

#[derive(Debug, Error)]
enum AppError {
    #[error("io: {0}")]      Io(#[from] std::io::Error),
    #[error("parse: {0}")]   Parse(#[from] std::num::ParseIntError),
    #[error("not found: {0}")] NotFound(String),
}
```

`#[from]` auto-generates `From`, so `?` works without manual impls. For opaque errors in libraries, `Box<dyn std::error::Error + Send + Sync>` (often aliased as `Box<dyn Error>`) is a quick escape hatch.

## transpose — Option<Result> ↔ Result<Option>

```rust
let first: Option<Result<i32, &str>> = Some(Ok(5));
let swapped: Result<Option<i32>, &str> = first.transpose();   // Ok(Some(5))

let list: Vec<Option<i32>> = vec![Some(1), None, Some(3)];
let collected: Option<Vec<i32>> = list.into_iter().collect(); // None (because of the None)
```

`collect` into `Option<Vec<T>>` short-circuits at the first `None`; into `Result<Vec<T>, E>` at the first `Err`.

## take and replace

```rust
let mut slot = Some(42);
let moved = slot.take();           // Some(42); slot is now None
let prev = slot.replace(7);        // None; slot is now Some(7)
```

Useful for one-shot state or moving a value out of an `Option` field while leaving a valid placeholder.

## Common pitfalls

| Pitfall | Fix |
|---------|-----|
| `.unwrap()` in libraries | Return `Result`, or `ok_or(err)?` |
| Nested `match` | Chain combinators or use `?` |
| `if let Some(x) = opt { Some(f(x)) } else { None }` | `opt.map(f)` |
| Manual `From` for every error | `thiserror` `#[from]` |
| `opt == Some(v)` when v is not `PartialEq`-friendly | `opt.as_ref().is_some_and(\|x| ..)` |

## Reference

- [std::option::Option](https://doc.rust-lang.org/std/option/enum.Option.html)
- [std::result::Result](https://doc.rust-lang.org/std/result/enum.Result.html)
- [std::error::Error](https://doc.rust-lang.org/std/error/trait.Error.html)
- [The ? operator](https://doc.rust-lang.org/book/ch09-02-recovering-from-errors-with-result.html)
- [Rust Standard Library](https://doc.rust-lang.org/std/)
