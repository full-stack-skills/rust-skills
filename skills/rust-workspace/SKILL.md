---
name: rust-workspace
description: Design Rust project topology — single-crate packages, multi-crate workspaces (virtual manifests, flat/grouped/nested layouts), workspace-level configuration (shared deps, lints, package metadata), dependency direction DAGs, and crate boundary decisions. Use when users ask how to split a project into crates, configure a workspace, avoid dependency cycles, refactor a mixed root-package workspace (rbatis-style), or decide between modules-in-one-crate vs separate crates. For in-crate src/ layout, see rust-module-layout.
---

# Rust Workspace and Project Topology

> Authority: [Cargo Book — Workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html), [The Book ch7](https://doc.rust-lang.org/book/ch07-00-managing-growing-projects-with-packages-crates-and-modules.html) and [ch14-03](https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html), [Rust Reference ch7](https://doc.rust-lang.org/reference/items/modules.html), [RFC 1525](https://rust-lang.github.io/rfcs/1525-cargo-workspace.html), [matklad — Large Rust Workspaces](https://matklad.github.io/2021/08/22/large-rust-workspaces.html).

This skill decides **how many crates a project should have and how they relate**. Its companion `rust-module-layout` decides **what lives inside one crate's `src/`**.

## Capability Boundaries

### ✅ Strengths
1. Single-crate vs multi-crate workspace decision (decision tree with five concrete triggers)
2. Four workspace layout patterns: flat `crates/`, grouped `crates/<category>/`, nested sub-workspaces, root package
3. Virtual manifest vs root package — trade-offs and migration
4. Workspace-level shared configuration: `[workspace.package]`, `[workspace.dependencies]`, `[workspace.lints]`
5. Dependency direction DAGs — types → core → sdk → server → binary
6. Diagnosing and refactoring the "mixed root package" anti-pattern
7. Crate naming, publishing, and version coordination across members

### ⚠️ Prerequisites
1. Rust ownership and basic module syntax — see `rust-stable`
2. In-crate module layout (lib.rs facade, mod declarations, visibility) — see `rust-module-layout`

### ❌ Out of Scope
1. Cargo.toml `[dependencies]` syntax and feature resolution → use `rust-cargo-build`
2. In-crate src/ directory layout → use `rust-module-layout`
3. Rust syntax fundamentals → use `rust-stable`
4. Testing organization → use `rust-testing`

## When to Use

- "Should I split this into a workspace or keep it one crate?"
- "How do I configure a Cargo workspace?"
- "Refactor my rbatis-style mixed root package"
- "Why does cargo only build one crate at the root?"
- "How do I share dependencies across workspace members?"
- "Is my dependency direction correct?"

## Data Privacy

This skill does not collect, store, or transmit any user data.

---

# Foundations — Packages, Crates, Modules

> In-crate module layout depth (mod files, visibility, re-exports) is covered by the companion `rust-module-layout` skill. This section covers only the parts that affect project-level decisions.

### Package vs crate vs workspace

| Term | Meaning |
|------|---------|
| **Package** | One `Cargo.toml` and the source it points at; what you publish to crates.io |
| **Crate** | A compilation unit — either a library (`src/lib.rs`) or a binary (`src/main.rs`, `src/bin/*.rs`). A package can contain multiple crates (1 lib + N binaries). |
| **Workspace** | A collection of packages sharing one `Cargo.lock` and `target/`. |
| **Module** | A nameable scope inside a crate — declared with `mod foo;`, resolved to `src/foo.rs` or `src/foo/mod.rs`. |

### Single-package layouts

```text
# Library only                      # Binary only                  # Library + binary
my-lib/                             my-app/                        my-crate/
├── Cargo.toml                      ├── Cargo.toml                 ├── Cargo.toml
└── src/                            └── src/                       └── src/
    └── lib.rs                          └── main.rs                 ├── lib.rs
                                                                      └── main.rs

# Multi-binary (one package, multiple binaries)
my-app/
├── Cargo.toml
└── src/
    ├── lib.rs
    ├── main.rs                      # binary named after the package
    └── bin/
        ├── tool_a.rs                # binary `tool_a`
        └── tool_b.rs                # binary `tool_b`
```

### Module declaration (the rule that surprises Java/Python devs)

```rust
// src/lib.rs — declare modules explicitly; directories are NOT auto-discovered
pub mod front_of_house;      // loads src/front_of_house.rs OR src/front_of_house/mod.rs
mod back_of_house;           // private
pub(crate) mod utils;        // crate-visible
```

Everything is **private by default**; `pub` exposes. See `rust-module-layout` for the full visibility model, the parent-bound reachability rule, and the modern `foo.rs + foo/` layout.

### `use` paths (quick reference)

```rust
use crate::front_of_house::hosting;       // absolute (current crate)
use std::collections::HashMap;            // absolute (external)
use self::back_of_house::Cook;            // relative (current module)
use super::parent_module::helper;         // relative (parent)
use std::{cmp::Ordering, io};             // nested
use std::fmt::Result as FmtResult;        // alias
pub use crate::front_of_house::hosting;   // re-export (facade pattern)
```

### Conditional compilation

```rust
#[cfg(target_os = "linux")]
fn only_linux() {}

#[cfg(feature = "serde")]
fn with_serde() {}

#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
struct Config;

if cfg!(target_os = "linux") { /* runtime check */ }
```

# Project Scaffolding

```bash
cargo new my-app              # Binary project
cargo new my-lib --lib        # Library project
cargo init                    # Initialize current directory
```

For multi-crate workspaces, prefer to create the root virtual manifest by hand (there is no `cargo workspace new`), then `cargo new --lib crates/<name>` for each member. For templates, use [`cargo-generate`](https://github.com/cargo-generate/cargo-generate).

---

# Workspace Patterns (single-crate vs multi-crate)

> Authority: [Cargo Book — Workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html), [The Book ch14-03](https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html), [matklad — Large Rust Workspaces](https://matklad.github.io/2021/08/22/large-rust-workspaces.html), [RFC 1525](https://rust-lang.github.io/rfcs/1525-cargo-workspace.html).

A **workspace** is a collection of one or more packages that share a single `Cargo.lock` and `target/` directory. Workspaces exist for four reasons: **faster builds** (shared dependency compilation), **coordinated versions** (one lockfile, one `cargo publish` flow), **cleaner boundaries** (each crate is an independent compilation unit with its own public API), and **independent reuse** (users can depend on one crate without pulling in the others).

## Decision tree — how many crates?

```
Is this project one cohesive library or one binary?
├── Yes → Single-crate layout (Section 8.1)
└── No, it has multiple subdomains
    ├── Do the subdomains share types and call each other heavily?
    │   └── Single-crate with module directories (use rust-module-layout skill)
    └── At least one subdomain is independently useful / independently versioned / has different deps?
        └── Multi-crate workspace (Section 8.2)
```

**Rule of thumb**: split into crates only when at least one of these is true (from `references/production-workspace-boundaries.md`):
1. The subdomain requires independent publishing or third-party reuse
2. The subdomain needs distinct `feature` / target / `no_std` / WASM boundaries
3. You need to **prohibit** a reverse dependency at compile time (e.g., `core` must not depend on `tokio`)
4. The subdomain has an independently versioned public API
5. Test/build lifecycles are significantly different

If none of these apply, **prefer modules over crates**. Modules are cheaper (no publish, no version coordination, no separate `Cargo.toml`). See the `rust-module-layout` skill for in-crate organization.

## Single-crate layout

The default for small-to-medium projects. One `Cargo.toml`, one `src/`. Four variants: library only, binary only, library + binary (same package), or multi-binary (`src/bin/<name>.rs`). See `examples/single-crate.md` for all four skeletons.

**When to graduate to a workspace**: when a second binary appears, or when the library grows large enough to want its own version trajectory separate from the binary.

## Multi-crate workspace — two flavors of root

Cargo supports two kinds of root `Cargo.toml`:

| Flavor | What's in root | When to use |
|--------|---------------|-------------|
| **Virtual manifest** | `[workspace]` only — **no `[package]`** | **Default for new workspaces.** Clean root, no `src/` at the top level, all crates live under `crates/`. |
| **Root package** | `[workspace]` **+** `[package]` + `src/` at root | Small (2-3 crate) workspaces where one crate is unambiguously primary; you accept the trade-offs below. |

The Cargo team and community (notably matklad's [Large Rust Workspaces](https://matklad.github.io/2021/08/22/large-rust-workspaces.html)) recommend **virtual manifests** for any non-trivial workspace:

1. **Root pollution** — a `[package]` at the root forces `src/`, `tests/`, `benches/` into the top level alongside every other crate's directory.
2. **Command ergonomics** — with a root package, `cargo build` at the root builds *only* the root package; `--workspace` is needed for everything. Virtual manifests build all members by default.
3. **Publishing friction** — root package + members leads to confusing `cargo publish` ordering.

## Four layout patterns

| Pattern | Layout | When | Used by |
|---------|--------|------|---------|
| **A. Flat `crates/`** | `crates/<name>/` (one level) | **Default** for most projects; up to ~20 crates | tokio, bevy, rust-analyzer |
| **B. Grouped `crates/<category>/`** | `crates/libs/*`, `crates/bins/*`, `crates/plugins/*` | 20+ crates with clear categorical buckets | large monorepos, plugin systems |
| **C. Nested sub-workspaces** | `vendor/<sub>/` with own `[workspace]` | Git submodule isolation (rare) | projects with vendored upstream workspaces |
| **D. Root package** | `[package]` at root + `crates/` | 2-3 crate workspaces with clear primary crate | small libs with a companion CLI |

Full copy-paste skeletons for each pattern: `references/workspace-layouts.md` and `examples/<pattern>-workspace.md`.

### Pattern A skeleton (the default)

```text
my-project/
├── Cargo.toml                      # virtual: [workspace] members = ["crates/*"]
└── crates/
    ├── core/                       # library
    │   ├── Cargo.toml              # [package] + version.workspace = true
    │   └── src/lib.rs
    ├── net/                        # library
    │   └── ...
    └── cli/                        # binary
        └── src/main.rs
```

```toml
# root Cargo.toml — virtual manifest
[workspace]
resolver = "3"
members = ["crates/*"]

[workspace.package]
edition = "2024"
version = "0.1.0"
license = "Apache-2.0"

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }   # pin once
my-core = { path = "crates/core" }                  # internal deps here
```

```toml
# crates/net/Cargo.toml
[package]
name = "my-net"
version.workspace = true               # inherits from [workspace.package]
edition.workspace = true

[dependencies]
serde.workspace = true                 # inherits from [workspace.dependencies]
my-core.workspace = true               # internal workspace dep
```

## The "mixed root package" anti-pattern

A common mistake from developers coming from Java/Maven or Python: putting a real `[package]` with substantial code at the workspace root **while also** having member crates.

```toml
# Cargo.toml — DON'T (anonymized from a real public crate)
[workspace]
members = ["codegen", "macro-driver", "example"]

[package]                            # ❌ root package + workspace together
name = "my_framework"
version = "4.9.6"

[dependencies]
my-codegen = { path = "codegen" }
my-macro-driver = { path = "macro-driver" }
```

```text
my-framework/
├── Cargo.toml                       # 163 lines mixing workspace + package config
├── src/                             # ❌ the root package's source pollutes the root
│   ├── lib.rs                       # 30 lines of `pub use *::*`
│   ├── crud.rs                      # 591 lines (monster file — see rust-module-layout)
│   ├── executor.rs                  # 642 lines
│   └── plugin/
├── codegen/                         # member crate
├── macro-driver/                    # member crate
└── tests/
```

**Five problems**: root pollution, asymmetric commands (`cargo build` builds only the root), coupled versioning, no clear facade (lib.rs becomes a glob re-export hub), and migration is a breaking change once published.

**Refactor target** — virtual manifest with all crates under `crates/`:

```text
my-framework/
├── Cargo.toml                       # virtual manifest — workspace config only
└── crates/
    ├── my-framework/                # was: src/ at root
    │   ├── Cargo.toml
    │   └── src/
    ├── codegen/
    ├── macro-driver/
    └── example/
```

Migration is **mechanical and preserves the published crate name** — full six-step procedure in `references/mixed-root-package-antipattern.md` and a worked example in `examples/migration-mixed-to-virtual.md`.

## Workspace-level shared configuration

Three workspace-level tables eliminate drift across members. See `references/workspace-dependencies.md` for the full syntax.

```toml
# root Cargo.toml
[workspace.package]                  # shared package metadata
version = "0.1.0"
edition = "2024"
rust-version = "1.85"
license = "Apache-2.0"

[workspace.dependencies]             # shared external + internal deps
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["rt-multi-thread", "macros"] }
my-core = { path = "crates/core" }

[workspace.lints.rust]               # shared lint config
unsafe_code = "forbid"
missing_docs = "warn"
```

Members opt in with `.workspace = true`:

```toml
# crates/net/Cargo.toml
[package]
name = "my-net"
version.workspace = true             # inherits 0.1.0
edition.workspace = true

[dependencies]
serde.workspace = true               # inherits pinned version + features
my-core.workspace = true

[lints]
workspace = true                     # inherits shared lints
```

## Dependency direction (DAG)

Crate dependencies form a **directed acyclic graph**. Cycles are forbidden (`cargo` will error). Plan direction deliberately.

```text
low-level types ──► domain logic ──► application ──► binary
   (my-types)         (my-core)         (my-server)     (my-cli)
```

**Anti-pattern — leaky direction**:

```toml
# crates/core/Cargo.toml — ❌ core depending on CLI concerns
[dependencies]
clap = "4"                           # CLI lib has no business in core
my-cli = { path = "../cli" }         # core cannot depend on the binary
```

**Verification**:

```bash
cargo tree                                    # visualize the dep graph
cargo tree --invert --package my-core         # what depends on my-core?
```

If `my-types` shows up as depending on anything non-`std`, the direction is wrong. Layering rules in `references/dependency-direction.md`.

## Reference example — `sa-token-rs` (11-crate virtual workspace)

[`sa-token-rs`](https://github.com/dromara/sa-token-rs) is a real-world Rust port of the Java Sa-Token permission framework — an exemplar of every pattern this skill teaches. Virtual manifest, 11 crates, clean 5-layer DAG, `crates/<category>/` grouping, full `[workspace.*]` inheritance.

### Layout (Pattern A + B hybrid)

```text
sa-token-rs/
├── Cargo.toml                          # virtual manifest
└── crates/
    ├── sa-token/                       # Layer 3: facade (public API)
    ├── sa-token-core/                  # Layer 1: core types & traits (no internal deps)
    ├── sa-token-derive/                # Layer 2: proc-macro (core only)
    ├── sa-token-context-mock/          # Layer 2: mock context (core only)
    ├── sa-token-dao-memory/            # Layer 2: memory DAO (core only)
    ├── sa-token-dao-redis/             # Layer 4: redis DAO (facade + core)
    ├── sa-token-axum/                  # Layer 4: axum adapter (facade + core)
    ├── sa-token-plugin/                # Pattern B grouping
    │   ├── sa-token-jwt/               # Layer 4: JWT plugin
    │   └── sa-token-sign/              # Layer 4: signature plugin
    ├── sa-token-demo/                  # Pattern B grouping
    │   └── sa-token-demo-axum/         # Layer 5: binary example
    └── sa-token-test/                  # Layer 5: integration tests
```

### DAG — 5 layers, every arrow points up

```text
L1  sa-token-core
      ▲
L2  sa-token-derive   sa-token-context-mock   sa-token-dao-memory
      ▲                      ▲                       ▲
L3  sa-token  (facade — aggregates L2 leaves into one public API)
      ▲
L4  sa-token-dao-redis   sa-token-axum   sa-token-jwt   sa-token-sign
      ▲
L5  sa-token-demo-axum   sa-token-test   (binaries + tests)
```

### Why it's exemplary

1. **Virtual manifest** — no root `[package]`; `cargo build` builds all 11 by default.
2. **Pattern A + B hybrid** — flat `crates/sa-token-*` for leaves, `crates/sa-token-plugin/` and `crates/sa-token-demo/` for grouped sub-crates.
3. **Full `[workspace.*]` inheritance** — `version`, `edition = "2024"`, `rust-version = "1.85"`, `license`, `repository`, `[workspace.lints]` (`unsafe_code = "forbid"`, `missing_docs = "warn"`, `clippy::pedantic = "warn"`), and `[workspace.dependencies]` for internal + external deps.
4. **Feature-gated optional dep** — `sa-token` exposes `redis = ["dep:sa-token-dao-redis"]`.
5. **Clean DAG** — core has zero internal deps; facade aggregates; adapters/plugins/DAOs sit on top; demos/tests consume everything.

See `references/sa-token-rs-case-study.md` for the full member-by-member Cargo.toml breakdown, DAG verification commands, and how the layout supports independent publishing.

## Workspace commands cheat sheet

```bash
cargo build --workspace               # build every member (default in virtual manifest)
cargo build -p my-core                # build one member
cargo test --workspace                # test every member
cargo check --workspace               # fast type-check everything
cargo doc --workspace --no-deps       # docs for every member
cargo publish -p my-core              # publish one member
cargo run -p my-cli                   # run a specific binary

cargo workspaces version minor       # bump all members in lockstep (needs cargo-workspaces)
cargo workspaces publish              # publish all members in topological order
```

For batch version bumps and publishes across all members, install [`cargo-workspaces`](https://crates.io/crates/cargo-workspaces).

---


## Workflow

1. **Decide project type** — single-crate (Section 8.1) or multi-crate workspace (Section 8.2)? Use the decision tree. When in doubt, start single-crate and graduate to a workspace when a real need appears (independent reuse, version divergence, dep isolation).
2. **For workspaces: choose a layout** — Pattern A (flat `crates/`) is the default. Use Pattern B (grouped) only if you have 20+ crates. Avoid Pattern D (root package) for new workspaces.
3. **Decide crate boundaries** — split only when at least one of the five conditions in the decision tree holds. Otherwise, use modules within a single crate (see `rust-module-layout`).
4. **Pin shared metadata and deps at workspace level** — `[workspace.package]`, `[workspace.dependencies]`, `[workspace.lints]`. Members opt in with `.workspace = true`.
5. **Verify dependency direction** — `cargo tree --invert --package my-core` must show only higher-level crates depending on lower-level ones. No reverse edges, no cycles.
6. **Select naming conventions** — snake_case crate names, kebab-case in `Cargo.toml` `name`. Use full words; avoid 2-letter abbreviations (see `rust-module-layout`'s naming reference).
7. **Validate** — `cargo check --workspace`, `cargo tree`, `cargo doc --workspace --no-deps`. Inspect the generated docs sidebar — it should reflect your intended public API surface.

## Gotchas

1. Distinguish between `crate::` (references the current crate root) and `::other_crate_name::` (absolute path reference to an external crate).
2. Restricted visibility such as `pub(crate)` is not an Edition boundary; verify the project's Rust version rather than assuming Edition 2015 forbids it.
3. Both `module.rs` and `module/mod.rs` are supported; new code typically prefers the former, but do not misinterpret a deprecated warning as an error for using `mod.rs`.
4. Workspace resolver settings apply globally; Edition 2021 defaults to resolver 2, while Edition 2024 defaults to resolver 3.
5. The path argument in `pub(in path)` must point to ancestor modules of the current item and cannot be used to expose visibility across arbitrary sibling modules.
6. Use of the `#[path]` attribute bypasses filesystem conventions — module paths no longer follow default file tree structures after application.
7. **A virtual manifest cannot contain `[dependencies]` or `[package]`.** If you see `failed to parse manifest at ... missing field package`, you've mixed virtual and root-package syntax. Either remove `[package]` (virtual) or add it (root package) — don't half-do both.
8. **`cargo build` at a root-package workspace only builds the root.** Use `--workspace` to build everything. With a virtual manifest, `cargo build` already builds all members — fewer surprises.
9. **`members = ["crates/*"]` globs match one level only.** For `crates/libs/core/`, use `members = ["crates/libs/*"]` (one glob per category) or list paths explicitly.
10. **Workspace-internal `path` deps still need versions for publish.** `my-core = { path = "../core", version = "0.1.0" }` — without `version`, `cargo publish` rejects it. Use `[workspace.dependencies]` to keep the version in one place.
11. **Bumping a workspace-shared dep requires editing only the root `Cargo.toml`.** Don't re-pin it in member crates — that defeats the purpose and creates drift.
12. **Renaming a published crate is a breaking change.** Add a deprecated alias crate (`pub use my_new_name::*;`) under the old name for one release cycle before removing it.

## On-Demand Resources

- [Layout Examples](examples/examples.md) — basic module layouts
- [Concept Quick Reference](references/references.md)
- [Workspace Layouts (4 patterns)](references/workspace-layouts.md) — flat, grouped, nested, root-package; with copy-paste skeletons
- [Virtual vs Root Manifest](references/virtual-vs-root-manifest.md) — the decision in depth, with command-ergonomics comparison
- [Mixed Root Package Anti-Pattern](references/mixed-root-package-antipattern.md) — full diagnosis + migration path for rbatis-style layouts
- [Workspace Dependencies](references/workspace-dependencies.md) — `[workspace.package]` / `[workspace.dependencies]` / `[workspace.lints]` in depth
- [Dependency Direction](references/dependency-direction.md) — DAG rules, layering, leaky direction anti-patterns
- [`sa-token-rs` Case Study](references/sa-token-rs-case-study.md) — real-world 11-crate virtual workspace with 5-layer DAG, full member-by-member breakdown, DAG verification, and publishing implications
- [Production-grade workspace boundaries](references/production-workspace-boundaries.md): When splitting protocols, domains, platforms, transports, SDKs, adapters, and binaries, read the relevant sections.
- `examples/golden-layout/`: single-crate CI compilation example
- `examples/golden-workspace/`: multi-crate virtual workspace example with three crates and a facade

## Official References

- [The Book ch 7 — Managing Growing Projects](https://doc.rust-lang.org/book/ch07-00-managing-growing-projects-with-packages-crates-and-modules.html)
- [The Book ch14-03 — Cargo Workspaces](https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html)
- [Rust Reference ch 7 (Items)](https://doc.rust-lang.org/reference/items.html)
- [Rust Reference ch 7.2 (Modules)](https://doc.rust-lang.org/reference/items/modules.html)
- [Cargo Book — Workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html)
- [Cargo Book — `workspace.package`](https://doc.rust-lang.org/cargo/reference/workspaces.html#the-package-table)
- [Cargo Book — Workspace dependencies](https://doc.rust-lang.org/cargo/reference/workspaces.html#the-dependencies-table)
- [RFC 1525 — Cargo Workspaces](https://rust-lang.github.io/rfcs/1525-cargo-workspace.html)
- [matklad — Large Rust Workspaces](https://matklad.github.io/2021/08/22/large-rust-workspaces.html) (community best-practice reference)
- [Rust API Guidelines — Organization (C-HIERARCHY, C-REEXPORT)](https://rust-lang.github.io/api-guidelines/about.html)
