# Procedural Macros Overview

> The three flavors of procedural macros — derive, attribute, and function-like — and when to use them. Authoring macros is complex; route to `rust-macros` for writing your own. This file covers **using** them.

## The three flavors

| Flavor | Syntax | Runs at | Example |
|--------|--------|---------|---------|
| Derive | `#[derive(Foo)]` | compile time, appended impl | `#[derive(Debug)]` |
| Attribute | `#[foo]` on item | compile time, replaces item | `#[tokio::main]` |
| Function-like | `foo!(...)` | compile time, token stream | `vec![1, 2, 3]` |

All procedural macros take a `TokenStream` and return a `TokenStream`. They run in a separate compiler process and cannot see type information.

## 1. Derive macros — most common

Declarative `#[derive(...)]` from std or external crates.

```rust
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct User { pub id: u64, pub name: String }

// External crates add derives via their own derive macros:
// Cargo.toml: serde = { version = "1", features = ["derive"] }
//             thiserror = "1"
//             clap = { version = "4", features = ["derive"] }

#[derive(serde::Serialize, serde::Deserialize)]
pub struct Config { pub retries: u32 }

#[derive(thiserror::Error, Debug)]
pub enum Error {
    #[error("io: {0}")] Io(#[from] std::io::Error),
    #[error("missing field")] Missing,
}

#[derive(clap::Parser)]
pub struct Cli { #[arg(long)] pub name: String }
```

Std derives are pure compiler intrinsics; third-party derives (`serde`, `thiserror`, `clap`, `derive_more`) are proc-macro crates listed in `Cargo.toml`.

## 2. Attribute macros — replace the annotated item

```rust
// Cargo.toml: tokio = { version = "1", features = ["full"] }
//             tracing = "0.1"

#[tokio::main]
async fn main() {
    println!("running on tokio runtime");
}

#[tracing::instrument(skip(db))]
async fn fetch(db: &Db, id: u64) -> Result<Item, Error> {
    // tracing auto-instruments: span created, args logged
    /* ... */
    # Ok(Item)
}
```

Attribute macros rewrite the item — the original function signature may be transformed (e.g. `async fn main` becomes a synchronous `main` that sets up a runtime). Examples: `tokio::main`, `tokio::test`, `tracing::instrument`, `actix_web::get`.

## 3. Function-like macros — general-purpose

```rust
fn main() {
    // Built into std:
    let v: Vec<i32> = vec![1, 2, 3];
    let s = format!("x = {}", 5);
    let _e = unimplemented!("not yet");

    // From crates:
    // let html = html! { <div>{"hi"}</div> };            // yew / maud
    // let q = sqlx::query!("SELECT 1 AS one");           // sqlx (compile-time check)
    // let cfg = toml::toml! { port = 8080 };             // toml
}
```

Function-like macros can take any token shape (not just Rust syntax), which makes them powerful for DSLs (HTML templating, SQL, config). They are also how `println!`/`format!` work.

## When to use them — and when NOT

| Want | Right tool |
|------|------------|
| Repeated field init across many structs | `#[derive(Default)]` or builder derive |
| Auto-generate `Debug`/`Clone`/`Serialize` | Derive macro from a crate |
| Async entry point | `#[tokio::main]` attribute macro |
| Logging spans | `#[tracing::instrument]` |
| Type-checked SQL / HTML | DSL function-like macro |
| Just want to reduce boilerplate for one function | **Regular function** — not a macro |
| Conditional code | `#[cfg]` attribute — not a proc macro |
| String formatting | `format!` — built-in |
| Custom trait on many types | Derive macro OR generic impl |

Do NOT reach for a procedural macro when a regular function, generic, `#[cfg]`, or `macro_rules!` (declarative macro) will do. Proc macros:

- Slow down compilation.
- Are opaque to rust-analyzer and IDE features.
- Cannot see types — only tokens.
- Are hard to debug.

## macro_rules! vs procedural macros

```rust
// Declarative macro_rules! — pattern-matches tokens, no external crate.
macro_rules! say {
    () => { println!("nothing"); };
    ($e:expr) => { println!("got {}", $e); };
}

fn main() {
    say!();
    say!(42);
}
```

`macro_rules!` is built into the language, lives in any crate, and is fine for simple repetition. Reach for a **procedural** macro only when you need to derive a trait, transform an item's signature, or parse non-Rust syntax.

## Authoring: route to `rust-macros`

Building your own derive, attribute, or function-like macro requires a `proc-macro = true` crate, parsing with `syn`, generating with `quote`, and resolving spans for good error messages. That entire workflow is owned by the **`rust-macros`** skill.

This file deliberately stops at **using** macros — read `rust-macros` when you need to author one.

## Common pitfalls

| Symptom | Fix |
|--------|-----|
| `cannot find derive macro` | Add the crate to `Cargo.toml` and bring it into scope (`use serde::Serialize;`) |
| `proc-macro derives only work on structs and enums` | Derive macros don't apply to fns; use an attribute macro instead |
| Slow compile | Audit proc-macro crates; some (`serde`, `clap`) are heavy |
| Poor error messages from macro | Look for the `--pretty=expanded` form (`cargo expand`) |

## Reference

- [Rust by Example — Macros](https://doc.rust-lang.org/rust-by-example/macros.html)
- [Rust by Example — macro_rules!](https://doc.rust-lang.org/rust-by-example/macros/syntax.html)
- [The Rust Reference — Procedural Macros](https://doc.rust-lang.org/reference/procedural-macros.html)
- [The Rust Book — Macros](https://doc.rust-lang.org/book/ch19-06-macros.html)
- [Procedural Macros workshop](https://github.com/dtolnay/proc-macro-workshop)
