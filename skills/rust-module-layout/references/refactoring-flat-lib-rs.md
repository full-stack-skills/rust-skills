# Refactoring a Flat `lib.rs` — Complete Walkthrough

This is the canonical refactoring for the most common anti-pattern: a `lib.rs` that has been treated as an index page plus a sea of `pub use *::*;` re-exports.

The original example is anonymized but representative of crates authored by developers coming from Java or Python, where the instinct is "expose everything at the top so users don't have to navigate."

---

## Symptoms

You have a flat `lib.rs` if you observe any of these:

1. `lib.rs` is shorter than 30 lines and consists *only* of `pub mod` and `pub use *::*;` declarations
2. `cargo doc --no-deps` shows 50+ items at the crate root, with no submodules in the sidebar
3. IDE completion on `my_crate::` returns hundreds of unrelated symbols
4. New users cannot guess where a type lives by looking at the docs
5. Two items with the same name appear at the crate root because two different submodules glob-export them

---

## Starting Point

```rust
// src/lib.rs — typical flat layout
pub mod common;
pub use common::*;
pub mod db;
pub use db::*;
pub mod error;
pub use error::*;
pub mod ext;
pub mod io;
pub mod net;
pub mod pool;
pub mod rt;
pub mod types;
pub mod util;
pub use error::*;
pub use util::*;
```

Other files in the crate:

```text
src/
├── lib.rs           (15 lines, as above)
├── common/
│   ├── mod.rs       (30 lines)
│   ├── statement_cache.rs
│   └── constants.rs
├── db.rs            (309 lines)
├── error.rs         (3 lines — just `pub type Result<T> = ...;`)
├── ext/
│   ├── mod.rs       (3 lines)
│   ├── ustr.rs
│   └── async_stream.rs
├── io/              (10 files — buffers, codecs)
├── net/             (TCP, UDP, DNS)
├── pool/            (manager, guard)
├── rt.rs            (runtime shim)
├── types/           (date, datetime, decimal, json, time, timestamp, uuid)
└── util/
    └── scan.rs
```

---

## Diagnosis

| Symptom | Cause |
|---------|-------|
| `lib.rs` is unreadable | It's neither documentation nor code — it's a wildcard import sheet |
| Module names are 2 letters | `db`, `io`, `rt`, `ext` — abbreviated to fit Java/Python conventions |
| Every `pub mod` is followed by `pub use *::*;` | Author conflates "module organization" with "namespace flattening" |
| `types/` and `util/` are junk drawers | No domain boundaries — code dumped wherever it compiled |
| `db.rs` is 309 lines | Mixed concerns: connection, driver trait, error conversion, statement handling |

---

## Refactoring Plan

The refactor preserves the public API (zero breaking changes for 0.x → 1.0 migration). We add a deprecation shim so existing users see warnings but their code keeps compiling.

### Phase 1 — Inventory the public API

Run:

```bash
cargo doc --no-deps --output-dir target/docs-before
```

Open `target/docs-before/<crate>/index.html`. List every item shown at the root. This is what users see today. The refactor must preserve (or deprecate) every one.

### Phase 2 — Bucket items by domain

Walk the inventory and assign each item to a domain:

| Item | Domain | New home |
|------|--------|----------|
| `Error` | errors | `error::Error` (re-exported at root) |
| `Connection` | connection | `connection::Connection` (re-exported at root) |
| `Driver` | connection | `connection::Driver` |
| `Pool`, `PoolConfig` | pool | `pool::Pool`, `pool::PoolConfig` |
| `Date`, `DateTime`, `Time`, `Timestamp` | types | `types::Date`, etc. (namespaced) |
| `Decimal`, `Json`, `Uuid` | types | `types::Decimal`, etc. |
| `FastPool` | pool | `pool::FastPool` |
| `statement_cache` impl | internal | `crate::common::statement_cache` (private) |

Items that don't belong anywhere → candidates for deprecation or removal.

### Phase 3 — Rename modules

Map vague names to semantic names:

| Old | New | Reason |
|-----|-----|--------|
| `db` | `connection` | `db` is ambiguous; the module manages connections |
| `io` | `buffer` | Conflicts with `std::io`; contents are buffers/codec |
| `rt` | `runtime` | 2-letter abbreviation; `rt` collides with tokio/async-std |
| `ext` | `extensions` (or domain-specific) | "ext" is meaningless |
| `util` | `scan` (only item) | Junk drawer becomes a domain |
| `common` | `statement_cache`, `constants` (split) | "common" is a junk drawer |

### Phase 4 — Rewrite `lib.rs` as a curated facade

```rust
// src/lib.rs — after refactor
//! <Crate name> — one-sentence description.
//!
//! ## Quick start
//! ```rust
//! use my_crate::{Connection, Pool};
//! ```

mod runtime;          // was rt
mod buffer;           // was io
mod connection;       // was db
mod pool;
mod types;

mod error;
mod extensions;       // was ext
mod statement_cache;  // was common
mod scan;             // was util

// ── Curated facade ────────────────────────────────────────────────
// Only the items users need at the root. Keep this list under ~30.

pub use error::{Error, Result};

pub use connection::{Connection, Driver};
pub use pool::{Pool, FastPool};

// Re-export the type namespace as a stable submodule
pub mod types {
    //! Database type wrappers — Date, DateTime, Decimal, etc.
    pub use crate::types::*;
}

// ── Backwards-compat aliases (deprecate after 1.0) ────────────────

#[deprecated(since = "0.5.0", note = "use `my_crate::connection`")]
pub mod db {
    pub use crate::connection::*;
}

#[deprecated(since = "0.5.0", note = "use `my_crate::buffer`")]
pub mod io {
    pub use crate::buffer::*;
}

#[deprecated(since = "0.5.0", note = "use `my_crate::runtime`")]
pub mod rt {
    pub use crate::runtime::*;
}
```

### Phase 5 — Split monster files

`db.rs` (309 lines) splits into:

```text
src/connection/
├── mod.rs             // pub use {driver::*, stream::*}; pub struct Connection {...}
├── driver.rs          // Driver trait
└── stream.rs          // Connection-specific stream helpers
```

Each subfile is < 150 lines, focused on one concern.

### Phase 6 — Validate

```bash
cargo check                                  # compiles
cargo test                                   # tests pass
cargo doc --no-deps --open                   # clean hierarchy visible
cargo +nightly udeps                         # (optional) find unused deps
```

### Phase 7 — Bump version and release notes

For 0.x → 0.x+1: deprecations are non-breaking. Users see warnings but code keeps working.

For 0.x → 1.0: remove deprecated aliases. Document the breaking change in CHANGELOG.

---

## Anti-Refactor: What NOT to Do

### ❌ Don't preserve every deep path

If `my_crate::common::statement_cache::CachedStmt` was reachable before, you don't have to preserve that exact path. Decide: is `CachedStmt` part of the public API? If no, make it private. If yes, re-export it where users expect to find it.

### ❌ Don't add a `prelude` module unless you mean it

`pub mod prelude { pub use ...; }` is a commitment. Users will write `use my_crate::prelude::*;`. If the prelude changes, their code breaks. Only add a prelude if the crate has many commonly-used items (like `tokio::prelude`).

### ❌ Don't keep glob re-exports for "convenience"

`pub use foo::*;` at the crate root is convenient for the author (no decision-making) but bad for users (no provenance). Replace every glob with an explicit list.

### ❌ Don't rename without a deprecation alias

Renaming `pub mod db` to `pub mod connection` without an alias is a silent breaking change. Users' `use my_crate::db::Connection;` stops compiling. Always provide:

```rust
#[deprecated(since = "0.5.0", note = "renamed to `connection`")]
pub mod db {
    pub use crate::connection::*;
}
```

---

## Verification Checklist

After the refactor, verify:

- [ ] `cargo check` passes
- [ ] `cargo test` passes
- [ ] `cargo doc --no-deps` shows a clean sidebar with submodules
- [ ] Crate root has < 30 public items
- [ ] Every `pub use` at the root is targeted (no `*::*`)
- [ ] Module names are full words (no 2-letter abbreviations)
- [ ] Deprecated aliases exist for all renamed modules
- [ ] CHANGELOG documents the deprecations
