# `sa-token-rs` Case Study — 11-crate Virtual Workspace

> Source: [github.com/dromara/sa-token-rs](https://github.com/dromara/sa-token-rs) — a Rust port of the Java Sa-Token permission framework. Used here as a real-world exemplar of the patterns taught in `rust-workspace`.

This file walks through the full workspace member-by-member: the root manifest, every member's `Cargo.toml`, the dependency DAG verification, and how the layout supports independent publishing and feature gating.

## Why this is a reference example

`sa-token-rs` demonstrates every best practice in one project:

- **Virtual manifest** (no root `[package]`) — clean root, `cargo build` builds all 11 by default
- **5-layer DAG** — core → leaves → facade → adapters/plugins/DAOs → demos/tests — every arrow points up
- **Contained + domain-grouped hybrid** — primary crates live under `crates/`, while plugin and demo families have their own subdirectories
- **Full `[workspace.*]` inheritance** — package metadata, dependencies, and lints defined once at root
- **Edition 2024 + MSRV 1.85** — declared once, inherited everywhere
- **Feature-gated optional dep** — Redis DAO behind `redis = ["dep:sa-token-dao-redis"]`

## Root `Cargo.toml` (annotated)

```toml
[workspace]
members = [
    "crates/sa-token",                            # L3: facade
    "crates/sa-token-axum",                       # L4: axum adapter
    "crates/sa-token-core",                       # L1: core
    "crates/sa-token-derive",                     # L2: proc-macro
    "crates/sa-token-context-mock",               # L2: mock context
    "crates/sa-token-dao-memory",                 # L2: memory DAO
    "crates/sa-token-dao-redis",                  # L4: redis DAO
    "crates/sa-token-plugin/sa-token-jwt",        # L4: JWT plugin (grouped)
    "crates/sa-token-plugin/sa-token-sign",       # L4: sign plugin (grouped)
    "crates/sa-token-demo/sa-token-demo-axum",    # L5: demo (grouped)
    "crates/sa-token-test",                       # L5: integration tests
]
resolver = "3"                                    # Edition 2024 default — MSRV-aware

[workspace.package]
version = "0.1.0"
edition = "2024"                                  # this skill's required edition
rust-version = "1.85"                             # MSRV — enforced across all members
license = "Apache-2.0"
repository = "https://github.com/dromara/sa-token-rs"

[workspace.dependencies]
# Internal crates — path + (implicitly) version for publishing
sa-token = { path = "crates/sa-token" }
sa-token-core = { path = "crates/sa-token-core" }
sa-token-derive = { path = "crates/sa-token-derive" }
sa-token-context-mock = { path = "crates/sa-token-context-mock" }
sa-token-dao-memory = { path = "crates/sa-token-dao-memory" }
sa-token-dao-redis = { path = "crates/sa-token-dao-redis" }
sa-token-jwt = { path = "crates/sa-token-plugin/sa-token-jwt" }
sa-token-sign = { path = "crates/sa-token-plugin/sa-token-sign" }

# External deps — pinned once, shared everywhere
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tokio = { version = "1", features = ["full"] }
axum = { version = "0.7" }
thiserror = "2"
tracing = "0.1"
chrono = "0.4"
uuid = { version = "1", features = ["v4"] }

[workspace.lints.rust]
unsafe_code = "forbid"
missing_docs = "warn"

[workspace.lints.clippy]
all = "warn"
pedantic = "warn"
```

## Layer 1 — `sa-token-core` (the foundation)

```toml
[package]
name = "sa-token-core"
version.workspace = true
edition.workspace = true
rust-version.workspace = true
license.workspace = true
description = "Core types and extension points for sa-token-rs"

[dependencies]
serde.workspace = true
serde_json.workspace = true
thiserror.workspace = true
tracing.workspace = true
chrono.workspace = true
uuid.workspace = true
rand.workspace = true
regex.workspace = true
url.workspace = true
base64.workspace = true

[lints]
workspace = true
```

**Key observation**: `sa-token-core` depends on **zero internal crates**. It defines the traits (`SaTokenContext`, `SaTokenDao`, `SaTokenPlugin`) and types (`SaTokenError`, `SaTokenResult`, session/login models) that everyone else builds on. This is what makes the DAG acyclic.

## Layer 2 — three independent leaves

Each of these depends on `sa-token-core` only — no other internal deps.

### `sa-token-derive` (proc-macro)

```toml
[package]
name = "sa-token-derive"
version.workspace = true
edition.workspace = true
# ... inheritance ...

[lib]
proc-macro = true

[dependencies]
sa-token-core.workspace = true
syn.workspace = true
quote.workspace = true
proc-macro2.workspace = true
```

Proc-macro crates need their own `[lib] proc-macro = true` declaration. They sit at Layer 2 because they only consume core types (for generating trait impls).

### `sa-token-context-mock`

```toml
[dependencies]
sa-token-core.workspace = true
```

A mock implementation of `SaTokenContext` for testing. Lives at Layer 2 so the facade can bundle it as the default test context.

### `sa-token-dao-memory`

```toml
[dependencies]
sa-token-core.workspace = true
```

In-memory DAO implementation. The default backend; bundled into the facade unconditionally.

## Layer 3 — `sa-token` (the facade)

The public API crate. Downstream users add `sa-token` to their `Cargo.toml` and get the full framework.

```toml
[package]
name = "sa-token"
version.workspace = true
edition.workspace = true
rust-version.workspace = true
license.workspace = true
description = "Sa-Token-Rs: 轻量级权限认证框架"

[features]
default = []
redis = ["dep:sa-token-dao-redis"]           # opt into Redis backend

[dependencies]
sa-token-core.workspace = true               # L1
sa-token-derive.workspace = true             # L2
sa-token-context-mock.workspace = true       # L2
sa-token-dao-memory.workspace = true         # L2
sa-token-dao-redis = { workspace = true, optional = true }   # L4, feature-gated

[lints]
workspace = true
```

**Key observations**:
- Re-exports core types and the derive macros — downstream does `use sa_token::SaTokenContext`, not `use sa_token_core::SaTokenContext`.
- `redis` feature gates the Redis DAO. Downstream without Redis doesn't pull in `redis` crate.
- Does **not** depend on `sa-token-axum`, `sa-token-jwt`, or `sa-token-sign` — those are optional adapters/plugins that downstream opts into separately.

## Layer 4 — adapters, plugins, and backends

These depend on the facade + core. They're the "optional integrations" a downstream project picks from.

### `sa-token-dao-redis`

```toml
[dependencies]
sa-token-core.workspace = true
sa-token.workspace = true
sa-token-context-mock.workspace = true
redis = { workspace = true }
```

### `sa-token-axum`

```toml
[dependencies]
sa-token-core.workspace = true
sa-token.workspace = true
sa-token-dao-memory.workspace = true
sa-token-context-mock.workspace = true
axum.workspace = true
tower.workspace = true
```

### `sa-token-plugin/sa-token-jwt` (grouped under `sa-token-plugin/`)

```toml
[dependencies]
sa-token-core.workspace = true
sa-token.workspace = true
sa-token-dao-memory.workspace = true
sa-token-context-mock.workspace = true
```

### `sa-token-plugin/sa-token-sign` (grouped under `sa-token-plugin/`)

```toml
[dependencies]
sa-token-core.workspace = true
sa-token.workspace = true
```

## Layer 5 — demos and integration tests

### `sa-token-demo/sa-token-demo-axum` (grouped under `sa-token-demo/`)

```toml
[dependencies]
sa-token = { path = "../../sa-token" }         # direct path (demo isn't published)
sa-token-axum = { path = "../../sa-token-axum" }
tokio.workspace = true
axum.workspace = true
```

Demos use `path = "..."` directly instead of `workspace = true` because they're not published and don't need version coordination.

### `sa-token-test`

```toml
[dependencies]
sa-token.workspace = true
sa-token-core.workspace = true
# ... other members under test ...
```

The integration test crate. Depends on the facade + core + any member under test.

## DAG verification

```bash
# Visualize the full dep graph
cargo tree --workspace

# What depends on sa-token-core? (should be everyone except itself)
cargo tree --invert --package sa-token-core

# Check for duplicate versions
cargo tree --duplicates

# Confirm no cycles (cargo will error if any)
cargo check --workspace
```

### Expected `cargo tree --invert --package sa-token-core` output

```
sa-token-core v0.1.0
├── sa-token-context-mock v0.1.0
├── sa-token-dao-memory v0.1.0
├── sa-token-dao-redis v0.1.0
├── sa-token-derive v0.1.0
├── sa-token-axum v0.1.0
│   ├── sa-token-demo-axum v0.1.0
│   └── sa-token-test v0.1.0
├── sa-token-jwt v0.1.0
├── sa-token-sign v0.1.0
└── sa-token v0.1.0
    ├── sa-token-axum v0.1.0 (*)     (already listed)
    ├── sa-token-demo-axum v0.1.0 (*)
    ├── sa-token-jwt v0.1.0 (*)
    ├── sa-token-sign v0.1.0 (*)
    └── sa-token-test v0.1.0 (*)
```

Every member appears. No back-edges. `sa-token-core` is the root of the inverted tree — proof it's the foundation.

## Publishing implications

Because internal deps are declared in `[workspace.dependencies]` with `path = "..."`, `cargo publish` needs version numbers to publish to crates.io. Two options:

1. **Add `version = "0.1"` to each `[workspace.dependencies]` entry** — then `cargo workspaces publish` (from `cargo-workspaces`) handles the topological order automatically.
2. **Hand-publish in DAG order** — `cargo publish -p sa-token-core` first, then `sa-token-derive`, then `sa-token`, etc.

The current `sa-token-rs` uses option 1's pattern but hasn't published yet (still at 0.1.0 with `publish = false` implied by not being on crates.io). When ready, adding versions to `[workspace.dependencies]` and running `cargo workspaces publish` will work.

## What this teaches

| Pattern | How `sa-token-rs` does it |
|---------|--------------------------|
| Virtual manifest | `[workspace]` at root, no `[package]` |
| Layered DAG | 5 layers, every arrow points up |
| Facade pattern | `sa-token` re-exports core + leaves |
| Optional plugins | Adapters/plugins depend on facade, not bundled by default |
| Grouped sub-crates | `sa-token-plugin/` and `sa-token-demo/` are domain families inside the contained layout |
| Workspace inheritance | `[workspace.package]`, `[workspace.dependencies]`, `[workspace.lints]` |
| Feature gating | `redis = ["dep:sa-token-dao-redis"]` |
| Edition + MSRV | `edition = "2024"`, `rust-version = "1.85"` inherited |
| Lint policy | `unsafe_code = "forbid"`, `missing_docs = "warn"`, `clippy::pedantic = "warn"` |

## Contrast with the anti-pattern

Compare `sa-token-rs` (virtual manifest, 5-layer DAG) with the **mixed root package anti-pattern** (rbatis-style: `[workspace] + [package]` at root, 642-line `src/executor.rs` at top level). `sa-token-rs` has:

- No `src/` at root (all code lives in `crates/<member>/src/`)
- No `[package]` at root (pure workspace config)
- No ambiguity about which crate is "primary" (it's `sa-token`, the facade, not the workspace root)
- `cargo build` builds everything by default (no `--workspace` needed)

## Source

- [sa-token-rs on GitHub](https://github.com/dromara/sa-token-rs)
- [Sa-Token (Java original)](https://sa-token.cc/) — the framework this port is based on
