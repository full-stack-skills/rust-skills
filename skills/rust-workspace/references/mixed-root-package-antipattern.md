# The Mixed Root Package Anti-Pattern — Full Diagnosis and Migration

The most common structural mistake in Rust workspaces, especially from developers coming from Java/Maven or Python. This reference expands on SKILL.md with the full six-step migration procedure.

> All examples are anonymized composites drawn from real public crates.

---

## What is the anti-pattern?

A **mixed root package** is a `Cargo.toml` that contains **both** `[workspace]` and `[package]` tables **while the root package has substantial source code at `<root>/src/`** alongside member crates in subdirectories.

```toml
# Cargo.toml — the anti-pattern
[workspace]
members = ["codegen", "macro-driver", "example"]

[package]                            # ❌ root package + workspace together
name = "my_framework"
version = "4.9.6"
description = "..."
authors = ["..."]
edition = "2021"

[features]
# ... 5 features

[dependencies]
my-codegen = { path = "codegen" }
my-macro-driver = { path = "macro-driver" }
dark-std = "0.2"
async-trait = "0.1"
serde = "1"
log = "0.4"
futures-core = "0.3"
hex = "0.4"
rand = "0.10"
parking_lot = "0.12.3"

[dev-dependencies]
serde_json = "1"
tokio = { version = "1", features = ["full"] }

[profile.release]
lto = true
opt-level = 3
codegen-units = 1
```

```text
my-framework/
├── Cargo.toml                       # 163 lines mixing workspace + package config
├── src/                             # ❌ root package source pollutes the root
│   ├── lib.rs                       #   30 lines of `pub use *::*` re-exports
│   ├── crud.rs                      #  591 lines (monster file — see rust-module-layout)
│   ├── crud_traits.rs               #  ...
│   ├── decode.rs                    #   77 lines
│   ├── error.rs                     #   ...
│   ├── executor.rs                  #  642 lines
│   ├── rbatis.rs                    #  ...
│   ├── utils/                       #   module directory
│   │   ├── mod.rs
│   │   ├── impled.rs
│   │   └── table_util.rs
│   └── plugin/                      #   module directory
│       ├── mod.rs
│       ├── page.rs
│       ├── id_generator/
│       │   └── snowflake.rs
│       ├── intercept/
│       │   ├── mod.rs
│       │   ├── intercept_page.rs
│       │   └── intercept_log.rs
│       └── table_sync/
│           ├── mod.rs
│           ├── deprecated.rs
│           └── rbdc_mapper.rs
├── codegen/                         # member crate
│   ├── Cargo.toml
│   └── src/
├── macro-driver/                    # member crate
│   ├── Cargo.toml
│   └── src/
├── example/                         # member crate (binary)
├── tests/
├── benches/
├── logo.png
├── README.md
├── README_CN.md
├── LICENSE
└── test.sh
```

---

## Five problems

### 1. Root pollution

`src/` at the top level mixes the framework's source with the workspace's organizational files. A newcomer `ls`-ing the directory sees `src/` (one specific crate's source), `codegen/` (another crate), `tests/` (yet another concern), `benches/`, `example/`, etc. — all jumbled together. There's no visual separation between "the workspace" and "the main crate".

### 2. Asymmetric commands

```bash
cargo build              # builds only my_framework (the root package)
cargo build --workspace  # builds everything
```

CI configs that forget `--workspace` silently under-build. New contributors assume `cargo build` builds everything and miss bugs in member crates.

### 3. Coupled versioning

The root package depends on members via `path = "codegen"`. They have separate version numbers (`my_framework` is 4.9.6, `codegen` is 4.9). To release:

1. Publish `codegen` 4.9.x first
2. Update `my_framework`'s dependency on `codegen` to the new version
3. Publish `my_framework` 4.9.6

Forget the order → publish fails. Use `cargo-workspaces` to automate, but the friction is real.

### 4. No clear facade

`src/lib.rs` becomes a 30-line `pub use *::*` index page:

```rust
// src/lib.rs — the flat-lib.rs anti-pattern from rust-module-layout
pub extern crate dark_std;
pub extern crate rbatis_codegen;
extern crate rbatis_macro_driver;
pub extern crate rbdc;

pub use rbatis_macro_driver::{html_sql, py_sql, snake_name, sql};

pub mod plugin;
pub mod rbatis;
#[macro_use]
pub mod utils;
pub mod executor;
#[macro_use]
pub mod crud;
#[macro_use]
pub mod error;
pub mod crud_traits;
pub mod decode;

pub use async_trait::async_trait;
pub use decode::*;
pub use error::*;
pub use executor::*;
pub use plugin::*;
pub use rbatis::*;
```

Every symbol dumps into the crate root. Provenance is lost; IDE completion is noisy. See `rust-module-layout` for the targeted facade fix.

### 5. Hard to split later

Once the root package is published with `<root>/src/` at this path, moving it to another member directory is a breaking change for any user who depends on the `path` structure (rare, but exists in private monorepos). Cargo publishing does not care about the repository path, but custom build scripts, IDE configuration, and private path dependencies might.

---

## Migration — six-step contained-layout example

First use `workspace-layouts.md` to select a target topology. A small workspace
may move the package to `<root>/my-framework/`; a growing workspace may use a
hybrid family; a large or root-heavy workspace may use
`<root>/crates/my-framework/`. The example below assumes the last case because
the diagnosed repository is already large. Adapt every path consistently; do
not introduce `crates/` merely because this example uses it.

The package-name/API migration is mechanical, but repository path consumers
must still be checked.

### Step 1 — Create the target directory

```bash
mkdir -p crates/my-framework
```

### Step 2 — Move source

```bash
git mv src crates/my-framework/src
git mv tests crates/my-framework/tests        # if tests/ belongs to the root package
git mv benches crates/my-framework/benches    # ditto
```

⚠️ **Be careful with `tests/`**: in some repos it contains workspace-wide integration tests, not just the root package's. Move only the root package's tests. If unsure, leave `tests/` at root for now.

### Step 3 — Create the new member `Cargo.toml`

```toml
# crates/my-framework/Cargo.toml
[package]
name = "my_framework"           # KEEP THE SAME NAME — no downstream breakage
version = "4.9.6"               # preserve version
description = "..."
authors = ["..."]
edition = "2021"
license = "Apache-2.0"
repository = "..."
documentation = "..."

[features]
# ... copy from root

[dependencies]
my-codegen = { path = "../codegen", version = "4.9" }    # note: ../codegen now
my-macro-driver = { path = "../macro-driver", version = "4.9", default-features = false, optional = true }
dark-std = "0.2"
async-trait = "0.1"
serde = "1"
# ... copy all deps from root

[dev-dependencies]
# ... copy

[profile.release]
# NOTE: [profile] is workspace-level — move to root, not member
```

⚠️ **Update `path` references**: `"codegen"` becomes `"../codegen"` (the member is now one level deeper).

### Step 4 — Rewrite root `Cargo.toml` as a virtual manifest

```toml
# root Cargo.toml — now a virtual manifest
[workspace]
resolver = "3"
members = [
    "crates/my-framework",
    "crates/codegen",
    "crates/macro-driver",
    "crates/example",
]

[workspace.package]
version = "4.9.6"               # if you want all members to share
edition = "2024"
license = "Apache-2.0"
repository = "..."

[workspace.dependencies]
# Pin shared external deps once
serde = "1"
async-trait = "0.1"
tokio = { version = "1", features = ["full"] }

# Internal deps
my-framework = { path = "crates/my-framework", version = "4.9.6" }
my-codegen = { path = "crates/codegen", version = "4.9" }
my-macro-driver = { path = "crates/macro-driver", version = "4.9" }

[workspace.lints.rust]
unsafe_code = "forbid"

[profile.release]
lto = true
opt-level = 3
codegen-units = 1
```

### Step 5 — Move member crates into the selected topology

```bash
git mv codegen crates/codegen
git mv macro-driver crates/macro-driver
git mv example crates/example
```

Update each member's `[package]` section to use `version.workspace = true`, `edition.workspace = true`, etc., and update their internal `path` references (now all relative to `crates/`):

```toml
# crates/codegen/Cargo.toml
[package]
name = "my-codegen"
version.workspace = true
edition.workspace = true

[dependencies]
# paths now go up one level then across
my-macro-driver = { path = "../macro-driver", version = "4.9" }
```

### Step 6 — Verify

```bash
cargo check --workspace           # compiles
cargo test --workspace            # all tests pass
cargo doc --workspace --no-deps   # docs build
cargo tree | head -40             # sanity-check the dep graph
```

The published crate name (`my_framework`) is unchanged. Downstream users see zero difference. Your repo is now a clean virtual workspace.

---

## Post-migration cleanup

Once the migration is done, take the opportunity to fix the **flat lib.rs anti-pattern** inside the new `crates/my-framework/src/lib.rs`. Replace `pub use *::*` with targeted re-exports. See `rust-module-layout/references/refactoring-flat-lib-rs.md`.

---

## Common Pitfalls

### Pitfall 1 — `path` references break

Any `path = "src/foo"` in build scripts or examples needs updating to `path = "crates/my-framework/src/foo"`. Run `cargo check --workspace` to catch them.

### Pitfall 2 — `[profile.release]` doesn't work in member `Cargo.toml`

Profiles are workspace-level. Keep them in root. If you copy them into a member, `cargo` errors.

### Pitfall 3 — `edition = "2021"` vs `"2024"`

This is a good time to bump edition if you've been meaning to. Set `edition = "2024"` in `[workspace.package]` and inherit everywhere.

### Pitfall 4 — tests/ ambiguity

If `tests/` contains workspace-wide integration tests (testing the combination of members), leave it at root. If it only tests the root package, move it with the package.

### Pitfall 5 — benches/ and examples/

Same as tests. Move if package-specific; keep at root if workspace-wide.

---

## Verification Checklist

- [ ] `cargo check --workspace` passes
- [ ] `cargo test --workspace` passes
- [ ] `cargo doc --workspace --no-deps` builds
- [ ] No `src/` at the workspace root
- [ ] Root `Cargo.toml` is a pure virtual manifest (no `[package]`, no `[dependencies]`)
- [ ] All members follow the recorded root-flat, hybrid, or contained topology
- [ ] Internal `path` references all use `../<sibling>` form
- [ ] `[profile]` settings live at root, not in members
- [ ] Published crate name unchanged
- [ ] CHANGELOG documents the repo restructure (note: this is NOT a breaking API change)
