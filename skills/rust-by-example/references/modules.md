# Modules

> Concrete patterns for `mod`, `use`, `pub`, `super`/`self`/`crate`, file-based module resolution, and re-exports. For project/workspace layout decisions, see `rust-module-layout` and `rust-workspace`.

## 1. `mod` declaration — file vs inline

```rust
// src/lib.rs
pub mod network;            // looks for src/network.rs or src/network/mod.rs
pub mod util {
    pub fn id() -> u64 { 0 }  // inline submodule
}
```

**File-based (modern, preferred):**

```text
src/
  lib.rs          // declares `pub mod network;`
  network.rs      // OR
  network/
    mod.rs         // legacy style — still supported
```

Rule of thumb: prefer `foo.rs` + optional `foo/` directory over `foo/mod.rs`. For deep layout advice, route to `rust-module-layout`.

## 2. File resolution: `foo.rs` vs `foo/mod.rs`

Both are accepted; pick one per project and be consistent. The compiler errors if both exist.

```text
# Modern form
src/network.rs
src/network/tcp.rs
src/network/udp.rs

# Legacy form (still works)
src/network/mod.rs
src/network/tcp.rs
src/network/udp.rs
```

Mixed style within one crate is legal but confusing — standardize.

## 3. `use` statements — simple, grouped, renamed

```rust
use std::collections::HashMap;              // simple
use std::io::{self, Read, Write};           // grouped: io module + two traits
use std::fmt::Write as FmtWrite;            // renamed to avoid clash
use std::time::{Duration, Instant};         // multiple siblings in one block
```

The `self` keyword inside a brace imports the parent module itself alongside its children.

## 4. `pub`, `pub(crate)`, `pub(super)`, `pub(in path)`

```rust
// crate is a library
pub struct Client;                          // visible to anyone using this crate
pub(crate) fn internal_helper() {}          // visible anywhere in this crate
pub(super) fn helper_for_parent() {}        // visible to parent module only
mod detail {
    pub(in crate::detail) fn deep() {}      // only this subtree
}
```

| Visibility | Visible to |
|-----------|------------|
| `pub` | Everyone |
| `pub(crate)` | Anything in the current crate |
| `pub(super)` | The parent module |
| `pub(in path)` | A specific module subtree |
| (no `pub`) | Current module only |

## 5. `self` / `super` / `crate` paths

```rust
// src/network/tcp.rs
use self::reader::Reader;       // child of current module
use super::udp::UdpSocket;      // sibling in parent
use crate::network::Client;     // absolute from crate root

mod reader {
    pub struct Reader;
}
```

- `crate::` — absolute, from crate root. Most robust in larger code.
- `super::` — one level up. Useful for reaching siblings without re-typing parents.
- `self::` — current module. Rare except inside `use` blocks.

## 6. Re-exports at crate root — `pub use`

Hide internal structure; expose a clean API surface.

```rust
// src/network/tcp.rs
pub struct TcpStream;

// src/lib.rs
mod network;
pub mod tcp { pub use crate::network::tcp::TcpStream; }  // nested re-export

// Or flatten directly:
mod network2;
pub use network2::tcp::TcpStream as Tcp;                 // rename on re-export
```

Re-exports are how the standard library exposes `std::io::Write` from `std::fmt::Write` style aliases. Use `pub use ... as ...` to give consumers a stable name even if internal paths move.

## 7. Full mini-crate

```rust
// src/lib.rs
pub mod api;
pub mod db;
pub use api::Client;           // re-export at crate root

pub fn version() -> &'static str { "1.0.0" }
```

```rust
// src/api.rs
pub struct Client;
impl Client {
    pub fn new() -> Self { Self }
}
```

```rust
// user code (different crate)
use my_crate::Client;          // works because of `pub use`
let _c = Client::new();
```

## Common pitfalls

| Symptom | Fix |
|--------|-----|
| `unresolved module` error | File named `foo.rs` but declared `pub mod foo;` — check spelling and that file lives next to the declaring module |
| `function is private` even after `pub` | A parent in the path is private — make the chain public, or `pub(crate)` and re-export |
| `foo.rs` AND `foo/mod.rs` both exist | Pick one — remove the other |
| `use` of an item not found | Try absolute `crate::...` path to disambiguate |
| Glob `use foo::*` pollutes namespace | Prefer explicit named imports |

## Reference

- [Rust by Example — Modules](https://doc.rust-lang.org/rust-by-example/mod.html)
- [Rust by Example — Crates](https://doc.rust-lang.org/rust-by-example/crates.html)
- [Rust by Example — use declarations](https://doc.rust-lang.org/rust-by-example/mod/use.html)
- [Rust by Example — super and self](https://doc.rust-lang.org/rust-by-example/mod/super.html)
- [The Rust Reference — Paths](https://doc.rust-lang.org/reference/paths.html)
- [The Rust Book — Modules](https://doc.rust-lang.org/book/ch07-00-managing-growing-projects-with-packages-crates-and-modules.html)
