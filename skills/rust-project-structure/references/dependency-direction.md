# Dependency Direction — DAG Rules and Layering

Crate dependencies form a **directed acyclic graph (DAG)**. Cargo forbids cycles (`error: cyclic package dependency detected`). This reference expands on SKILL.md with concrete layering rules for common project types.

---

## The Universal Rule

**Lower-level crates must not depend on higher-level crates.**

```text
low-level ──► high-level
   A ────────► B ────────► C
```

- A can depend on std only
- B can depend on A and std
- C can depend on A, B, and std
- **C cannot depend back on B or A in a way that creates a cycle**

---

## Generic Layering

For most projects:

```text
types / primitives ───► core / domain ───► application ───► binary
   (no deps)            (depends on types)   (depends on core)  (depends on app)
```

### Example

```text
my-types ────────► my-core ────────► my-server ────────► my-cli
                                                     └─► my-server-gui (alternate bin)
```

- `my-types`: pure data structures, no deps beyond std
- `my-core`: domain logic, depends on `my-types`
- `my-server`: application layer, depends on `my-core` + `my-types`
- `my-cli`: binary entry point, depends on `my-server`
- `my-server-gui`: alternate binary, also depends on `my-server`

`cargo tree --invert --package my-types` should show every crate in the workspace. `cargo tree --invert --package my-cli` should show only itself.

---

## Layering for Protocol-Heavy Projects (client/server SDK)

For projects with both wire protocol and domain logic:

```text
types ──► proto ──► core ──► sdk ──► client
                  │                  ╰─► server ──► server-bin
                  ╰─► os/pty ──► server
```

| Layer | Contents | Allowed deps |
|-------|----------|-------------|
| `types` | Platform-neutral value types, error enums | std only |
| `proto` | Wire DTOs, version tags, frame formats, serialization | types, serde |
| `core` | Pure domain model, business rules | types, proto |
| `os` / `pty` | Platform-specific (`cfg`), unsafe, handles | types |
| `sdk` | Stable client facade, handles | core, proto |
| `server` | Concurrent state, I/O lifecycles | core, proto, os, pty |
| `server-bin` | Process entrypoint, config | server |

Rules:
- **`types` contains no logic** — just data.
- **`proto` contains no business logic** — just wire format.
- **`core` has no I/O** — pure functions and types.
- **`sdk` exposes stable handles** — no internal transports leak.
- **The binary is responsible for composition** — wiring crates together at startup.

---

## Layering for Plugin Architectures

For projects with a core library and plugins:

```text
core ──► plugin-api ──► { plugin-jwt, plugin-redis, plugin-memory }
   ╰────────────────────────────► main-app
```

- `core`: framework primitives
- `plugin-api`: trait definitions plugins must implement
- `plugin-jwt`, `plugin-redis`, etc.: independent plugin crates
- `main-app`: the application that uses `core` and optionally pulls in plugins

**Plugins must not depend on each other**. Each is independently useful and independently versioned.

---

## Layering for Database Drivers (like rbdc)

For projects with a database driver abstraction and concrete drivers:

```text
driver-core (traits) ──► { driver-mysql, driver-pg, driver-sqlite, ... }
                                ╲
                                 ╲──► orm (uses driver-core, may use specific drivers optionally)
```

- `driver-core`: the `Driver`, `Connection`, `Pool` traits
- `driver-mysql`, `driver-pg`, etc.: concrete implementations behind feature flags
- `orm`: the user-facing library that depends on `driver-core` and optionally on specific drivers

**Drivers should not depend on the ORM** — that's a reverse dependency. The ORM depends on the driver trait crate; users opt into specific drivers via features.

---

## Anti-Patterns

### Anti-pattern 1 — Cycle

```text
my-core ─────► my-cli
   ▲              │
   └──────────────┘   ❌ cargo will reject with "cyclic package dependency"
```

Fix: extract the shared concern into a lower crate that both can depend on.

### Anti-pattern 2 — Leaky direction

```toml
# crates/core/Cargo.toml — ❌ core depending on CLI concerns
[dependencies]
clap = "4"                       # CLI lib has no business in core
my-cli = { path = "../cli" }     # core cannot depend on the binary
```

Cargo won't always reject this (no cycle), but it's structurally wrong. `core` now carries `clap` as a transitive dep everywhere it's used. Fix: move the CLI logic into `my-cli`.

### Anti-pattern 3 — God crate

```text
my-everything ──► { my-net, my-db, my-cli, my-server }
```

One crate depends on everything. Usually happens when `my-everything` is a "convenience" crate that re-exports everything. Use a thin facade crate (`my-prelude`) that depends on the others but exposes only the curated API. Don't put logic in it.

### Anti-pattern 4 — Hidden transitive deps

```toml
# crates/server/Cargo.toml
[dependencies]
my-core = { path = "../core" }
# server uses serde directly but doesn't declare it
```

If `my-core` re-exports types from `serde`, `server` can use them via `my-core::Ser` — but if `my-core` ever stops re-exporting, `server` breaks. **Always declare direct deps explicitly.** Don't rely on transitive exports.

---

## Verification

```bash
# Visualize the dep graph
cargo tree

# Reverse — what depends on X?
cargo tree --invert --package my-core

# Find duplicate dep versions
cargo tree --duplicates

# Audit dep licenses and bans
cargo install cargo-deny
cargo deny check
```

### Verification checklist

- [ ] `cargo tree --invert --package <types-crate>` shows every crate (everyone depends on types)
- [ ] `cargo tree --invert --package <binary-crate>` shows only itself (nothing depends on binaries)
- [ ] No "cyclic package dependency" errors
- [ ] No reverse dependencies from low-level to high-level
- [ ] `cargo tree --duplicates` shows minimal duplication (some is unavoidable)

---

## Tooling: `cargo-deny`

For enforcing dependency direction and license/security policies:

```toml
# deny.toml at workspace root
[advisories]
db-urls = ["https://github.com/rustsec/advisory-db"]
vulnerability = "deny"
unmaintained = "workspace"
unsound = "workspace"

[licenses]
allow = ["MIT", "Apache-2.0", "BSD-3-Clause", "ISC"]
confidence-threshold = 0.8

[bans]
# Ban specific crates
deny = [
    { name = "openssl", use-instead = "rustls" },
]

# Detect duplicate versions
multiple-versions = "warn"
```

```bash
cargo install cargo-deny
cargo deny check
```

CI integration: run `cargo deny check` on every PR.
