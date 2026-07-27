# Cargo Guide Workflow (Onboarding)

Beginner-friendly walkthrough of the first chapters of the [Cargo Guide](https://doc.rust-lang.org/cargo/guide/). Each section maps to a Guide chapter, gives the canonical commands and file shapes, calls out common mistakes, and points to the deeper reference or sibling skill when a topic exceeds onboarding scope.

Reach for this file when the user is starting a new Rust project, asking "how do I build/test/run", wiring up CI, or deciding how to manage `Cargo.lock`. Hand off once the question turns into manifest field depth, resolver internals, or module layout.

## Contents

1. Why Cargo exists
2. Creating a new package
3. Working on an existing package
4. Adding dependencies
5. Package layout
6. `Cargo.toml` and `Cargo.lock`
7. Continuous integration
8. Cargo Home
9. Tests
10. Publishing
11. Build performance

## 1. Why Cargo Exists

Cargo is the official Rust package manager and build system. In other language ecosystems the responsibilities it unifies are spread across several tools:

| Responsibility | Without Cargo (typical tools) | With Cargo |
|---|---|---|
| Build / compile | `make`, `cmake`, `ninja` | `cargo build` |
| Dependency management | `vcpkg`, `conan`, `npm` | `[dependencies]` + crates.io |
| Test runner | custom harness, `gtest` | `cargo test` |
| Doc generation | `doxygen`, custom | `cargo doc` |
| Publishing | custom scripts | `cargo publish` |

Cargo provides all five in a single tool driven by one declarative `Cargo.toml`. The payoff for new users: no per-project build scripts to maintain, reproducible dependency resolution via `Cargo.lock`, and one command vocabulary (`build`, `check`, `test`, `run`, `doc`, `fmt`, `clippy`) that works identically across every Rust project.

### Gotcha

Cargo is not a general-purpose build system like `make`. It is opinionated about project layout (see Section 5). Tasks that need arbitrary file generation or orchestration belong in a `build.rs` (see `build-scripts.md`) or an external tool — not in hand-written `make` targets glued onto Cargo.

## 2. Creating a New Package

### `cargo new` vs `cargo init`

```bash
cargo new my-lib              # creates ./my-lib/ with a fresh project
cargo new my-app              # binary by default (src/main.rs)
cargo new --lib my-lib        # explicit library (src/lib.rs)
cargo new --bin my-app        # explicit binary
cargo new --vcs git my-app    # also init a git repo and add .gitignore
cargo new --name custom ./dir # override the package name derived from the folder

cargo init                    # use the current directory; do NOT create a wrapper folder
cargo init --lib              # same, but a library
```

- `cargo new <path>` creates a new subdirectory. Use it when starting from a clean parent folder.
- `cargo init` adopts the current directory in place. Use it when the folder already exists (e.g., a repo already cloned with a README).

### Generated structure

```
my-lib/
├── Cargo.toml       # [package] with name, version, edition
├── src/
│   └── lib.rs       # or main.rs for a binary
└── .gitignore       # present when Cargo initializes supported version control
```

### Default `Cargo.toml` skeleton

```toml
[package]
name = "my-lib"
version = "0.1.0"
edition = "2024"

[dependencies]
```

- `edition` defaults to the latest stable edition supported by the installed Cargo. Current stable Cargo generates `edition = "2024"`; use `cargo --version` before relying on generated defaults.
- `cargo new` creates the manifest, source entry point, and optional version-control files. It does not create a README; add one when the package needs user-facing documentation or publication metadata.

### Gotchas

- Use a package name accepted by the installed Cargo and target registry. If the package and binary names differ, use `--name` or an explicit `[[bin]]`.
- A project can contain **both** `src/lib.rs` and `src/main.rs` — the library is then available to the binary via the package name, which is the common idiom for testable applications.
- Inside an existing version-control repository, Cargo normally avoids initializing another repository. Use `--vcs` only when an explicit choice is needed.

## 3. Working on an Existing Package

The everyday loop, in rough order of frequency:

| Command | Purpose | Notes |
|---|---|---|
| `cargo check` | Type-check without codegen | Much faster than `build`; use during development |
| `cargo build` | Compile, write artifacts to `target/` | Use `--release` for optimized builds |
| `cargo run` | Build and run the main binary | Args after `--` go to the program |
| `cargo run --example foo` | Run `examples/foo.rs` | Examples are compiled as separate binaries |
| `cargo test` | Run unit, integration, and doctests | Add `--no-fail-fast` to run all suites |
| `cargo test --test integration_test` | Run one integration test file under `tests/` | File name, not test fn name |
| `cargo doc --open` | Generate API docs and open in browser | `--no-deps` skips dependency docs |
| `cargo clean` | Remove `target/` | Frees disk; forces full rebuild next time |
| `cargo update` | Update `Cargo.lock` within declared requirements | Does not edit `Cargo.toml` |
| `cargo fmt` | Format code | `--check` for CI mode |
| `cargo clippy` | Lint | `-- -D warnings` for CI mode |
| `cargo bench` | Build and run benchmark targets | Harness and framework requirements depend on the benchmark design |

### `check` vs `build`

`cargo check` skips code generation and linking — it answers "does this type-check?" in a fraction of the time. Make it the default inner-loop command; reserve `cargo build` for when you need a runnable artifact or to surface linker errors.

### Running a specific binary in a multi-bin project

```bash
cargo run --bin tool        # run src/bin/tool.rs (or a [[bin]] target)
cargo run --bin tool -- --flag value
```

### Gotchas

- `cargo run` recompiles only what changed, but it **does** produce a real binary — running it has side effects. For pure validation use `cargo check`.
- `cargo test` runs doctests by default, which compile every code block in rustdoc comments; pass `--doc` or `--tests` to narrow scope when doctests are slow.
- `cargo update` only moves versions **within** the requirements already declared in `Cargo.toml`. To pull a breaking change you must edit `Cargo.toml` first. See `rust-dependencies` for the version-requirement syntax.

## 4. Adding Dependencies

### Basic forms

```toml
[dependencies]
serde = "1"                                                   # bare version = crates.io, caret semantics
serde = { version = "1", features = ["derive"] }              # enable features
reqwest = { version = "0.12", default-features = false, features = ["json", "rustls-tls"] }
```

### Non-crates.io sources

```toml
my-crate = { path = "../my-crate" }                                        # local path (same repo)
my-crate = { git = "https://github.com/user/repo" }                        # default branch
my-crate = { git = "https://github.com/user/repo", branch = "dev" }        # pinned branch
my-crate = { git = "https://github.com/user/repo", tag = "v1.2.3" }        # pinned tag
my-crate = { git = "https://github.com/user/repo", rev = "a1b2c3d" }       # pinned commit (most reproducible)
my-private = { version = "1.0", registry = "my-company" }                  # private registry; see registries-authentication.md
```

### Scopes

```toml
[dependencies]            # used by lib/bin targets, at build time and runtime
tokio = { version = "1", features = ["full"] }

[dev-dependencies]        # tests, examples, benches ONLY — not compiled into released artifacts
proptest = "1"
pretty_assertions = "1"

[build-dependencies]      # build.rs ONLY — built for the host triple, not linked into the artifact
prost-build = "0.13"
```

### Optional dependencies and features

```toml
[dependencies]
serde = { version = "1", optional = true }

[features]
default = []
json = ["dep:serde"]      # "dep:" exposes the optional dep as a feature without auto-coupling
```

### Hand-off

The depth on version-requirement syntax (`"1"`, `"1.2"`, `"1.2.3"`, `"=1.2.3"`, `"^"`, `"~"`, `"*"`), cargo-update semantics, and SemVer-compatible upgrades belongs to **rust-dependencies** (selection and governance) and **rust-semver** (breaking-change classification). Feature unification internals are in `dependencies-features-resolver.md`; command diagnostics are in `cargo-command-map.md`.

### Gotchas

- Inspect default features and disable them only when the resulting capability, platform, TLS, and compatibility contract is intentional and tested.
- crates.io does not accept ordinary published dependencies that exist only as path, Git, or alternate-registry sources. When local or Git development needs a registry publication fallback, declare a compatible registry `version` alongside the alternate location as supported by the installed Cargo.
- Git dependencies are distinct sources and do not become crates.io mirror traffic — see `registries-authentication.md`.

## 5. Package Layout (Canonical)

```
my-package/
├── Cargo.toml
├── Cargo.lock                  # commit by default; document any deliberate exception
├── src/
│   ├── lib.rs                  # library crate root (or main.rs for a binary)
│   ├── main.rs                 # binary crate root (can coexist with lib.rs)
│   └── bin/
│       └── tool.rs             # additional binary target named `tool`
├── tests/                      # integration tests (each file is a separate crate)
│   └── integration_test.rs
├── benches/                    # benchmarks (each file is a separate crate)
│   └── my_bench.rs
├── examples/                   # examples (each file is a separate binary)
│   └── simple.rs
├── build.rs                    # optional build script
└── .cargo/
    └── config.toml             # optional project config; see configuration-environment.md
```

### Conventions Cargo assumes

- `src/lib.rs` → library target named after the package.
- `src/main.rs` → binary target named after the package.
- `src/bin/*.rs` → extra binaries, one per file.
- `tests/*.rs`, `benches/*.rs`, `examples/*.rs` → discovered automatically; no manifest entry needed unless you want to override paths or settings.

You only add explicit `[lib]`, `[[bin]]`, `[[test]]`, `[[bench]]`, or `[[example]]` tables when the file path or target name deviates from the convention above.

### Hand-off

- Multi-crate repository layout (virtual workspace, `[workspace] members`, shared `[workspace.dependencies]`) belongs to **rust-workspace**.
- In-crate module tree design (`mod.rs` vs file-based modules, `pub` visibility, re-exports) belongs to **rust-module-layout**.
- Target table field depth (`crate-type`, `proc-macro`, `path`, `required-features`) is in `manifest-targets.md`.

### Gotcha

Every file under `tests/`, `benches/`, and `examples/` compiles as its own crate. Putting many integration tests in one file speeds up the suite; splitting them into many files parallelizes better but multiplies compile units. There is no universal answer — measure for your project.

## 6. `Cargo.toml` vs `Cargo.lock`

The current Cargo Guide recommends checking `Cargo.lock` into version control when in doubt. A lockfile records the exact graph used by contributors and CI; dependency requirements in `Cargo.toml` still define what downstream consumers may resolve.

### Rules of thumb

- Commit `Cargo.lock` by default for applications, libraries, examples, tools, and mixed workspaces so CI can reproduce and audit the tested graph.
- Document a deliberate exception when a repository validates broad dependency resolution without a committed lockfile.
- Use `--locked` only when a lockfile exists and must remain unchanged; Cargo fails if the lockfile is missing or needs an update.
- Publishing may generate or include a minimized lockfile according to current Cargo packaging rules. Verify package contents with the installed Cargo rather than assuming repository lockfile policy controls downstream resolution.

### Hand-off

Lockfile mechanics and reproducibility policy remain in this Cargo skill. Version-requirement semantics, crate selection, advisories, licenses, and dependency governance belong to **rust-dependencies**. Command-side `--locked`, `--frozen`, and `--offline` behavior is summarized in `cargo-command-map.md`.

### Gotcha

A common mistake is deleting `Cargo.lock` to "force an update". That throws away the entire resolved graph and re-resolves from scratch, often pulling in surprise breaking changes. To update one dependency, run `cargo update -p that-crate`; to update everything within declared requirements, run `cargo update` and review the diff before committing.

## 7. Continuous Integration

### GitHub Actions template

A standard Rust CI job: format check, lint, test, and doc build with caching.

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2           # cache ~/.cargo and target/ keyed on Cargo.lock
      - run: cargo fmt --all --check
      - run: cargo clippy --workspace --all-targets --all-features --locked -- -D warnings
      - run: cargo test --workspace --all-targets --all-features --locked
      - run: cargo doc --workspace --all-features --no-deps --locked
```

- `dtolnay/rust-toolchain@stable` follows the stable channel rather than pinning a release. Use an explicit supported toolchain when reproducibility or MSRV validation requires it.
- `Swatinem/rust-cache@v2` caches `~/.cargo/registry`, `~/.cargo/git`, and `target/`, keyed on `Cargo.lock` hash. This is usually the single biggest CI speedup.
- For MSRV verification, add a second job using the declared `rust-version` without `--all-features` unless the feature set is explicitly MSRV-clean.

### GitLab CI template

```yaml
variables:
  RUST_BACKTRACE: "1"
  RUST_VERSION: "1.97" # update intentionally with the repository's supported toolchain

test:
  image: rust:${RUST_VERSION}
  cache:
    key: "$CI_COMMIT_REF_NAME"
    paths:
      - .cargo/
      - target/
  before_script:
    - export CARGO_HOME=$CI_PROJECT_DIR/.cargo
  script:
    - cargo fmt --all --check
    - cargo clippy --workspace --all-targets --all-features --locked -- -D warnings
    - cargo test --workspace --all-targets --all-features --locked
    - cargo doc --workspace --all-features --no-deps --locked
```

### Lockfile flags in CI

| Flag | Behavior | When |
|---|---|---|
| `--locked` | Fail if `Cargo.lock` would need to change | Every CI job on a repo that commits a lockfile |
| `--frozen` | `--locked` + `--offline`; refuse any network | Air-gapped / hermetic / signed-release builds |
| `--offline` | Use only cached registry/git data; still allows lock updates against the cache | Local dev offline; CI with pre-populated cache |

If `--locked` fails, identify whether the lockfile is absent or stale. Update intentionally on a development branch, review the graph change, commit it when policy requires, and never add an unconditional `cargo update` to CI merely to silence the failure.

### Gotchas

- `cargo fmt --all --check` **fails** if any file is not formatted; run `cargo fmt --all` locally before pushing.
- `cargo clippy -- -D warnings` turns every lint warning into a CI failure. Decide deliberately whether the project treats lints as errors and route policy design to `rust-style-clippy`.
- Caching `target/` can go stale if the toolchain changes; `Swatinem/rust-cache` handles keying, but a manual cache clear is sometimes needed after a toolchain bump.

## 8. Cargo Home

`CARGO_HOME` (default `~/.cargo/` on Unix) holds the registry index, downloaded crates, Git checkouts, installed binaries, and registry credentials. Its layout, CI caching strategy, and cleanup safeguards are documented in `build-cache-diagnostics.md`.

For onboarding purposes, the two things to know:

1. **Cache it in CI.** Cache `$CARGO_HOME/registry/cache` and `$CARGO_HOME/git/db` between runs, keyed on the `Cargo.lock` hash. This is what `Swatinem/rust-cache` (Section 7) does under the hood.
2. **Do not delete it wholesale.** Removing Cargo Home also removes credentials, installed binaries, and developer state. Prove cache corruption and resolve the exact cache entry before cleanup.

## 9. Tests

Cargo discovers unit tests, integration tests, doctests, examples, and benchmark targets through conventional layout. Use `cargo test` selectors to execute the intended scope, but route test architecture, fixtures, property testing, concurrency control, and coverage policy to **rust-testing**.

Always distinguish compilation from execution: test commands run project-controlled code and may require services, credentials, files, network access, or target hardware.

Official guide: [Tests](https://doc.rust-lang.org/cargo/guide/tests.html).

## 10. Publishing

Use `cargo package --list` before packaging, then build and test the packaged crate. Resolve the registry, credentials, ownership, version, publication order, and authorization before `cargo publish`.

Publishing and yanking change external registry state. Follow `publishing.md` for the complete gate and route API compatibility decisions to **rust-semver**.

Official guide entry: [Publishing on crates.io](https://doc.rust-lang.org/cargo/reference/publishing.html).

## 11. Build Performance

Measure the actual workflow before changing profiles, linkers, codegen settings, feature unification, or caches:

```bash
cargo build --timings
cargo tree --duplicates
cargo tree -e features
```

Use `profiles.md` for profile trade-offs and `build-cache-diagnostics.md` for timings, rebuilds, and cache behavior.

Official guide: [Optimizing Build Performance](https://doc.rust-lang.org/cargo/guide/build-performance.html).

## Key References

- [Cargo Guide — Home](https://doc.rust-lang.org/cargo/guide/)
- [Cargo Guide — Why Cargo Exists](https://doc.rust-lang.org/cargo/guide/why-cargo-exists.html)
- [Cargo Guide — Creating a New Package](https://doc.rust-lang.org/cargo/guide/creating-a-new-project.html)
- [Cargo Guide — Working on an Existing Package](https://doc.rust-lang.org/cargo/guide/working-on-an-existing-project.html)
- [Cargo Guide — Dependencies](https://doc.rust-lang.org/cargo/guide/dependencies.html)
- [Cargo Guide — Package Layout](https://doc.rust-lang.org/cargo/guide/project-layout.html)
- [Cargo Guide — Cargo.toml vs Cargo.lock](https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html)
- [Cargo Guide — Continuous Integration](https://doc.rust-lang.org/cargo/guide/continuous-integration.html)
- [Cargo Guide — Cargo Home](https://doc.rust-lang.org/cargo/guide/cargo-home.html)
- [Cargo Guide — Tests](https://doc.rust-lang.org/cargo/guide/tests.html)
- [Cargo — Publishing on crates.io](https://doc.rust-lang.org/cargo/reference/publishing.html)
- [Cargo Guide — Optimizing Build Performance](https://doc.rust-lang.org/cargo/guide/build-performance.html)
