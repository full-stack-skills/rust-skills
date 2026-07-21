# Layout Templates (Copy-Paste Skeletons)

Each template is a complete `src/` tree you can clone and rename. Pick the one that matches your crate's size.

---

## Template A — Single-Domain Library (small)

**Use when**: crate has one major concern, < 1000 LOC, < 10 public items.

```text
my_crate/
├── Cargo.toml
└── src/
    ├── lib.rs
    └── error.rs
```

```rust
// src/lib.rs
//! One-sentence crate description.

mod error;

pub use error::Error;

// Public API goes here — keep all implementation in this file
// until it exceeds ~500 lines, then promote to Template B.
pub fn do_thing(input: &str) -> Result<String, Error> {
    // ...
    Ok(input.to_uppercase())
}
```

```rust
// src/error.rs
use std::fmt;

#[derive(Debug)]
pub enum Error {
    Invalid(String),
    Io(std::io::Error),
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::Invalid(s) => write!(f, "invalid input: {s}"),
            Error::Io(e) => write!(f, "io: {e}"),
        }
    }
}

impl std::error::Error for Error {}

impl From<std::io::Error> for Error {
    fn from(e: std::io::Error) -> Self { Error::Io(e) }
}
```

---

## Template B — Multi-Domain Library (medium)

**Use when**: crate has 3–6 distinct subdomains, 1k–10k LOC.

```text
my_crate/
├── Cargo.toml
└── src/
    ├── lib.rs
    ├── error.rs
    ├── parser.rs          // or parser/mod.rs in legacy layout
    ├── parser/
    │   ├── lexer.rs
    │   └── grammar.rs
    ├── ast.rs
    └── codegen.rs
```

```rust
// src/lib.rs
//! Crate docs.

mod error;
mod parser;
mod ast;
mod codegen;

pub use error::Error;
pub use parser::Parser;
pub use ast::{Expr, Stmt, Module};
// codegen stays internal — users don't call into it directly

/// Top-level convenience entry point.
pub fn parse_and_compile(input: &str) -> Result<String, Error> {
    let parser = Parser::new();
    let module = parser.parse(input)?;
    Ok(codegen::compile(&module))
}
```

```rust
// src/parser.rs
// Modern layout: src/parser.rs + src/parser/ directory coexist.
mod lexer;                  // src/parser/lexer.rs
mod grammar;                // src/parser/grammar.rs

pub use self::lexer::Lexer;
pub use self::grammar::Grammar;

pub struct Parser { /* ... */ }

impl Parser {
    pub fn new() -> Self { /* ... */ unimplemented!() }
    pub fn parse(&self, input: &str) -> Result<crate::ast::Module, crate::Error> {
        unimplemented!()
    }
}
```

---

## Template C — Deep Domain Library (large)

**Use when**: crate has many subdomains, 10k+ LOC, public API has > 30 items.

```text
my_crate/
├── Cargo.toml
└── src/
    ├── lib.rs                 // ~50 lines: mod decls + curated facade
    ├── error.rs
    ├── runtime/
    │   ├── mod.rs             // (or runtime.rs + runtime/)
    │   ├── scheduler.rs
    │   ├── task.rs
    │   └── waker.rs
    ├── net/
    │   ├── mod.rs
    │   ├── tcp.rs
    │   ├── udp.rs
    │   └── dns.rs
    ├── buffer/
    │   ├── mod.rs
    │   ├── read.rs
    │   └── write.rs
    └── util/
        ├── mod.rs
        ├── time.rs
        └── hash.rs
```

```rust
// src/lib.rs
//! Crate docs — what users will read first.

mod error;
mod runtime;
mod net;
mod buffer;
mod util;

// Curated public facade — keep this list under ~30 items.
// If it grows beyond that, the crate should probably split.
pub use error::Error;
pub use runtime::{Runtime, RuntimeBuilder};
pub use net::{TcpListener, UdpSocket};
pub use buffer::Buffer;

// util stays private — it's an implementation detail.
// If users genuinely need util::time::now(), consider whether
// they should depend on a separate `my-crate-util` crate instead.
```

---

## Template D — Binary + Library Crate

**Use when**: crate ships both a library (for embedding) and a binary (CLI).

```text
my_crate/
├── Cargo.toml
└── src/
    ├── lib.rs                // public library API
    ├── main.rs               // thin binary entry — delegates to lib
    ├── error.rs
    └── cli/                  // binary-only modules
        ├── args.rs
        └── output.rs
```

```rust
// src/main.rs
use my_crate::{do_thing, Error};

mod cli;                      // binary-private — not visible from library

fn main() -> Result<(), Error> {
    let args = cli::args::parse();
    let result = do_thing(&args.input)?;
    cli::output::print(result);
    Ok(())
}
```

```rust
// src/lib.rs — the library knows nothing about the CLI
mod error;
pub use error::Error;

pub fn do_thing(input: &str) -> Result<String, Error> {
    Ok(input.to_uppercase())
}
```

```toml
# Cargo.toml
[package]
name = "my_crate"

[lib]
name = "my_crate"
path = "src/lib.rs"

[[bin]]
name = "my_crate"
path = "src/main.rs"
```

---

## Template E — Multi-Binary Workspace Member

**Use when**: crate ships several binaries sharing common library code.

```text
my_crate/
├── Cargo.toml
└── src/
    ├── lib.rs                // shared library
    ├── bin/
    │   ├── server.rs         // each file in bin/ is one binary
    │   ├── client.rs
    │   └── benchmark.rs
    └── shared/               // library modules used by multiple binaries
        ├── mod.rs
        └── protocol.rs
```

```rust
// src/bin/server.rs
use my_crate::shared::protocol;

fn main() {
    let request = protocol::Request::new();
    // ...
}
```

---

## Template F — Plugin / Extension Crate

**Use when**: crate is loaded as a dynamic plugin, with a clear API boundary.

```text
my_crate/
├── Cargo.toml
└── src/
    ├── lib.rs                // exports only the plugin ABI
    ├── api.rs                // the ABI types
    ├── api/
    │   ├── mod.rs            // legacy: src/api/mod.rs + src/api/
    │   ├── v1.rs
    │   └── v2.rs
    └── plugins/
        ├── mod.rs
        ├── auth.rs
        └── cache.rs
```

```rust
// src/lib.rs
//! Public ABI for plugins — keep this stable across versions.

mod api;
mod plugins;

pub use api::{Plugin, PluginContext, PluginError};

// Versioned API namespaces
pub mod v1 { pub use crate::api::v1::*; }
pub mod v2 { pub use crate::api::v2::*; }
```

---

## Which Template Should I Pick?

| Situation | Template |
|-----------|----------|
| Toy / utility crate, < 500 LOC | A |
| Single domain, growing past one file | A → B |
| 3–6 subdomains, library only | B |
| Large library, many subdomains | C |
| Ship a CLI + a library | D |
| Ship multiple CLIs | E |
| Plugin / dynamically loaded | F |
