---
name: rust-module-layout
description: Design and enforce the internal layout of a single Rust crate — lib.rs/main.rs as a thin index, semantically named directory modules, `mod` declarations, `pub` visibility, and targeted re-exports. Use when users ask how to organize src/, write lib.rs, split a growing crate into subdirectories, choose between `foo.rs` and `foo/mod.rs`, name modules, avoid flat lib.rs "index plus glob re-export" anti-patterns, or migrate Java-style or Python-style flat projects to idiomatic Rust module trees.
---

# Rust Module Layout (Inside a Single Crate)

> Authority: [The Rust Book ch7](https://doc.rust-lang.org/book/ch07-00-managing-growing-projects-with-packages-crates-and-modules.html), [Rust Reference ch7](https://doc.rust-lang.org/reference/items/modules.html), [Rust API Guidelines — Organization](https://rust-lang.github.io/api-guidelines/about.html) (C-HIERARCHY, C-REEXPORT), [Rust Style Guide](https://doc.rust-lang.org/style-guide/).

This skill is the **crate-internal** counterpart to `rust-workspace`. That skill decides *crate boundaries* (workspace, packages, dependency direction). This skill decides *what lives inside one crate's `src/`*: the file tree, the `mod` declarations, the visibility, and the public re-export surface.

## Capability Boundaries

### ✅ Strengths
1. Translating a logical module hierarchy into a physical `src/` directory tree
2. Writing `lib.rs` / `main.rs` as a thin **index**, not a dumping ground
3. Choosing between `foo.rs` / `foo/mod.rs` / `foo/` (Edition 2018+ vs legacy)
4. Naming modules semantically (`connection` rather than `db`, `runtime` rather than `rt`)
5. Applying `pub` / `pub(crate)` / `pub(super)` / `pub(in path)` deliberately
6. Designing a flat **public facade** over a deep **private tree** via targeted `pub use`
7. Recognizing and refactoring the **"flat lib.rs + `pub use *::*`"** anti-pattern (common in crates ported from Java/Python)
8. Splitting a 500+ line file into a directory without breaking callers
9. Migrating legacy `mod.rs` layouts to the modern `foo.rs + foo/` form

### ⚠️ Prerequisites
1. Rust ownership and basic module syntax — see the `rust-stable` skill
2. Crate vs package vs workspace — see the `rust-workspace` skill

### ❌ Out of Scope
1. Cargo.toml / dependencies / features → use `rust-cargo-build`
2. Splitting a crate into workspace members → use `rust-workspace`
3. Visibility of `unsafe` blocks → use `rust-unsafe-ffi`

## Data Privacy

This skill does not collect, store, or transmit any user data.

---

# The Two Inviolable Rules

If you remember nothing else, remember these. Every Rust crate in existence obeys them:

### Rule 1 — Directories are not modules until you declare them

```rust
// ❌ You created src/string/case.rs. The compiler does not see it.
// ✅ You must declare every level:
//    src/lib.rs
pub mod string;            // loads src/string.rs OR src/string/mod.rs

//    src/string.rs (modern) OR src/string/mod.rs (legacy)
pub mod case;              // loads src/string/case.rs
```

A file sitting in a directory is invisible to the compiler until a parent module declares `mod <name>;`. This is the #1 surprise for developers coming from Java/Python/Go, where the filesystem *is* the module system.

### Rule 2 — Everything is private by default; only `pub` exposes

```rust
// src/string/case.rs
pub fn to_snake_case(s: &str) -> &str { ... }   // ✅ callable from outside
fn helper(s: &str) -> &str { ... }              // 🔒 crate-internal to this file
```

| Modifier | Visible to |
|----------|-----------|
| *(no modifier)* | Current module and its descendants only |
| `pub(crate)` | Entire crate, not external users |
| `pub(super)` | Parent module only |
| `pub(in path)` | Ancestor module `path` and its descendants |
| `pub(self)` | Same as no modifier (rarely written explicitly) |
| `pub` | Everyone (subject to parent module visibility — privacy is **parent-bound**) |

**Critical subtlety**: `pub` on an item does *not* guarantee external visibility. The item is reachable only if every module on the path from the crate root to it is also `pub`. This is why `mod string;` (private) hides everything under `string/` from external users, even if `string::case::to_snake_case` is `pub`.

---

# Decision: `foo.rs` vs `foo/mod.rs` vs `foo.rs + foo/`

Rust 2018+ introduced a third layout that eliminates `mod.rs`. All three are legal; pick one and be consistent within a crate.

| Layout | File layout | When to use |
|--------|------------|-------------|
| **Single file** | `src/foo.rs` | Module body fits in one file (rule of thumb: <300–500 lines) |
| **Legacy directory** | `src/foo/mod.rs` + `src/foo/bar.rs` | Pre-2018 codebases; required when targeting Edition 2015 |
| **Modern directory** (2018+) | `src/foo.rs` + `src/foo/bar.rs` | **Default for new code** — one fewer file per directory, no `mod.rs` boilerplate |

```text
// Modern layout (default for new crates)
src/
├── lib.rs              // pub mod foo;
├── foo.rs              // pub mod bar; pub fn root_fn() {}
└── foo/
    └── bar.rs          // pub fn bar_fn() {}
```

```text
// Legacy layout (only if Edition 2015)
src/
├── lib.rs              // pub mod foo;
└── foo/
    ├── mod.rs          // pub mod bar;
    └── bar.rs
```

**Mixing is allowed but discouraged.** If one subtree uses `foo/mod.rs` and another uses `bar.rs + bar/`, readers have to check each directory individually. Pick one per crate (the validator script enforces consistency).

---

# Canonical Layout Templates

### Template A — Small crate (< ~1000 LOC, single domain)

```text
src/
├── lib.rs              // 5–30 lines: mod decls + pub use facade
├── error.rs            // crate error type
├── parser.rs           // one file per major concern
├── ast.rs
└── codegen.rs
```

```rust
// src/lib.rs
//! One-line crate docs.
mod error;
mod parser;
mod ast;
mod codegen;

pub use error::Error;
pub use parser::parse;            // targeted re-export — only the most-used items
pub use ast::{Expr, Stmt};
```

### Template B — Medium crate (~1k–10k LOC, multiple subdomains)

```text
src/
├── lib.rs              // index + facade
├── error.rs
├── parser/
│   ├── mod.rs          // (or parser.rs in modern layout) — declares submodules
│   ├── lexer.rs
│   ├── grammar.rs
│   └── error.rs        // parser-specific errors, re-exported upward
├── ast/
│   ├── mod.rs
│   ├── expr.rs
│   ├── stmt.rs
│   └── visit.rs
└── codegen/
    ├── mod.rs
    ├── llvm.rs
    └── cranelift.rs
```

```rust
// src/lib.rs
mod error;
mod parser;
mod ast;
mod codegen;

pub use error::Error;
pub use parser::Parser;             // types users construct
pub use ast::{Expr, Stmt, Module}; // data types users manipulate
// Note: codegen stays internal — users don't construct it directly
```

### Template C — Large crate (10k+ LOC, deep nesting)

Same as Template B but:
- Each top-level directory may nest 3–4 levels deep (`parser/grammar/expr/primary.rs`)
- `lib.rs` stays thin (~50 lines max) — only `mod` + selected `pub use`
- Subdirectory `mod.rs` files act as **sub-facades**: they re-export their most useful items upward one level, but keep implementation details private
- See `references/large-crate-layout.md` for a worked 50-file example

---

# The Public Facade Pattern (C-REEXPORT)

The [Rust API Guidelines (C-REEXPORT)](https://rust-lang.github.io/api-guidelines/about.html) recommend: **the crate root re-exports the most common types so users write `use my_crate::Thing` rather than `use my_crate::deep::path::Thing`**.

```rust
// src/lib.rs — GOOD
mod connection;
mod pool;
mod query;
mod error;

// Targeted re-exports — only the items users actually need
pub use connection::Connection;
pub use pool::Pool;
pub use query::{Query, QueryBuilder};
pub use error::Error;

// The internal tree (connection/, pool/, query/) stays private.
// Users cannot reach my_crate::connection::tcp::TcpStream even if they try.
```

### Targeted re-export vs glob re-export

| Form | When OK | When bad |
|------|---------|----------|
| `pub use foo::{Bar, Baz};` | ✅ **Default** — explicit, IDE-friendly, forces author to make a decision per item | — |
| `pub use foo::*;` | Rarely — only when `foo` is a leaf module of *stably-named* items that all belong at the root | ❌ Most cases — dumps dozens of unrelated symbols into the root namespace, hides provenance, breaks IDE autocomplete |
| `pub use foo::*;` for every `foo` | Never | ❌ This is the **flat lib.rs anti-pattern** (see next section) |

Glob re-export is seductive because it "just works" — type a name, it resolves. But it has real costs:

1. **Provenance is lost**: `my_crate::Pool` — where does `Pool` actually live? `pool::`? `connection::pool::`? `connection::pool::v2::`? Readers and IDEs cannot tell.
2. **Symbol conflicts silently**: two `pub use *::*` from different submodules clash; last-write-wins.
3. **Refactoring is opaque**: moving `Pool` from `pool::` to `pool::v2::` doesn't show up in diffs because the re-export is glob.
4. **IDE completion becomes noise**: typing `my_crate::` shows hundreds of symbols instead of a curated dozen.

---

# Anti-Patterns (and how to refactor them)

These patterns appear frequently in crates authored by developers coming from Java/Python, where the language has different conventions. All examples are **anonymized** but drawn from real public crates.

| # | Anti-pattern | Symptom | Fix |
|---|--------------|---------|-----|
| 1 | **Flat `lib.rs` + glob re-exports everywhere** | `pub mod foo; pub use foo::*;` repeated for every module | Replace `pub use foo::*;` with targeted `pub use foo::{A, B};`; make implementation modules private (`mod foo;`) |
| 2 | **Monster file at `src/` root** | One file with 500+ lines mixing multiple concerns | Split into a directory, one file per concern (see `examples/splitting-files.md`) |
| 3 | **Vague / abbreviated module names** | `db`, `io`, `rt`, `ext`, `util`, `common`, `core`, `types` | Rename to semantic names: `connection`, `buffer`, `runtime` (see `references/naming.md`) |
| 4 | **Leaky privacy** (`pub` everywhere) | `pub struct Pool { pub inner: Vec<_>, pub config: _, }` | Default to private; widen only when stable (see `references/visibility-and-privacy.md`) |
| 5 | **Deep public tree** | `my_crate::connection::tcp::stream::TcpStream` | Keep the tree private; expose a flat facade (`mod connection; pub use connection::TcpStream;`) |
| 6 | **`mod.rs` in Edition 2018+ crate** | Mixed `foo/mod.rs` + `bar.rs + bar/` layouts in same crate | Pick one per crate; prefer modern `foo.rs + foo/` (see `references/modernizing-mod-rs.md`) |
| 7 | **`#[macro_use] mod foo;`** | Legacy pre-2018 macro import leaks all macros crate-wide | Use `#[macro_export]` + explicit `pub use` (see `examples/refactoring-anti-patterns.md` Refactor 5) |

For full step-by-step refactors of each anti-pattern, see:
- [`examples/refactoring-anti-patterns.md`](examples/refactoring-anti-patterns.md) — seven worked walkthroughs with before/after code
- [`references/refactoring-flat-lib-rs.md`](references/refactoring-flat-lib-rs.md) — complete migration of an index + glob `lib.rs` to a curated facade

---

# Splitting a Growing File

When a file exceeds ~500 lines or starts mixing concerns, split it into a directory.

**Mechanical procedure** (zero behavior change for callers):

1. Create `src/foo/` directory
2. For each concern in the original `foo.rs`, create `src/foo/<concern>.rs` and move the items
3. Replace `src/foo.rs` with `pub mod <concern>;` declarations and targeted re-exports to preserve the old API
4. Run `cargo check` — compilation should succeed with **zero changes to callers**

For a worked 600-line → directory example, see [`examples/splitting-files.md`](examples/splitting-files.md).

### Directory vs workspace split

- **Split into a directory** (within the same crate): subdomains share types, are always used together, or are tightly coupled. One version, one publish.
- **Split into a workspace** (separate crates): subdomains are *independently useful*, have *different stability* trajectories, or have *different dependency footprints*.

See `rust-workspace` for the workspace-level decision.

---

# Visibility Cheat Sheet

```rust
// Public — anyone with a path to this item can use it
pub fn f() {}

// Crate-visible — usable anywhere inside this crate, not by external users
pub(crate) fn g() {}

// Parent-visible — usable in the parent module and its descendants
pub(super) fn h() {}

// Restricted to an ancestor path and its descendants
pub(in crate::foo::bar) fn i() {}

// Module-private (default) — usable only inside this module
fn j() {}

// `pub` with a private parent is effectively `pub(crate)` from the outside.
// Privacy is **parent-bound**: external reachability requires every module
// on the path from the crate root to be `pub`.
mod internal {
    pub struct Hidden;          // pub, but `internal` is private → unreachable externally
}
```

---

# Workflow

1. **Identify logical domains** — list the concerns the crate addresses (parsing, AST, codegen, runtime). Each becomes a top-level module.
2. **Decide top-level visibility** — for each module, ask: is this part of the public API (users construct these types) or implementation detail? Mark implementation modules `mod` (private).
3. **Design the facade** — write `lib.rs` as if it were the only file users read. List every `pub use` they will need. If the list exceeds ~30 items, the crate is doing too much — consider a workspace split.
4. **Lay out the directory tree** — for each top-level module, decide: single file (Template A) or directory (Template B/C). Use modern `foo.rs + foo/` layout for new code.
5. **Name modules semantically** — full words, no abbreviations. The module name should tell the reader what's inside without opening the file.
6. **Apply privacy minimally** — start with everything private. Widen to `pub(crate)`, then `pub(super)`, then `pub` only when a caller actually needs it.
7. **Validate** — run `cargo check`, then `cargo doc --no-deps --open`. The generated `index.html` for your crate root is your public API. If it lists 100+ items, your facade is leaking.

## Gotchas

1. **Privacy is parent-bound.** A `pub` item inside a private `mod` is not externally reachable. Many "why can't external users see my type?" bugs trace to this.
2. **`foo.rs` and `foo/mod.rs` cannot both exist** for the same `foo` — the compiler errors out. Choose one.
3. **`#[path]` breaks filesystem conventions** and should be reserved for generated code or unusual layouts. Document why if you use it.
4. **`pub use foo::*`** at the crate root looks convenient but makes refactor diffs unreadable and IDE completion noisy. Prefer targeted `pub use foo::{A, B};`.
5. **`extern crate foo;`** is unnecessary in Edition 2018+ for most crates; just `use foo as bar;`. Keep `extern crate` only for crates that need `#[macro_use]` (rare) or rename-on-import.
6. **`pub use crate::foo::Bar;`** vs `pub use self::foo::Bar;` vs `pub use foo::Bar;` — all legal. `crate::` is the most readable for absolute paths inside the current crate; `self::` for relative; `foo::Bar` (without prefix) only works if `foo` is an external crate or in `use` scope.
7. **Renaming a module is a breaking change** if the module is `pub`. Bump the major version, or provide a deprecation alias: `pub mod old_name { pub use crate::new_name::*; }`.
8. **`mod.rs` is not deprecated.** It's required for Edition 2015 and still works in 2018+. The modern `foo.rs + foo/` layout is preferred for new code but `mod.rs` is not wrong.

## On-Demand Resources

- [Layout templates with copy-paste skeletons](examples/templates.md)
- [Flat-lib.rs refactoring walkthrough](references/refactoring-flat-lib-rs.md)
- [Large crate layout (50-file worked example)](references/large-crate-layout.md)
- [Migrating `foo/mod.rs` → `foo.rs + foo/`](references/modernizing-mod-rs.md)
- [Java/Python → Rust module mindset](references/coming-from-java-python.md)
- [Public facade design (C-REEXPORT)](references/facade-design.md)
- [Naming conventions](references/naming.md)

## Official References

- [The Rust Programming Language, ch7 — Managing Growing Projects](https://doc.rust-lang.org/book/ch07-00-managing-growing-projects-with-packages-crates-and-modules.html)
- [The Rust Reference, ch7 — Modules](https://doc.rust-lang.org/reference/items/modules.html)
- [The Rust Reference — Visibility and Privacy](https://doc.rust-lang.org/reference/visibility-privacy.html)
- [Rust API Guidelines — Organization (C-HIERARCHY, C-REEXPORT)](https://rust-lang.github.io/api-guidelines/about.html)
- [Rust Style Guide](https://doc.rust-lang.org/style-guide/)
- [Rust Edition Guide — `use` declarations](https://doc.rust-lang.org/edition-guide/rust-2018/path-changes.html)
