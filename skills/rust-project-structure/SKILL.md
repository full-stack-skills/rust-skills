---
name: rust-project-structure
description: Design and refactor Rust packages, crates, modules, public APIs, workspaces, dependency direction, feature boundaries, and production daemon layering. Use when users ask how to organize lib.rs or main.rs, split a crate, create a workspace, control visibility and re-exports, prevent dependency cycles, or separate protocol, domain, platform, SDK, and binary layers.
---

# Rust Project Structure and Boilerplate

> Based on *The Rust Programming Language* Chapter 7 and *The Rust Reference* Chapter 7 (Items & Modules).

## Capability Boundaries

### ✅ Strengths
1. Concepts and conventions for packages (`package`) and crates (binary/library)
2. Module file system layout: `src/lib.rs`, `src/main.rs`, submodules/directories
3. `mod` declarations and module nesting
4. Public visibility model: `pub`, `pub(crate)`, `pub(super)`, `pub(self)`
5. Import path patterns (absolute/relative, nested `A::{B,C}`, glob `A::*`, aliases `A as B`, re-exports)
6. External crate references
7. Workspace multi-package project layouts and dependency directions
8. Conditional compilation with `cfg` attributes
9. Project templates and scaffolding (`cargo new`, `cargo-generate`)

### ⚠️ Prerequisites
1. Understanding Rust ownership and module foundations (refer to the `rust-stable` skill)

### ❌ Out of Scope
1. Cargo.toml configuration → use the `rust-cargo-build` skill
2. Rust syntax fundamentals → use the `rust-stable` skill
3. Testing organization → use the `rust-testing` skill

## When to Use

- "Organize Rust project structure"
- "How modules reference each other"
- "Public visibility rules"
- "Multi-crate workspace layouts"

## Data Privacy

This skill does not collect, store, or transmit any user data.

---

# One: Packages and Crates

```rust
// Package binary + library mixed layout
my-project/
├── Cargo.toml
├── src/
│   ├── lib.rs        # Library crate root
│   └── main.rs       # Binary crate root

// Multi-binary crate layout
my-project/
├── Cargo.toml
└── src/
    ├── lib.rs
    ├── main.rs
    └── bin/
        ├── other.rs
        └── another.rs  // Each file in `bin/` is an independent binary
```

# Two: Module System

```rust
// lib.rs — Declare module(s)
pub mod front_of_house;      // Load from `front_of_house.rs` or `front_of_house/mod.rs`
mod back_of_house;           // Private modules, visible only within this crate
pub(crate) mod utils;        // Public to the entire crate but not externally accessible

// front_of_house.rs
pub mod hosting;             // Load from `hosting.rs`

// front_of_house/hosting.rs
pub fn add_to_waitlist() {}
fn seat_at_table() {}        // Default private (current module + submodules)
```

# Three: Visibility Model

```rust
pub fn public_fn() {}             // Visible externally
fn private_fn() {}                // Private by default (within current crate and its submodules)
pub(crate) fn crate_visible() {}  // Visible to the entire crate but not external
pub(super) fn parent_visible() {} // Visible within this module's parent modules
pub(self) fn module_visible() {}  // Visible within this module itself (equivalent to default visibility)
pub(in crate::foo) fn restricted() {} // Visible only in specified ancestor modules' scope
```

# Four: Import Path Patterns

```rust
// Absolute paths — `crate::` or root path
use crate::front_of_house::hosting;
use std::collections::HashMap;

// Relative paths — `self::` or `super::`
use self::back_of_house::Cook;
use super::parent_module::helper;

// Nested paths
use std::{cmp::Ordering, io};
use std::io::{self, Write};

// Glob (use with caution)
use std::collections::*;

// Aliases
use std::fmt::Result as FmtResult;

// Re-exports (`pub use`)
pub use crate::front_of_house::hosting;
// External crates can now be accessed via `my_crate::hosting`
```

# Five: Workspaces (Workspace)

```toml
# Cargo.toml (workspace root)
[workspace]
members = [
    "crates/core",
    "crates/utils",
    "app",
]
resolver = "3"
```

```text
my-workspace/
├── Cargo.toml          # Defines the workspace
├── crates/
│   ├── core/
│   │   ├── Cargo.toml  # [package] + [dependencies]
│   │   └── src/lib.rs
│   └── utils/
│       ├── Cargo.toml
│       └── src/lib.rs
├── app/
│   ├── Cargo.toml
│   └── src/main.rs
└── Cargo.lock          # Shared lock file
```

```toml
# crates/utils/Cargo.toml — References workspace crate(s)
[dependencies]
core = { path = "../core" }
```

# Six: Conditional Compilation

```rust
#[cfg(target_os = "linux")]
fn only_linux() {}

#[cfg(not(target_os = "windows"))]
fn not_windows() {}

#[cfg(feature = "serde")]
fn with_serde() {}

// `cfg!` macro (runtime check)
if cfg!(target_os = "linux") {
    println!("Running on Linux");
}

// `cfg_attr`
#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
struct Config;
```

# Seven: Project Scaffolding

```bash
cargo new my-app              # Binary project
cargo new my-lib --lib        # Library project
cargo init                    # Initialize current directory
cargo new --vcs none          # No git initialization

# Use templates (requires cargo-generate)
cargo install cargo-generate
cargo generate --git https://github.com/rust-unofficial/patterns.git
```

## Workflow

1. Confirm project type — single crate package, multi-crate package, or workspace?
2. Select naming conventions — determine binary and library names based on project purpose (snake_case)
3. Plan module hierarchy — start with `lib.rs`, split modules into files/directories by functional domain
4. Design visibility interfaces — decide which types/functions are public (`pub`), private, or crate-visible; do not mix DTOs, domain state, and platform handles across layers
5. Organize paths and imports — configure import statements to ensure compliance with module visibility rules
6. Verify dependency directions — use `cargo metadata`/`cargo tree` to confirm core crates have no reverse dependencies on CLI, network implementations, or platform-specific code
7. Validate — run `cargo check` to verify compilation success; inspect IDE module navigation

## Gotchas

1. Distinguish between `crate::` (references the current crate root) and `::other_crate_name::` (absolute path reference to an external crate).
2. Restricted visibility such as `pub(crate)` is not an Edition boundary; verify the project's Rust version rather than assuming Edition 2015 forbids it.
3. Both `module.rs` and `module/mod.rs` are supported; new code typically prefers the former, but do not misinterpret a deprecated warning as an error for using `mod.rs`.
4. Workspace resolver settings apply globally; Edition 2021 defaults to resolver 2, while Edition 2024 defaults to resolver 3.
5. The path argument in `pub(in path)` must point to ancestor modules of the current item and cannot be used to expose visibility across arbitrary sibling modules.
6. Use of the `#[path]` attribute bypasses filesystem conventions — module paths no longer follow default file tree structures after application.

## On-Demand Resources

- [Layout Examples](examples/examples.md)
- [Concept Quick Reference](references/references.md)
- [Production-grade workspace boundaries](references/production-workspace-boundaries.md): When splitting protocols, domains, platforms, transports, SDKs, adapters, and binaries, read the relevant sections.
- `examples/golden-layout/`: CI compilation module boundary examples

## Official References

- [The Book ch 7](https://doc.rust-lang.org/book/ch07-00-managing-growing-projects-with-packages-crates-and-modules.html)
- [Rust Reference ch 7 (Items)](https://doc.rust-lang.org/reference/items.html)
- [Rust Reference ch 7.2 (Modules)](https://doc.rust-lang.org/reference/items/modules.html)
- [Cargo Workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html)
