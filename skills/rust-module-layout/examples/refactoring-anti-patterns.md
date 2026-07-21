# Refactoring Anti-Patterns (Step-by-Step Walkthroughs)

Concrete refactorings of common anti-patterns. All examples are anonymized composites drawn from real public crates.

---

## Refactor 1 — Flat `lib.rs` with Glob Re-exports

### Before

```rust
// src/lib.rs — anti-pattern: index + glob
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

Symptoms:
- `lib.rs` is unreadable
- `cargo doc` shows 100+ items at the crate root with no hierarchy
- IDE completion is noisy
- Users can't tell where any type actually lives

### After

```rust
// src/lib.rs — curated facade
//! Crate docs.

mod runtime;          // was rt
mod buffer;           // was io
mod connection;       // was db
mod pool;
mod types;
mod util;

mod error;
mod ext;

// Curated facade — only items users actually need
pub use error::Error;
pub use connection::Connection;
pub use pool::Pool;
pub use runtime::Runtime;

// For advanced users who want the type namespace
pub mod types {
    //! Stable type namespace — re-export of internal types.
    pub use crate::types::*;
}
```

### Migration steps

1. **Inventory** — `cargo doc --no-deps` and list every item currently at the crate root.
2. **Bucket** — group items by their natural home (types → `types`, runtime → `runtime`, etc.). Move orphan items into a new home or mark them deprecated.
3. **Rename vague modules** — `db` → `connection`, `io` → `buffer`, `rt` → `runtime`.
4. **Replace `pub use *` with targeted `pub use {A, B}`** — for each item at the root, decide: does it belong at the root (yes) or should it live under a namespace?
5. **Mark the facade `#[deprecated]` aliases** for backwards compat if you're shipping a 0.x → 1.0:

```rust
#[deprecated(note = "use my_crate::Connection instead; the db module is now connection")]
pub mod db {
    pub use crate::connection::*;
}
```

6. **Bump minor version** (semver: removing re-exports is breaking for 1.0+).
7. **Update docs** — `cargo doc --open` should now show a clean, navigable hierarchy.

---

## Refactor 2 — Monster File → Directory

### Before

```text
src/
├── lib.rs
├── crud.rs           // 591 lines: CRUD trait + 5 impls + macro + helpers
└── error.rs
```

### After

```text
src/
├── lib.rs
├── crud/
│   ├── mod.rs        // pub use {select::*, insert::*, ...}; trait CRUD {}
│   ├── select.rs
│   ├── insert.rs
│   ├── update.rs
│   ├── delete.rs
│   └── macros.rs     // macro_rules! implementations
└── error.rs
```

```rust
// src/crud/mod.rs
mod select;
mod insert;
mod update;
mod delete;
mod macros;

pub use select::select;
pub use insert::insert;
pub use update::update;
pub use delete::delete;

pub trait Crud {
    fn select(&self, q: &str);
    fn insert(&self, q: &str);
    fn update(&self, q: &str);
    fn delete(&self, q: &str);
}
```

```rust
// src/crud/select.rs
pub fn select() { /* ... */ }
```

```rust
// src/lib.rs
mod crud;
pub use crud::Crud;
```

### Migration steps

1. Identify concerns (5 CRUD operations + macros).
2. Create `src/crud/` directory.
3. Move each impl to its own file; leave the trait in `mod.rs`.
4. Add `mod <concern>;` + `pub use <concern>::<fn>;` in `mod.rs`.
5. `cargo check` — zero caller-side changes.

---

## Refactor 3 — Leaky Privacy

### Before

```rust
pub struct Connection {
    pub host: String,
    pub port: u16,
    pub socket: std::net::TcpStream,
    pub state: ConnectionState,
}

pub enum ConnectionState {
    Idle,
    Busy,
    Closed,
}
```

Symptoms:
- Users can construct `Connection` with arbitrary state
- Internal fields are mutable from outside
- Refactoring requires breaking changes

### After

```rust
pub struct Connection {
    host: String,
    port: u16,
    socket: std::net::TcpStream,
    state: ConnectionState,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ConnectionState {
    Idle,
    Busy,
    Closed,
}

impl Connection {
    pub fn new(host: &str, port: u16) -> std::io::Result<Self> {
        let socket = std::net::TcpStream::connect((host, port))?;
        Ok(Self {
            host: host.to_string(),
            port,
            socket,
            state: ConnectionState::Idle,
        })
    }

    pub fn host(&self) -> &str { &self.host }
    pub fn port(&self) -> u16 { self.port }
    pub fn state(&self) -> ConnectionState { self.state }
}
```

### Migration steps

1. Make fields private.
2. Add accessor methods (`host()`, `port()`, `state()`).
3. Add a constructor (`new()`) that validates.
4. Bump major version — this is a breaking change for downstream users who accessed fields directly.

---

## Refactor 4 — Deep Public Tree → Flat Facade

### Before

```rust
// Users have to write this nightmare:
use my_crate::connection::tcp::stream::TcpStream;
use my_crate::connection::udp::socket::UdpSocket;
```

### After

```rust
// src/lib.rs
mod connection;

pub use connection::tcp::stream::TcpStream;
pub use connection::udp::socket::UdpSocket;

// Optionally expose a cleaner namespace for power users
pub mod transport {
    //! Low-level transports — advanced API.
    pub use crate::connection::tcp::stream::TcpStream;
    pub use crate::connection::udp::socket::UdpSocket;
}
```

```rust
// User code
use my_crate::TcpStream;            // clean
// or
use my_crate::transport::TcpStream; // namespaced
```

### Migration steps

1. Identify which deep types users actually import (grep their code or survey issues).
2. Re-export those types at the crate root or a clean namespace.
3. Keep the deep tree private (`mod connection;` instead of `pub mod connection;`).
4. Bump minor version if any paths become unreachable.

---

## Refactor 5 — `#[macro_use] mod foo;` → `#[macro_export]`

### Before

```rust
// src/lib.rs
#[macro_use]
pub mod macros;
```

Symptoms:
- Every macro defined in `macros` is in scope crate-wide without explicit `use`
- IDE can't find macro definitions easily
- Hard to control which macros are exported

### After

```rust
// src/macros.rs
#[macro_export]
macro_rules! my_macro {
    () => { /* ... */ };
}

#[macro_export]
macro_rules! other_macro {
    ($x:expr) => { /* ... */ };
}
```

```rust
// src/lib.rs
mod macros;                         // private module — just for organization

pub use my_macro;                   // explicit re-export (optional if #[macro_export] is enough)
pub use other_macro;
```

### Migration steps

1. Remove `#[macro_use]` from the `mod` declaration.
2. Tag each macro with `#[macro_export]` (places it at crate root).
3. If you want a namespace, use `pub use` in `lib.rs`.
4. Add explicit `use my_crate::my_macro;` at every call site that relied on `#[macro_use]`.

---

## Refactor 6 — Vague Module Names

### Before

```rust
pub mod db;          // what's inside? driver? ORM? pool?
pub mod io;          // io of what? conflicts with std::io
pub mod rt;          // which runtime? tokio? async-std?
pub mod ext;         // extensions of what?
pub mod util;        // junk drawer
```

### After

```rust
pub mod connection;  // database connection management
pub mod buffer;      // I/O buffers — codec, framing
pub mod runtime;     // async runtime abstractions
pub mod prelude;     // curated re-exports for `use my_crate::prelude::*;`
mod hash;            // private — internal hashing helpers
mod time;            // private — internal time utilities
```

### Migration steps

1. For each vague name, ask: "what does this module *contain*?"
2. Pick a name that answers the question (`db` → `connection`, `io` → `buffer`).
3. Rename the module: `git mv src/db src/connection`.
4. Update `mod` declaration and all `use` paths.
5. For backwards compatibility, provide a deprecated alias:

```rust
#[deprecated(note = "renamed to `connection`")]
pub mod db {
    pub use crate::connection::*;
}
```

6. Bump minor version (renaming `pub mod` is a breaking change).

---

## Refactor 7 — Mixed `mod.rs` + Modern Layout

### Before

```text
src/
├── foo/
│   ├── mod.rs
│   └── bar.rs
├── baz.rs
└── baz/
    └── qux.rs
```

### After (pick one — modern shown)

```text
src/
├── foo.rs
├── foo/
│   └── bar.rs
├── baz.rs
└── baz/
    └── qux.rs
```

### Migration steps

1. `git mv src/foo/mod.rs src/foo.rs`
2. Update any `#[path]` attributes (should be none if standard layout).
3. `cargo check` — should compile with zero changes.

Don't mix layouts within a crate. Pick `foo.rs + foo/` (modern) or `foo/mod.rs` (legacy) and apply consistently.
