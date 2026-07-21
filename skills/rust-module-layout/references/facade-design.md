# Public Facade Design (C-REEXPORT, C-HIERARCHY)

How to design the public surface of a crate so users see a flat, ergonomic namespace while the implementation stays organized in a deep tree.

This reference expands on the [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/about.html) — specifically:

- **C-HIERARCHY** — Modules provide a sensible API hierarchy
- **C-REEXPORT** — Crate root re-exports common functionality

---

## The Two-Layer Model

```text
┌──────────────────────────────────────────────┐
│  Public Facade (lib.rs)                      │
│  ──────────────────────────────              │
│  pub use parser::Parser;                     │
│  pub use ast::{Expr, Stmt};                  │
│  pub use error::Error;                       │
│                                              │
│  → Users only see this layer.                │
│  → Curated, stable, ergonomic.               │
└──────────────────────────────────────────────┘
                    ↑
                    │ targeted pub use
                    │
┌──────────────────────────────────────────────┐
│  Internal Tree (private)                     │
│  ───────────────────────────                 │
│  parser/ lexer/ grammar/                     │
│  ast/    expr/    stmt/    visit/            │
│  codegen/ llvm/    cranelift/                │
│                                              │
│  → Implementation lives here.                │
│  → Deep, organized by concern.              │
│  → Invisible to external users.              │
└──────────────────────────────────────────────┘
```

---

## C-HIERARCHY — Module Hierarchy Principles

### 1. Reflect the mental model, not the file tree

If users think of your crate as having a "parser", an "AST", and a "codegen", those should be the top-level *namespaces* — even if internally `parser/` is split into `lexer/`, `grammar/`, `error/`.

```rust
// ✅ Hierarchy reflects mental model
pub mod parser { /* users can reach my_crate::parser::* */ }
pub mod ast    { /* users can reach my_crate::ast::* */ }
pub mod codegen{ /* users can reach my_crate::codegen::* */ }
```

```rust
// ❌ Hierarchy reflects implementation details
pub mod lexer { /* users don't think "lexer", they think "parser" */ }
pub mod grammar { /* ditto */ }
```

### 2. Top-level modules should be nouns or domains

Good: `parser`, `ast`, `net`, `buffer`, `time`, `crypto`
Bad: `util`, `common`, `ext`, `core` (too vague), `helpers`, `misc`

### 3. Limit top-level module count to ~7 ± 2

Human working memory holds 7±2 chunks. If your crate has 15 top-level modules, users can't navigate it. Group related modules under a parent:

```rust
// ❌ Too many top-level modules
pub mod tcp;
pub mod udp;
pub mod dns;
pub mod unix_socket;
pub mod bluetooth;
pub mod serial;

// ✅ Grouped under a parent
pub mod net {
    pub mod tcp;
    pub mod udp;
    pub mod dns;
    pub mod unix;
    pub mod bluetooth;
    pub mod serial;
}
```

### 4. Submodule depth ≤ 3 for public paths

Users shouldn't write `my_crate::net::tcp::stream::state::StreamState`. If a path is that deep, hide the deep tree and re-export the leaf:

```rust
pub mod net {
    pub use self::tcp::stream::TcpStream;        // 2 levels: net::TcpStream
    mod tcp {                                     // private
        mod stream {
            pub struct TcpStream { /* ... */ }
        }
    }
}
```

---

## C-REEXPORT — Re-export Principles

### 1. The crate root re-exports the most common types

Users should write `use my_crate::Parser;` rather than `use my_crate::parser::Parser;`. The crate root is the import surface.

```rust
// src/lib.rs
mod parser;
mod error;

pub use parser::Parser;
pub use error::Error;
```

### 2. Re-export *types*, not implementations

Re-export structs, enums, traits, and key functions. Do **not** re-export modules, internal traits, or implementation details.

```rust
// ✅ Re-export types
pub use parser::Parser;
pub use ast::{Expr, Stmt};

// ❌ Don't re-export modules wholesale
pub use parser::*;        // what's in parser? Probably internals.
```

### 3. Targeted re-exports beat globs

```rust
// ✅ Explicit list — author makes a decision per item
pub use parser::{Parser, ParseError};
pub use ast::{Expr, Stmt, Module};

// ❌ Glob — dumps everything, hides provenance
pub use parser::*;
pub use ast::*;
```

Glob re-exports are appropriate only when:
- The re-exported module contains only items that all belong at the root
- The list of items is stable (adding items is a non-breaking change but expands the root surface)
- The author has considered every item

### 4. Re-exports preserve stability

If `Parser` moves from `parser::Parser` to `parser::core::Parser`, the re-export at the crate root hides the move:

```rust
// Before
mod parser;
pub use parser::Parser;

// After internal move
mod parser;
pub use parser::core::Parser;   // callers see no change
```

This is the #1 benefit of the facade pattern: internal refactors don't break callers.

---

## Facade Sizes — Rules of Thumb

| Crate root size | Diagnosis |
|-----------------|-----------|
| 0–5 items | Probably too few — users will complain about long paths |
| 5–15 items | **Sweet spot** for most libraries |
| 15–30 items | Acceptable for large libraries; consider grouping |
| 30+ items | The crate is doing too much — split into workspace members or use `prelude` |

### The `prelude` pattern

For crates with many commonly-used types (like `tokio`, `futures`), provide a `prelude` module:

```rust
// src/lib.rs
pub use parser::Parser;
pub use ast::{Expr, Stmt};
// ... 25 more items ...

pub mod prelude {
    //! Curated re-exports for `use my_crate::prelude::*;`
    //!
    //! This brings the most commonly used types into scope.

    pub use crate::Parser;
    pub use crate::{Expr, Stmt, Module};
    pub use crate::Error;
    // ... everything a user typically needs ...
}
```

Users write:

```rust
use my_crate::prelude::*;
```

And get the most common types. **Use this sparingly** — preludes are a commitment. Once you add something to a prelude, removing it is a breaking change.

---

## Deprecating Facade Items

When you need to remove an item from the facade:

```rust
// Before
pub use parser::OldParser;

// During deprecation window (0.x → 0.x+1)
#[deprecated(since = "0.5.0", note = "use `Parser` instead")]
pub type OldParser = Parser;

// After (1.0)
// OldParser is removed; users must migrate
```

Document deprecations in CHANGELOG and release notes.

---

## Facade Anti-Patterns

### Anti-pattern: Re-exporting implementation modules

```rust
// ❌ Don't do this
pub mod parser {
    pub mod lexer;       // lexer is an implementation detail of parser
    pub mod grammar;     // grammar is an implementation detail
    pub use self::lexer::*;
    pub use self::grammar::*;
}
```

Users see `my_crate::parser::lexer::Lexer` and think it's part of the API. It isn't — it's an implementation detail. Hide it:

```rust
// ✅ Hide the tree, expose the surface
mod parser {                          // private — implementation detail
    mod lexer { /* ... */ }
    mod grammar { /* ... */ }

    pub struct Parser { /* ... */ }   // the only public item
}

pub use parser::Parser;               // flat surface
```

### Anti-pattern: Re-exporting for the author's convenience

```rust
// ❌ Author wrote this to avoid typing long paths in their own code
pub use crate::parser::lexer::token::TokenKind;
```

If users don't need `TokenKind`, don't re-export it. Internal `use` statements (in implementation modules) are fine — they're not part of the facade.

### Anti-pattern: Mirroring the internal tree as public

```rust
// ❌ This exposes internal organization as the public API
pub mod parser;
pub mod parser_lexer;       // mirrors parser/lexer/
pub mod parser_grammar;     // mirrors parser/grammar/
```

If users need to reach into the parser, give them one clean namespace (`parser::`) and put the leaf types there.

---

## Documentation as Part of the Facade

The crate's `cargo doc` output *is* the facade users see. Treat documentation as part of the design:

```rust
// src/lib.rs
//! # my_parser
//!
//! A parser for the XYZ language.
//!
//! ## Quick start
//!
//! ```rust
//! use my_parser::{Parser, Error};
//!
//! let parser = Parser::new();
//! let module = parser.parse("fn main() {}")?;
//! ```
//!
//! ## Architecture
//!
//! Internally, parsing is split into lexing ([`lexer`]), grammar ([`grammar`]),
//! and AST construction ([`ast`]). Most users only need [`Parser`] and the
//! AST types.

mod lexer;
mod grammar;
mod ast;

pub use ast::{Module, Expr, Stmt};
pub use error::Error;
pub use parser::Parser;
```

The crate-level doc string is the first thing users read. Make it count.
