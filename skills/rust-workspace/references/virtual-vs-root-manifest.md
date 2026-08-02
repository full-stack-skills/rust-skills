# Virtual Manifest vs Root Package — In Depth

The decision between a **virtual manifest** and a **root package** is the single most important workspace decision. This reference expands on SKILL.md with the full trade-off matrix and command-ergonomics comparison.

> Authority: [Cargo Book — Workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html), [Cargo issue #3526](https://github.com/rust-lang/cargo/issues/3526) (mixed manifests accepted), [matklad — Large Rust Workspaces](https://matklad.github.io/2021/08/22/large-rust-workspaces.html).

---

## Definitions

| Term | Definition |
|------|-----------|
| **Virtual manifest** | A root `Cargo.toml` containing `[workspace]` but **no `[package]`**. The root is purely organizational. |
| **Root package** | A root `Cargo.toml` containing **both** `[workspace]` **and** `[package]`. The root is both the workspace organizer and one of the crates. |
| **Workspace root** | The directory containing the top-level `Cargo.toml`. Always exists. |
| **Root crate** | The crate whose source lives at the workspace root (`<root>/src/`). Only exists with a root package. |

---

## Virtual Manifest — the recommended default

```toml
# Cargo.toml — virtual manifest
[workspace]
resolver = "3"
members = ["my-core", "my-cli"]

[workspace.package]
version = "0.1.0"
edition = "2024"

[workspace.dependencies]
# ... shared deps
```

```text
my-project/
├── Cargo.toml              # virtual — no src/ here
├── my-core/
│   └── src/lib.rs
└── my-cli/
    └── src/main.rs
```

### Behavior

| Command | What it does |
|---------|-------------|
| `cargo build` | Builds **all** members |
| `cargo build -p my-core` | Builds one member |
| `cargo run` | ❌ Errors — no root package to run |
| `cargo run -p my-cli` | Runs one binary |
| `cargo test` | Tests **all** members |
| `cargo doc` | Documents **all** members |
| `cargo publish` | ❌ Errors — nothing to publish at root; use `-p <name>` |

### Why it's preferred

1. **Clean root**: no `src/`, `tests/`, `benches/` cluttering the top level alongside the workspace's organizational files.
2. **Symmetric commands**: `cargo build` / `test` / `doc` act on all members uniformly. No `--workspace` flag needed.
3. **Clear separation**: the root is unambiguously "the workspace", and each crate is unambiguously "a crate". New contributors don't get confused about what's what.
4. **Easier extraction**: each member already owns a manifest and public boundary; move its selected member directory and update paths.
5. **Easier publishing**: each member is published independently with `cargo publish -p <name>`. No special handling for the root.

### Downsides (minor)

1. To run a binary, you must specify `-p my-cli` (no default).
2. `cargo run` at root errors. Use `cargo run -p <bin-name>`.

---

## Root Package — acceptable for small workspaces only

```toml
# Cargo.toml — root package
[workspace]
resolver = "3"
members = ["my-cli"]

[package]                   # the root package
name = "my_main_lib"
version = "0.1.0"
edition = "2024"

[dependencies]
# ... root package deps
```

```text
my-project/
├── Cargo.toml              # [workspace] + [package]
├── src/                    # root package source — at the top level
│   └── lib.rs
├── tests/                  # root package tests
├── benches/                # root package benchmarks
└── my-cli/
    └── src/main.rs
```

### Behavior

| Command | What it does |
|---------|-------------|
| `cargo build` | Builds **only the root package** ⚠️ |
| `cargo build --workspace` | Builds all members |
| `cargo run` | Runs the root package's binary (if any) |
| `cargo test` | Tests **only the root package** ⚠️ |
| `cargo test --workspace` | Tests all members |
| `cargo publish` | Publishes the root package |
| `cargo publish -p my-cli` | Publishes a member |

### Why it's problematic at scale

1. **Root pollution**: `src/`, `tests/`, `benches/` sit alongside `crates/` and other workspace organizational files. Confusing for newcomers.
2. **Asymmetric commands**: `cargo build` builds only the root; you must remember `--workspace` for everything else. This trips up CI configs and new contributors constantly.
3. **Publishing coupling**: if the root package depends on path members, you must publish members **first**, then the root. Forgetting the order causes publish failures.
4. **Two roles for one file**: the root `Cargo.toml` is both the workspace config AND a package config. It grows long and conflates concerns.
5. **Migration is breaking**: once published, moving the root package into a member directory changes repository paths. Users with `path = ""` references break.

### When it's acceptable

- 2-3 package workspace
- One package is unambiguously the primary entry point (e.g., the main library)
- The root package has a focused role; most other concerns live in members

Substantial root code is a review signal, not a LOC cutoff. Prefer a virtual
manifest when root ownership, default command scope, publishing order, or path
compatibility becomes ambiguous. See `mixed-root-package-antipattern.md`.

---

## Command Ergonomics — Side by Side

| Operation | Virtual manifest | Root package |
|-----------|------------------|--------------|
| `cargo build` (no args) | All members | Root only |
| `cargo build --workspace` | All members | All members |
| `cargo build -p foo` | One member | One member |
| `cargo run` (no args) | ❌ error | Runs root's bin |
| `cargo run -p foo` | One binary | One binary |
| `cargo test` (no args) | All members | Root only |
| `cargo test --workspace` | All members | All members |
| `cargo doc` (no args) | All members | Root only |
| `cargo publish` (no args) | ❌ error | Publishes root |
| `cargo publish -p foo` | One member | One member |

**Pattern**: virtual manifest makes `--workspace` the default, which is what you usually want. Root package makes `-p` the default for the root, which is rarely what you want at workspace scale.

---

## The Mixed Manifest Anti-Pattern

A root package + members where the root package has substantial code is the worst case. See `mixed-root-package-antipattern.md` for diagnosis and migration.

---

## Cargo's Acceptance

[Cargo issue #3526](https://github.com/rust-lang/cargo/issues/3526) established that modern Cargo accepts both `[package]` + `[workspace]` in the same manifest (the root package pattern). It's fully supported — just not always wise. The Cargo team's official docs describe both flavors without taking a stance; the virtual-manifest preference is a community best-practice articulated most clearly by matklad.

---

## Decision Summary

| Question | If yes |
|----------|--------|
| Is the product just 1 package? | Single package, no workspace needed |
| Does the workspace have 2-3 packages with one clearly primary? | Root package acceptable |
| Does the workspace have 4+ packages or no uniquely primary root package? | Prefer a **virtual manifest**; document any exception |
| Does root code make ownership, commands, publishing, or paths ambiguous? | Prefer a **virtual manifest** |
| Are you migrating from a Java/Python project where you put everything at the root? | **Virtual manifest** (you have the mixed anti-pattern) |

When in doubt: virtual manifest.

This decision is independent of member placement. A virtual workspace can be
root-flat, hybrid/domain-grouped, or contained under `crates/`; select that
topology separately using `workspace-layouts.md`.
