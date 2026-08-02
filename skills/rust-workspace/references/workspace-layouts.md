# Workspace Layout Patterns — Project-Driven Skeletons

Choose crate boundaries before choosing directories. The source repository's
Maven/Gradle modules, package count, or directory depth are evidence about the
domain, not a Cargo layout to copy mechanically. Authority: [Cargo Book —
Workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html) and
[matklad — Large Rust Workspaces](https://matklad.github.io/2021/08/22/large-rust-workspaces.html).

## Decision inputs

Record these before selecting a topology:

1. Resulting Rust packages and which ones are independently published.
2. Dependency, feature, target, `no_std`, proc-macro, and FFI boundaries.
3. Stable families such as adapters, plugins, bindings, examples, or tests.
4. Root-directory noise from documentation, tools, fixtures, or other languages.
5. Existing public paths, automation, and contributor expectations that a move
   would break.

Workspace member/package count is only a review trigger: 2-8 cohesive packages normally remain
root-flat; around 8-20 compare root-flat and hybrid layouts; 20+ commonly needs
grouping or a `crates/` container. Stronger project evidence overrides the count.

---

## Pattern A — Root-flat virtual workspace (small default)

**When**: a small, cohesive Rust-only workspace whose members are all useful to
see at a glance. This is the default for a newly derived 2-8 package workspace.

```text
my-project/
├── Cargo.toml
├── Cargo.lock
├── my-core/
│   ├── Cargo.toml
│   └── src/lib.rs
├── my-net/
│   ├── Cargo.toml
│   └── src/lib.rs
└── my-cli/
    ├── Cargo.toml
    └── src/main.rs
```

```toml
[workspace]
resolver = "3"
members = ["my-core", "my-net", "my-cli"]

[workspace.package]
version = "0.1.0"
edition = "2024"
rust-version = "1.85"
license = "Apache-2.0"

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
my-core = { path = "my-core" }
my-net = { path = "my-net" }
```

**Pros**: `ls` exposes the product's packages immediately; member paths are
short; adding a small integration-test package is unsurprising.

**Watch**: use explicit member names. `members = ["*"]` also matches unrelated
top-level directories containing manifests and is too broad.

---

## Pattern B — Hybrid or domain-grouped workspace

**When**: core packages still deserve top-level visibility, while one or more
real families would otherwise flood the root. Group by domain or lifecycle, not
by a generic desire for symmetry.

```text
my-project/
├── Cargo.toml
├── my-core/
├── my-api/
├── my-test/
├── support/
│   ├── my-axum/
│   └── my-wasm/
└── examples/
    ├── hello-world/
    └── web-demo/
```

```toml
[workspace]
resolver = "3"
members = [
    "my-core",
    "my-api",
    "my-test",
    "support/*",
    "examples/*",
]
```

**Pros**: preserves discoverable core crates while containing repetitive
adapters/examples. It supports gradual growth without a repository-wide move.

**Watch**: each glob matches one level only. Do not invent `libs/`, `modules/`,
or `packages/` buckets if the project has no corresponding conceptual family.

---

## Pattern C — Contained or grouped `crates/` workspace

**When**: many Rust packages, a multi-language repository, a crowded root, or a
clear need to separate Cargo members from documentation, tooling, datasets, and
other products. `crates/` is a valid Rust convention; it is not the universal
default and it is not a Java/Maven requirement.

```text
my-project/
├── Cargo.toml
├── docs/
├── tooling/
└── crates/
    ├── core/
    │   ├── Cargo.toml
    │   └── src/lib.rs
    ├── adapters/
    │   ├── axum/
    │   └── wasm/
    ├── bindings/
    │   └── python/
    └── tests/
        └── my-project-test/
```

```toml
[workspace]
resolver = "3"
members = [
    "crates/core",
    "crates/adapters/*",
    "crates/bindings/*",
    "crates/tests/*",
]
```

**Pros**: keeps a large or multi-language root legible and scales with stable
families. **Cons**: adds path depth and hides small workspaces behind an
unnecessary container when adopted too early.

---

## Pattern D — Nested sub-workspaces (rare)

**When**: a vendored upstream repository or Git submodule must retain its own
workspace and lockfile.

```text
my-project/
├── Cargo.toml
├── my-core/
└── vendor/
    └── upstream-lib/
        ├── Cargo.toml
        └── crates/
```

```toml
[workspace]
resolver = "3"
members = ["my-core"]
exclude = ["vendor/upstream-lib"]
```

Avoid this unless independent upstream ownership requires it; Cargo workspace
nesting adds operational complexity.

---

## Pattern E — Root package workspace (small and intentional)

**When**: two or three packages, one package is unequivocally the main
published library/application, and root-package command asymmetry is useful or
accepted.

```text
my-project/
├── Cargo.toml              # [workspace] + [package]
├── src/lib.rs              # primary package
└── my-cli/
    ├── Cargo.toml
    └── src/main.rs
```

```toml
[workspace]
resolver = "3"
members = ["my-cli"]

[package]
name = "my-project"
version = "0.1.0"
edition = "2024"
```

Root package and root-flat member location are independent decisions. A small
virtual workspace may be root-flat without having a root package. Avoid a root
package once its dual role makes commands, publishing, or root ownership
ambiguous; see `mixed-root-package-antipattern.md`.

---

## Migration-project examples

| Resulting Rust product | Recommended topology | Reason |
|------------------------|----------------------|--------|
| Core library + whole-project tests + one language binding | Root-flat | Few cohesive publish/test units; all are immediately discoverable |
| Core + tests + several framework adapters | Hybrid | Core stays visible; adapter family is contained |
| Dozens of format/protocol modules, demos, bindings, and test infrastructure | Hybrid or contained/grouped | Root noise and stable families justify collection |
| Multi-language monorepo with a Rust product | Rust-specific container, then apply A/B/C inside it | Language ownership is clearer than a repository-wide flat list |

Do not equate a Java module with a Rust package. Merge source modules that have
no independent Rust boundary, and split a source module when Rust target,
publishing, proc-macro, FFI, or dependency isolation requires it.

## Decision summary

| Situation | Start with |
|-----------|------------|
| One cohesive package | Single package, no workspace |
| 2-8 cohesive packages | A: root-flat virtual |
| Growing project with real adapter/example/test families | B: hybrid/domain-grouped |
| Large, root-heavy, or multi-language repository | C: contained/grouped |
| Independently owned vendored workspace | D: nested/excluded |
| 2-3 packages with one intentional root package | E: root package |

Record the selected topology and rejected alternatives in the architecture or
migration roadmap. Revisit it when the project crosses a boundary, not merely
when an arbitrary workspace member count changes.
