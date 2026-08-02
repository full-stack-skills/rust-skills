# Workspace Dependencies — `[workspace.package]`, `[workspace.dependencies]`, `[workspace.lints]`

How to use the three workspace-level tables to eliminate version drift across member crates.

> Authority: [Cargo Book — Workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html).

---

## The Three Workspace Tables

| Table | Purpose |
|-------|---------|
| `[workspace.package]` | Shared package metadata (version, edition, license, authors, repository, etc.) |
| `[workspace.dependencies]` | Pinned external dependencies + internal workspace deps |
| `[workspace.lints]` | Shared lint configuration (rust, clippy) |

All three are inherited in member crates via the `.workspace = true` syntax.

---

## `[workspace.package]` — Shared Metadata

Define once at root:

```toml
# root Cargo.toml
[workspace.package]
version = "0.1.0"
edition = "2024"
rust-version = "1.85"
license = "Apache-2.0"
repository = "https://github.com/me/my-project"
homepage = "https://my-project.example.com"
authors = ["Me <me@example.com>"]
description = "A common description prefix"   # rarely shared; usually per-crate
```

Members opt in:

```toml
# crates/core/Cargo.toml
[package]
name = "my-core"
version.workspace = true
edition.workspace = true
rust-version.workspace = true
license.workspace = true
repository.workspace = true
homepage.workspace = true
authors.workspace = true
description = "my-core: the core domain types"   # override locally
```

### What you should and shouldn't share

| Field | Share? | Why |
|-------|--------|-----|
| `version` | **Share** | Lockstep versioning is the most common pattern |
| `edition` | **Share** | All members should be on the same edition |
| `rust-version` | **Share** | MSRV consistency |
| `license` | **Share** | All members typically under the same license |
| `repository` | **Share** | All live in the same repo |
| `homepage` | Share | If applicable |
| `authors` | Share | Usually the same team |
| `description` | Don't share | Each crate has its own purpose |
| `name` | Can't share | Always per-crate |
| `keywords`, `categories` | Don't share | Each crate has its own discovery profile |

### Independent versioning

If members need independent version trajectories (e.g., `my-plugin-jwt` is 0.1 while `my-core` is 1.5), don't share `version`:

```toml
# crates/core/Cargo.toml
[package]
name = "my-core"
version = "1.5.0"                # explicit, not inherited
edition.workspace = true
# ...
```

---

## `[workspace.dependencies]` — Pinned Deps

The single source of truth for external dependency versions. Members opt in with `dep.workspace = true`.

```toml
# root Cargo.toml
[workspace.dependencies]
# External
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tokio = { version = "1", features = ["rt-multi-thread", "macros", "net", "io-util"] }
anyhow = "1"
thiserror = "2"
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
chrono = { version = "0.4", default-features = false, features = ["clock", "std"] }
uuid = { version = "1", features = ["v4"] }
base64 = "0.22"
hex = "0.4"
sha2 = "0.10"
hmac = "0.12"
rand = "0.8"
regex = "1"
url = "2"
async-trait = "0.1"
futures = "0.3"

# Internal workspace deps
my-core = { path = "crates/core", version = "0.1.0" }
my-net = { path = "crates/net", version = "0.1.0" }
```

Members opt in:

```toml
# crates/net/Cargo.toml
[dependencies]
serde.workspace = true              # gets "1" + derive feature
serde_json.workspace = true
tokio.workspace = true
my-core.workspace = true            # internal dep
async-trait.workspace = true
```

### Why `[workspace.dependencies]` matters

Without it, members drift:

```toml
# ❌ Without workspace.dependencies — drift waiting to happen
# crates/core/Cargo.toml
serde = { version = "1.0.193", features = ["derive"] }

# crates/net/Cargo.toml
serde = { version = "1", features = ["derive"] }

# crates/cli/Cargo.toml
serde = "1.0"                       # oops, no derive feature
```

With it, one bump fixes all members:

```bash
# Bump serde 1.0.193 → 1.0.200 across all members
$EDITOR Cargo.toml                  # edit only the root
# change: serde = { version = "1.0.200", features = ["derive"] }
cargo update -p serde
```

### Internal workspace deps

List internal workspace deps in `[workspace.dependencies]` too, with both `path` AND `version`:

```toml
# root Cargo.toml
[workspace.dependencies]
my-core = { path = "crates/core", version = "0.1.0" }
```

The `path` is used during development; the `version` is what `cargo publish` records. **Without `version`, `cargo publish` rejects it.**

```toml
# crates/net/Cargo.toml
[dependencies]
my-core.workspace = true            # inherits both path and version
```

### Optional and feature overrides

Members can add `optional = true` or override features when needed:

```toml
# crates/cli/Cargo.toml
[dependencies]
serde.workspace = true
tracing = { workspace = true, optional = true }    # make it optional in this crate

[features]
trace-logs = ["dep:tracing"]
```

```toml
# crates/extra/Cargo.toml — add MORE features, can't remove
tokio = { workspace = true, features = ["fs"] }    # adds fs to the workspace's list
```

Note: you can only **add** features in members, not remove them. To have different feature sets per crate, define separate dep entries in the workspace (e.g., `serde-lite` and `serde-full`).

---

## `[workspace.lints]` — Shared Lint Config

```toml
# root Cargo.toml
[workspace.lints.rust]
unsafe_code = "forbid"
missing_docs = "warn"
rust_2024_compatibility = "warn"

[workspace.lints.clippy]
all = "warn"
pedantic = "warn"
nursery = "warn"
cargo = "warn"

# Specific Clippy overrides
[workspace.lints.clippy.pedantic]
must_use_candidate = "allow"        # too noisy
module_name_repetitions = "allow"   # we like descriptive names
```

Members opt in:

```toml
# crates/core/Cargo.toml
[lints]
workspace = true
```

### Per-crate overrides

A member can override a specific lint:

```toml
# crates/cli/Cargo.toml
[lints]
workspace = true

[lints.clippy]
pedantic = { level = "allow", priority = 1 }   # this crate opts out of pedantic
```

Or add to it:

```toml
[lints.clippy]
restriction = "warn"          # add restriction lints just for this crate
```

---

## `[profile]` is also workspace-level

Release profile belongs at root, not in members:

```toml
# root Cargo.toml
[profile.release]
lto = true
opt-level = 3
codegen-units = 1
strip = true

[profile.dev]
debug = "line-tables-only"     # faster dev builds
```

If you copy `[profile]` into a member's `Cargo.toml`, `cargo` errors. Keep profiles at root.

---

## A Realistic Workspace Root

Combining the shared-configuration patterns, here is a small root-flat virtual
workspace. Member placement remains independent of dependency inheritance.

```toml
# Cargo.toml — virtual manifest, all shared config here
[workspace]
resolver = "3"
members = ["my-core", "my-net", "my-db"]

[workspace.package]
version = "0.1.0"
edition = "2024"
rust-version = "1.85"
license = "Apache-2.0"
repository = "https://github.com/me/my-project"
homepage = "https://my-project.example.com"
authors = ["Me <me@example.com>"]

[workspace.dependencies]
# External
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tokio = { version = "1", features = ["rt-multi-thread", "macros", "net", "io-util"] }
anyhow = "1"
thiserror = "2"
tracing = "0.1"
async-trait = "0.1"
chrono = { version = "0.4", default-features = false, features = ["clock", "std"] }

# Internal
my-core = { path = "my-core", version = "0.1.0" }
my-net = { path = "my-net", version = "0.1.0" }
my-db = { path = "my-db", version = "0.1.0" }

[workspace.lints.rust]
unsafe_code = "forbid"
missing_docs = "warn"

[workspace.lints.clippy]
all = "warn"
pedantic = "warn"

[profile.release]
lto = true
codegen-units = 1
```

A typical member `Cargo.toml` becomes short:

```toml
# my-net/Cargo.toml — minimal, everything inherited
[package]
name = "my-net"
version.workspace = true
edition.workspace = true
rust-version.workspace = true
license.workspace = true
repository.workspace = true
authors.workspace = true
description = "Network primitives for my-project"

[dependencies]
serde.workspace = true
tokio.workspace = true
my-core.workspace = true
async-trait.workspace = true

[lints]
workspace = true
```

That's it. ~15 lines per member, down from ~50 with duplicated config.
