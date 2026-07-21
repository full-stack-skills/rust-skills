# Workspace Layout Patterns — Four Complete Skeletons

Copy-paste `Cargo.toml` and directory trees for each of the four workspace patterns referenced in SKILL.md. Authority: [Cargo Book — Workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html), [matklad — Large Rust Workspaces](https://matklad.github.io/2021/08/22/large-rust-workspaces.html).

---

## Pattern A — Flat `crates/` (default)

**When**: up to ~20 crates; default for new workspaces.
**Used by**: tokio, bevy, rust-analyzer, most modern Rust libraries.

```text
my-project/
├── Cargo.toml                      # virtual manifest
├── Cargo.lock
├── README.md
├── LICENSE
└── crates/
    ├── core/
    │   ├── Cargo.toml
    │   └── src/
    │       └── lib.rs
    ├── net/
    │   ├── Cargo.toml
    │   └── src/
    │       └── lib.rs
    ├── cli/                        # binary crate
    │   ├── Cargo.toml
    │   └── src/
    │       └── main.rs
    └── server/                     # binary crate
        ├── Cargo.toml
        └── src/
            └── main.rs
```

```toml
# root Cargo.toml — virtual manifest
[workspace]
resolver = "3"
members = ["crates/*"]

[workspace.package]
version = "0.1.0"
edition = "2024"
rust-version = "1.85"
license = "Apache-2.0"
repository = "https://github.com/me/my-project"

[workspace.dependencies]
# External deps pinned once
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["rt-multi-thread", "macros"] }
anyhow = "1"
tracing = "0.1"

# Internal workspace deps
my-core = { path = "crates/core" }
my-net = { path = "crates/net" }

[workspace.lints.rust]
unsafe_code = "forbid"
missing_docs = "warn"

[workspace.lints.clippy]
all = "warn"
```

```toml
# crates/net/Cargo.toml
[package]
name = "my-net"
version.workspace = true
edition.workspace = true
rust-version.workspace = true
license.workspace = true
repository.workspace = true

[dependencies]
serde.workspace = true
tokio.workspace = true
my-core.workspace = true

[lints]
workspace = true
```

**Pros**: trivial to add/remove/split crates; `members = ["crates/*"]` auto-discovers; flat namespace is easy to navigate.
**Cons**: at 50+ crates the flat list becomes hard to scan.

---

## Pattern B — Grouped `crates/<category>/`

**When**: 20+ crates with clear categorical buckets.
**Used by**: large monorepos, plugin architectures.

```text
my-project/
├── Cargo.toml
└── crates/
    ├── libs/                       # library crates
    │   ├── core/
    │   │   ├── Cargo.toml
    │   │   └── src/lib.rs
    │   ├── net/
    │   │   └── src/lib.rs
    │   └── crypto/
    │       └── src/lib.rs
    ├── bins/                       # binary crates
    │   ├── cli/
    │   │   └── src/main.rs
    │   └── server/
    │       └── src/main.rs
    └── plugins/                    # optional extensions
        ├── jwt/
        │   └── src/lib.rs
        └── redis/
            └── src/lib.rs
```

```toml
# root Cargo.toml
[workspace]
resolver = "3"
members = [
    "crates/libs/*",
    "crates/bins/*",
    "crates/plugins/*",
]
# Note: Cargo's glob `*` matches one level only.
# `crates/libs/*` matches `crates/libs/core` but NOT `crates/libs/core/sub`.

[workspace.package]
# ... same as Pattern A
```

**Pros**: scales to 50+ crates with clear categorical buckets; mirrors mental model.
**Cons**: each category must be listed in `members` explicitly; deeper nesting (e.g., `crates/libs/crypto/*`) requires explicit listing.

**Real-world example** (anonymized): a multi-platform auth library organized as:

```text
sa-token-rs/                       # actual project layout (truncated)
├── Cargo.toml
└── crates/
    ├── sa-token/                  # main facade
    ├── sa-token-core/             # core types
    ├── sa-token-axum/             # framework integration
    ├── sa-token-derive/           # proc macros
    ├── sa-token-context-mock/     # context impl
    ├── sa-token-dao-memory/       # DAO impl
    ├── sa-token-dao-redis/        # DAO impl
    ├── sa-token-plugin/           # plugins subdirectory
    │   ├── sa-token-jwt/
    │   └── sa-token-sign/
    └── sa-token-demo/             # demos subdirectory
        └── sa-token-demo-axum/
```

This is Pattern A with two nested subdirectories (`sa-token-plugin/`, `sa-token-demo/`) acting as informal category buckets. The `members` list has to enumerate them explicitly.

---

## Pattern C — Nested sub-workspaces (rare)

**When**: git submodule isolation; vendored upstream workspaces.

```text
my-project/
├── Cargo.toml                  # root workspace
├── crates/
│   └── core/
└── vendor/
    └── upstream-lib/           # nested workspace (e.g., git submodule)
        ├── Cargo.toml          # its own [workspace]
        └── crates/
            ├── lib-a/
            └── lib-b/
```

```toml
# root Cargo.toml
[workspace]
resolver = "3"
members = ["crates/*"]
exclude = ["vendor/upstream-lib"]  # exclude nested workspace
```

The nested workspace has its own `[workspace]` block and manages its own `Cargo.lock`. The root workspace excludes it to prevent conflicts.

**Pros**: git submodules can add/remove crates internally without updating the root `members` list.
**Cons**: complex; Cargo has historically had rough edges with nested workspaces. Avoid unless you specifically need submodule isolation. The [`nested_workspace`](https://crates.io/crates/nested_workspace) crate provides extra tooling if you must go this route.

---

## Pattern D — Root package workspace (small only)

**When**: 2-3 crate workspaces where one crate is unambiguously primary.

```text
my-project/
├── Cargo.toml                  # [workspace] + [package] together
├── src/                        # root package source
│   └── lib.rs
├── tests/
└── crates/
    └── cli/                    # companion binary
        ├── Cargo.toml
        └── src/
            └── main.rs
```

```toml
# root Cargo.toml
[workspace]
resolver = "3"
members = ["crates/*"]

[package]
name = "my_lib"
version = "0.1.0"
edition = "2024"

[dependencies]
# ... root package deps
```

**Acceptable for**: a library + its companion CLI (2-3 crates total).
**Avoid for**: anything larger. The trade-offs (root pollution, asymmetric commands, publishing friction) outweigh the convenience. See `mixed-root-package-antipattern.md` for what happens when Pattern D grows out of control.

---

## How to Choose

| Situation | Pattern |
|-----------|---------|
| Just starting, 1-3 crates | A (flat) |
| 3-20 crates, all related | A (flat) |
| 20+ crates, multiple categories | B (grouped) |
| Integrating a vendored workspace via submodule | C (nested) |
| Library + companion CLI (2 crates max) | D (root package) |
| Anything else | A (flat) — you can always graduate to B later |
