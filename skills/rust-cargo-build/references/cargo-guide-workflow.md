# Cargo Guide Workflow (Onboarding)

Beginner-friendly walkthrough of the first chapters of the [Cargo Guide](https://doc.rust-lang.org/cargo/guide/) — the "how do I actually use Cargo?" complement to the Cargo Book Reference depth in `cargo-reference-cheatsheet.md`. Each section maps to a Guide chapter, gives the canonical commands and file shapes, calls out gotchas that trip up new users, and points to the deeper reference or sibling skill when a topic exceeds onboarding scope.

Reach for this file when the user is starting a new Rust project, asking "how do I build/test/run", wiring up CI, or needs the apps-vs-libs `Cargo.lock` policy. Hand off once the question turns into manifest field depth, resolver internals, or module layout.

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
├── .gitignore       # contains /target
└── README.md        # only when --vcs is set (default: git if the parent is not already a repo)
```

### Default `Cargo.toml` skeleton

```toml
[package]
name = "my-lib"
version = "0.1.0"
edition = "2021"

[dependencies]
```

- `edition` defaults to the latest stable edition supported by the `cargo` that generated the project. Newer Cargo (1.85+) generates `edition = "2024"`.
- `cargo new` writes a starter `#[test]` in `src/lib.rs` or `src/main.rs` so `cargo test` works immediately — useful as a smoke test that the toolchain is installed correctly.

### Gotchas

- Package names in `Cargo.toml` cannot contain uppercase letters; `cargo new` lowercases the folder name. If you need a different binary name, use `--name` or `[[bin]] name = ...`.
- A project can contain **both** `src/lib.rs` and `src/main.rs` — the library is then available to the binary via the package name, which is the common idiom for testable applications.
- `cargo new` refuses to run inside an existing git repository by default; pass `--vcs none` if the parent is already versioned.

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
| `cargo bench` | Run benchmarks in `benches/` | Nightly-only without `criterion` |

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
my-private = { version = "1.0", registry = "my-company" }                  # private registry (see cheatsheet §5)
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

The depth on version-requirement syntax (`"1"`, `"1.2"`, `"1.2.3"`, `"=1.2.3"`, `"^"`, `"~"`, `"*"`), cargo-update semantics, and SemVer-compatible upgrades belongs to **rust-dependencies** (selection and governance) and **rust-semver** (breaking-change classification). Feature unification internals and `cargo tree -e features` diagnostics are in `cargo-reference-cheatsheet.md` §8.

### Gotchas

- Prefer `default-features = false` for heavy crates (like `reqwest`, `tokio`) so you only pull what you use — but verify the slimmed feature set still compiles, since some features implicitly depend on others.
- A path dependency is fine for local dev but **cannot** be published to crates.io pointing at an unpublished local path; publish a versioned crate or use a git/tag source instead.
- Git dependencies bypass crates.io source replacement (mirroring/vendoring) — see `cargo-reference-cheatsheet.md` §5.

## 5. Package Layout (Canonical)

```
my-package/
├── Cargo.toml
├── Cargo.lock                  # commit for apps, do NOT commit for libs (Section 6)
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
    └── config.toml             # optional per-project config (see cheatsheet §3)
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

| Project type | Commit `Cargo.lock`? | Why |
|---|---|---|
| Binary / application | **Yes** | Guarantees the exact dependency versions you tested are the ones that ship |
| Library published to crates.io | **No** | The lockfile would freeze transitive deps for downstream apps, defeating their own resolution |

### Rules of thumb

- Apps: commit `Cargo.lock`. CI must build with `--locked` (Section 7) so a drifted lockfile fails the pipeline instead of silently re-resolving.
- Libraries: do not commit. The crates.io index ignores `Cargo.lock` on publish anyway — it is not packaged into the `.crate` file.
- Workspace with mixed apps and libs: commit one lockfile at the workspace root. The presence of at least one binary in the workspace is usually reason enough to commit it.

### Hand-off

Lockfile policy rationale, `cargo update` workflows, version-requirement syntax, and dependency governance belong to **rust-dependencies**. CI lock-handling flags (`--locked` / `--frozen` / `--offline`) are covered with worked examples in `cargo-reference-cheatsheet.md` §7.

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
      - run: cargo clippy --workspace --all-targets --all-features -- -D warnings
      - run: cargo test --workspace --all-targets --all-features
      - run: cargo doc --workspace --all-features --no-deps
```

- `dtolnay/rust-toolchain@stable` installs a pinned stable toolchain. Add `with: components: rustfmt,clippy` if you pin the toolchain separately.
- `Swatinem/rust-cache@v2` caches `~/.cargo/registry`, `~/.cargo/git`, and `target/`, keyed on `Cargo.lock` hash. This is usually the single biggest CI speedup.
- For MSRV verification, add a second job using `dtolnay/rust-toolchain@1.75` (or your declared `rust-version`) without `--all-features` unless the feature set is MSRV-clean.

### GitLab CI template

```yaml
variables:
  RUST_BACKTRACE: "1"

test:
  image: rust:latest
  cache:
    key: "$CI_COMMIT_REF_NAME"
    paths:
      - .cargo/
      - target/
  before_script:
    - export CARGO_HOME=$CI_PROJECT_DIR/.cargo
  script:
    - cargo fmt --all --check
    - cargo clippy --workspace --all-targets --all-features -- -D warnings
    - cargo test --workspace --all-targets --all-features
    - cargo doc --workspace --all-features --no-deps
```

### Lockfile flags in CI

| Flag | Behavior | When |
|---|---|---|
| `--locked` | Fail if `Cargo.lock` would need to change | Every CI job on a repo that commits a lockfile |
| `--frozen` | `--locked` + `--offline`; refuse any network | Air-gapped / hermetic / signed-release builds |
| `--offline` | Use only cached registry/git data; still allows lock updates against the cache | Local dev offline; CI with pre-populated cache |

Full semantics and the fix for "`--locked` failed in CI" are in `cargo-reference-cheatsheet.md` §7: run `cargo update` locally, commit the refreshed lockfile, and re-push — never add `cargo update` to CI.

### Gotchas

- `cargo fmt --all --check` **fails** if any file is not formatted; run `cargo fmt --all` locally before pushing.
- `cargo clippy -- -D warnings` turns every lint warning into a CI failure. Decide deliberately whether your project treats lints as errors; pin the policy in `[lints]` (cheatsheet §1) so it travels with the source.
- Caching `target/` can go stale if the toolchain changes; `Swatinem/rust-cache` handles keying, but a manual cache clear is sometimes needed after a toolchain bump.

## 8. Cargo Home

`CARGO_HOME` (default `~/.cargo/` on Unix) holds the registry index, downloaded crates, git checkouts, installed binaries, and registry credentials. Its layout, CI caching strategy, and safe cleanup commands (`cargo cache -a`, never `rm -rf ~/.cargo`) are documented in full in `cargo-reference-cheatsheet.md` §4 (Cargo Home and Build Cache).

For onboarding purposes, the two things to know:

1. **Cache it in CI.** Cache `$CARGO_HOME/registry/cache` and `$CARGO_HOME/git/db` between runs, keyed on the `Cargo.lock` hash. This is what `Swatinem/rust-cache` (Section 7) does under the hood.
2. **Do not delete it wholesale.** `rm -rf ~/.cargo` also removes `credentials`, `bin/`, and any locally installed tools. Use targeted cleanup or `cargo cache -a`.

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
