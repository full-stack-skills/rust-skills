# Cargo Book Reference Cheatsheet

Deep-dive reference for advanced Cargo Book topics that go beyond the manifest fundamentals covered elsewhere. Each section maps to a [Cargo Reference](https://doc.rust-lang.org/cargo/reference/) chapter and includes the exact TOML shape, semantics, gotchas, and validation commands. Versions and field names are aligned with recent stable Cargo; verify any field that has a version gate against the toolchain in the target project via `cargo --version` and the official reference before relying on it.

## 1. `[lints]` Table (rust + clippy, Workspace Inheritance)

The `[lints]` table declares rustc and Clippy lint levels in `Cargo.toml` itself, so lint policy travels with the source tree rather than living only in `.clippy.toml` or CI flags. Supported on Cargo 1.74+; on older toolchains it is silently ignored, so always cross-check `package.rust-version`.

### Standalone crate

```toml
[lints.rust]
unsafe_code = "forbid"
missing_docs = "warn"
rust_2018_idioms = "warn"

[lints.clippy]
all = "warn"
pedantic = "warn"
dbg_macro = "deny"
```

- Levels: `"forbid"`, `"deny"`, `"warn"`, `"allow"`.
- Tool key is one of `rust` or `clippy`. The lint name drops the `clippy::` prefix.
- `[lints]` is **not** a free-form table — unknown lint names cause Cargo to error on load.

### Workspace inheritance

Define the canonical policy once at the workspace root, then opt-in from each member:

```toml
# Root Cargo.toml (workspace)
[workspace.lints.rust]
unsafe_code = "forbid"

[workspace.lints.clippy]
all = { level = "warn", priority = -1 }   # base layer
pedantic = "warn"

# Member Cargo.toml
[lints]
workspace = true
```

`priority` (integer, default 0) controls layering when both `[workspace.lints]` and member-specific `[lints]` apply — higher priority wins. Use `priority = -1` for broad base rules (like `clippy::all`) so narrower specific rules override them.

### Gotchas

- Cargo's `[lints]` is applied to `cargo check`, `cargo build`, `cargo test`, and `cargo clippy` via `RUSTFLAGS`. It is **not** a replacement for `clippy::` attributes inside source, only an out-of-source declaration.
- When a member sets `[lints] workspace = true`, it inherits the *whole* workspace table; per-member overrides still layer on top by lint name + priority.
- If `[lints]` is set but the toolchain is older than 1.74, no error is raised — the policy simply does not apply. Pin `rust-version = "1.74"` or higher in those crates.

## 2. `[build-dependencies]` vs `[dependencies]`

Cargo distinguishes four dependency scopes; choosing the wrong one causes link errors, doubled compile times, or surprise dev-only behavior in production.

| Table | Used by | Typical examples |
|---|---|---|
| `[dependencies]` | lib/bin targets at build time and runtime | `serde`, `tokio`, `reqwest` |
| `[dev-dependencies]` | tests, examples, benches only; not compiled into released artifacts | `proptest`, `mockall`, `pretty_assertions` |
| `[build-dependencies]` | `build.rs` only; not linked into the final artifact | `prost-build`, `bindgen`, `cc` |
| `[target.<cfg>.dependencies]` | target-scoped `[dependencies]` | `windows-sys` on `cfg(windows)` |

```toml
[dependencies]
serde = { version = "1", features = ["derive"] }

[dev-dependencies]
pretty_assertions = "1"

[build-dependencies]
prost-build = "0.13"
```

### Rules

- `[build-dependencies]` are built for the **host** triple, not the target triple — critical during cross-compilation. A `build.rs` that links native code via `cc` must use a build-dependency that supports host/target separation.
- The same crate name may appear in both `[dependencies]` and `[build-dependencies]` (e.g., `serde`); they are independent compilations and will not share types across the boundary. Do not assume `pub` items from `[dependencies]` are visible to `build.rs`.
- `[dev-dependencies]` cannot be used by a `build.rs`. If `build.rs` needs `tempfile`, declare it under `[build-dependencies]`.
- Optional build-deps are allowed: `[build-dependencies] bindgen = { version = "0.70", optional = true }`, gated by a feature in `[features]`.

### Gotcha

Avoid naming a regular dependency and a build dependency the same *if* you also expect them to share types or version resolution. They will resolve independently, and a version skew between the two will silently produce duplicate compilations. Inspect with:

```bash
cargo tree -e build
cargo tree -e normal
```

## 3. `.cargo/config.toml` Sections

Lives at `.cargo/config.toml` (or `config`) in the workspace root, any ancestor directory, or `$CARGO_HOME/config.toml`. Cargo merges these with the closer-to-cwd file taking precedence. The full schema is in the [Configuration Reference](https://doc.rust-lang.org/cargo/reference/config.html).

### `[build]`

Controls global build behavior.

```toml
[build]
jobs = 8                       # parallel jobs; default = num CPUs
target-dir = "target"          # absolute or workspace-relative
rustflags = ["-W", "unused"]   # appended to every rustc invocation
rustdocflags = ["-D", "warnings"]
incremental = true             # dev only; rarely useful in CI
```

### `[target.<triple>]` and `[target.'cfg(...)']`

Target-specific settings, applied only when building for that triple or matching the cfg predicate.

```toml
[target.x86_64-unknown-linux-gnu]
linker = "clang"
rustflags = ["-C", "link-arg=-fuse-ld=lld"]

[target.aarch64-apple-darwin]
rustflags = ["-C", "link-arg=-arch", "-C", "link-arg=arm64"]

[target.'cfg(target_os = "linux")']
rustflags = ["-C", "link-arg=--no-undefined"]

[target.wasm32-unknown-unknown]
runner = "node"                # used by `cargo run` and `cargo test`
```

The cfg form is preferred for cross-cutting platform rules because it survives new triples being added.

### `[env]`

Sets environment variables visible to `build.rs`, rustc, and processes spawned by Cargo (1.56+).

```toml
[env]
DATABASE_URL = "postgres://localhost/mydb"
RUST_LOG = "info"
SOME_VAR = { value = "secret", force = true }   # override caller-provided env
```

`force = true` is required to override variables already set in the shell. Avoid placing real secrets here — the file is checked into version control.

### `[net]`

Network behavior for fetching crates and git deps.

```toml
[net]
git-fetch-with-cli = true   # use system `git` for fetches (needed for ssh/auth)
retry = 3                   # retry count on network failure
```

`git-fetch-with-cli = true` is essential behind corporate proxies or when a git dep requires SSH credentials that libgit2 cannot access.

### `[source]` — see Section 5 below for full treatment.

```toml
[source.crates-io]
replace-with = "vendored-sources"
```

### `[alias]`

Custom cargo subcommands that expand into existing commands.

```toml
[alias]
t = "test"
br = "build --release"
lint = "clippy --workspace --all-targets -- --deny warnings"
deps = "tree --duplicates"
```

Aliases cannot shadow built-in commands (`build`, `test`, etc.) — if you name an alias `test`, calling `cargo test` invokes the built-in, and only `cargo test <args>` reaches the alias as if it were a subcommand name.

### `[term]`

Terminal output.

```toml
[term]
color = "auto"      # "always" | "never" | "auto"
quiet = false
verbose = false
```

### Precedence and discovery order

1. `--config` flags on the command line.
2. `.cargo/config.toml` in cwd and walking up to the workspace root.
3. `$CARGO_HOME/config.toml`.
4. Built-in defaults.

## 4. Cargo Home (`CARGO_HOME`) and Build Cache

Defaults to `~/.cargo/` on Unix and `%USERPROFILE%\.cargo\` on Windows; override with the `CARGO_HOME` environment variable.

### Layout

| Path | Contents |
|---|---|
| `$CARGO_HOME/bin/` | Binaries installed via `cargo install` |
| `$CARGO_HOME/registry/index/` | Registry index clones (crates.io, sparse, custom) |
| `$CARGO_HOME/registry/cache/` | Downloaded `.crate` archives |
| `$CARGO_HOME/registry/src/` | Unpacked crate sources used during builds |
| `$CARGO_HOME/git/db/` | Bare clones of git dependencies |
| `$CARGO_HOME/git/checkouts/` | Working-tree checkouts of git deps |
| `$CARGO_HOME/credentials` / `credentials.toml` | Registry API tokens |

### CI reproducibility

- Pin `CARGO_HOME` to a known location (e.g., `/tmp/cargo-home`) and cache `registry/cache` and `git/db` between runs. Cache keys should incorporate `Cargo.lock` hash.
- `cargo install` writes into `$CARGO_HOME/bin`; in CI, prefer `cargo binstall` or vendor binaries via a pinned script instead of rebuilding the same tool every run.
- For air-gapped or fully reproducible builds, use `cargo vendor` and `[source]` replacement (Section 5) so no network is required.

### Cleaning

```bash
# Targeted cache cleanup (recommended — preserves credentials and installed binaries)
rm -rf "$CARGO_HOME/registry/cache"

# User-friendly inspection and pruning
cargo install cargo-cache
cargo cache -a                 # show summary, then prune
```

Do **not** `rm -rf ~/.cargo` wholesale — this also deletes `credentials`, `bin/`, and any locally installed tools.

## 5. Source Replacement (Enterprise Registries, Mirroring)

Source replacement redirects where Cargo fetches a given registry's crates. The full rules are in [Source Replacement](https://doc.rust-lang.org/cargo/reference/source-replacement.html).

### Mirror crates.io

```toml
[source.tuna]
registry = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"

[source.crates-io]
replace-with = "tuna"
```

The `sparse+` protocol prefix selects the modern sparse index (Cargo 1.68+) and is dramatically faster than the legacy git index. Use it for any registry that supports sparse.

### Vendored offline builds

```bash
cargo vendor vendor/                # writes crates into ./vendor/
cargo vendor --versioned-dirs vendor/  # stable dirs keyed by version
```

```toml
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
```

This produces a fully air-gapped build: no registry fetch, no git fetch, fully reviewable sources.

### Private enterprise registry

```toml
[source.my-company]
registry = "https://crates.internal.corp/git/index"

[source.crates-io]
replace-with = "my-company"          # optional: route everything through the proxy
```

### Authentication

```bash
cargo login --registry my-company <token>
# Writes to $CARGO_HOME/credentials.toml
```

Never commit credentials. For CI, inject the token via `CARGO_REGISTRIES_MY_COMPANY_TOKEN` rather than writing files.

### Gotchas and limits

- `[source.crates-io]` cannot be replaced by **two** sources — only one `replace-with` chain is allowed.
- A registry that is itself a replacement of crates.io cannot be a `replace-with` target a second time; Cargo detects cycles and errors.
- Git deps (`[dependencies.foo] git = "..."`) bypass `replace-with` entirely — they are not subject to crates.io mirroring.
- Supply-chain governance — license, advisory, ban, source checks — belongs to **rust-dependencies**, not this skill. Use `cargo-deny` with `deny.toml` there; here we only configure *where* crates come from.

## 6. `cargo metadata` for Scripting

Emits a stable JSON document describing every package Cargo would resolve. Format version 1 has been stable since Cargo 1.43 and is the only version new code should target.

### Common invocations

```bash
# Minimal: just the workspace members, no transitive resolution
cargo metadata --format-version 1 --no-deps

# Full graph (default): every resolved package and edge
cargo metadata --format-version 1

# Filter to specific deps
cargo metadata --format-version 1 --filter-platform x86_64-unknown-linux-gnu
```

### Useful jq filters

```bash
# List every package name and version
cargo metadata --format-version 1 | jq '.packages[] | {name, version}'

# Workspace members only
cargo metadata --format-version 1 --no-deps | jq '.workspace_members'

# Resolve tree edges
cargo metadata --format-version 1 | jq '.resolve.nodes[] | {id, deps: [.deps[].name]}'

# Find which packages pull in a given dependency
cargo metadata --format-version 1 | jq '.resolve.nodes[] | select(.deps[].name == "serde") | .id'
```

### Use cases

- Release tooling (`cargo-release`, `cargo-workspaces`) — drive version bumps from a deterministic graph.
- Dashboards — surface feature usage, MSRV per package, and license coverage.
- Migration tools — locate every crate still depending on a deprecated API.

### Gotcha

`cargo metadata` resolves the dependency graph, so it touches the registry. In CI use `--frozen` or `--locked` and pre-populate the cache to keep runs deterministic. Output is large (multi-MB on big workspaces); pipe through `jq` rather than printing to stdout.

## 7. CI Modes: `--locked`, `--frozen`, `--offline`

Three flags that look similar but mean very different things.

| Flag | Behavior | When to use |
|---|---|---|
| `--locked` | Use the existing `Cargo.lock` verbatim. Fail if the lockfile would need to change. | Every CI job on an existing repo; PR checks; release pipelines. |
| `--frozen` | Implies `--locked` **plus** `--offline`. Refuse to touch the network at all. | Air-gapped environments, signed-release builds, hermetic CI. |
| `--offline` | Use only cached registry/git data. Never reach the network, but allow `Cargo.lock` updates against the local cache. | Local dev on a train; CI with a pre-populated cache where you still want lock updates. |

### Recommended CI pattern

```bash
# On PR: catch lock drift early
cargo fetch --locked
cargo build --locked --workspace --all-targets
cargo test  --locked --workspace

# On release: hermetic
cargo build --frozen --release
cargo test  --frozen
```

### Gotchas

- `--locked` failing means `Cargo.lock` is out of date — fix it by running `cargo update` locally, committing the lockfile, and re-pushing. Do **not** add `cargo update` to CI to silence the failure.
- `--offline` still updates `Cargo.lock` if a new transitive dep is needed and is present in the cache. If you want full immutability, use `--frozen`.
- A deleted `Cargo.lock` makes `--locked` re-resolve from scratch, which is the opposite of deterministic. Library workspaces without lockfiles cannot meaningfully use `--locked`; document this or commit a lockfile anyway.

## 8. `cargo tree` Deep Usage

`cargo tree` prints the dependency graph. The `-e` (edges) and `-i` (invert) flags unlock almost every diagnostic need.

### Basic

```bash
cargo tree                       # full tree from workspace root
cargo tree --depth 2             # limit output to 2 levels
cargo tree -p my-crate           # tree for one package
cargo tree --workspace           # all members side by side
```

### Edge kinds (`-e`)

```bash
cargo tree -e normal             # only normal deps (default)
cargo tree -e dev                # only dev-deps
cargo tree -e build              # only build-deps
cargo tree -e features           # show which features are enabled where
cargo tree -e no-dev             # everything except dev-deps (good for prod audit)
cargo tree -e normal,build       # combine multiple kinds
```

### Duplicates (`--duplicates`, alias `-d`)

```bash
cargo tree -d                    # crates pulled in at >1 version
cargo tree -d -p serde           # duplicates of serde specifically
```

Output names each duplicate version and which paths lead to it. Duplicate versions are a code-size and compile-time signal, not necessarily a bug — but every duplicate deserves a one-line justification.

### Inverse tree (`--invert` / `-i`)

```bash
cargo tree -i serde              # who depends on serde, and through what path?
cargo tree -i serde --depth 1    # direct dependents only
cargo tree -i serde -e features  # which features of serde each consumer enables
```

The inverse tree is the primary tool for "why is X in my build?" investigations.

### Feature unification

```bash
cargo tree -e features -p tokio
cargo tree -e features -i tokio  # who enables which tokio feature
```

Combined with `cargo build --features X` you can prove exactly which features are active after unification. This is mandatory when a `--all-features` build fails but per-feature builds succeed — the inverse feature tree will show the conflicting consumer.

### Worked example: hunting a duplicate

```bash
# Step 1: list duplicates
cargo tree -d | grep -A2 serde

# Step 2: see who pulls the unwanted version
cargo tree -i serde@0.9.0 -e normal

# Step 3: decide — pin the consumer up, or accept the duplicate
```

### Gotchas

- `cargo tree` resolves by default; if you want to inspect the manifest without resolving, use `cargo metadata --no-deps` instead.
- `-e features` only shows features explicitly enabled by a path through the graph; default features are folded in implicitly. To see defaults explicitly, run with `--features` overrides one at a time.
- Filtering with `--target` changes the resolved graph (target-specific deps come and go); always specify `--target` when investigating a cross-compile duplicate.

## Key References

- [Cargo Book — Home](https://doc.rust-lang.org/cargo/)
- [Cargo Reference — Lints](https://doc.rust-lang.org/cargo/reference/lints.html)
- [Cargo Reference — Build scripts (specifying dependencies)](https://doc.rust-lang.org/cargo/reference/build-scripts.html)
- [Cargo Reference — Configuration](https://doc.rust-lang.org/cargo/reference/config.html)
- [Cargo Reference — Source Replacement](https://doc.rust-lang.org/cargo/reference/source-replacement.html)
- [Cargo Reference — Cargo Home](https://doc.rust-lang.org/cargo/guide/cargo-home.html)
- [Cargo Reference — `cargo metadata` output format](https://doc.rust-lang.org/cargo/commands/cargo-metadata.html)
- [Cargo Reference — `cargo tree`](https://doc.rust-lang.org/cargo/commands/cargo-tree.html)
- [Cargo Reference — `cargo vendor`](https://doc.rust-lang.org/cargo/commands/cargo-vendor.html)
