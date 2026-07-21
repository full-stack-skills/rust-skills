---
name: rust-cargo-build
description: Configure and diagnose Rust Cargo builds, including Cargo.toml manifests, dependency sources and versions, features, resolvers, profiles, build.rs, workspaces, cross-compilation, packaging, and publishing. Also covers the Cargo Book Reference depth: `.cargo/config.toml` (build, env, target, net, source, alias), `[lints]` table and workspace inheritance, `[build-dependencies]` vs `[dependencies]` scoping, Cargo Home and build cache layout, source replacement (mirrors, vendoring, private registries), `cargo metadata` for scripting, CI modes (`--locked`, `--frozen`, `--offline`), and `cargo tree` diagnostics (`--duplicates`, `--invert`, `-e features`). Includes Cargo Guide onboarding (cargo new, build, check, test, run, dependencies, package layout, Cargo.toml vs Cargo.lock, and CI integration with GitHub Actions / GitLab CI templates). Use when users ask about Cargo manifests, dependency resolution, feature unification, build output, MSRV-aware resolution, Cargo commands, `config.toml` sections, source mirroring, crates.io publishing, or beginner "how do I build/test/run my Rust project" questions. Hand supply-chain governance (license/advisory/ban audits via cargo-deny) to rust-dependencies, semver versioning decisions to rust-semver, and module/crate topology to rust-workspace; hand test design to rust-testing. Route standard-library API lookup ("how do I use HashMap/Vec/io?") to rust-stdlib and "how do I write X in Rust?" tutorial-style questions to rust-by-example.
---

# Rust Cargo Build System

Configure the build based on the project's actual Cargo version, MSRV (Minimum Supported Rust Version), and workspace root manifest. Read detailed fields as needed; do not generate unvalidated configurations from memory.

## Pre-Flight Checks

```bash
rustc --version --verbose
cargo --version
cargo metadata --no-deps --format-version 1
```

Additionally, verify:

- The root `Cargo.toml` is a package or virtual workspace.
- Consistency of `edition`, `rust-version`, `resolver`, and `Cargo.lock`.
- Dependency sources (crates.io, Git paths, local paths) and whether they inherit from the workspace.
- Build targets, feature combinations, target platforms, and publishing registry configuration.

## Cargo Guide Workflow (Onboarding)

For beginner and "getting started" questions, the first chapters of the [Cargo Guide](https://doc.rust-lang.org/cargo/guide/) cover the everyday Cargo loop. Reach for the deep reference when the answer turns into manifest field syntax, resolver internals, or module topology.

1. **Why Cargo Exists** — Cargo unifies build, dependency resolution, test, doc gen, and publish into one tool, replacing make/cmake + vcpkg/conan + custom harnesses.
2. **Creating a New Package** — `cargo new` (creates a subfolder) vs `cargo init` (adopts the cwd); defaults produce `src/lib.rs` or `src/main.rs` plus a minimal `Cargo.toml`.
3. **Working on an Existing Package** — the everyday loop: `cargo check` (fast, no codegen), `build`, `run`, `test`, `doc`, `clean`, `update`, plus `fmt`/`clippy`.
4. **Dependencies** — `[dependencies]`, `[dev-dependencies]`, `[build-dependencies]`, optional deps and features; crates.io, path, and git sources. Version-requirement syntax depth belongs to `rust-dependencies`.
5. **Package Layout** — canonical `src/`, `tests/`, `benches/`, `examples/`, `build.rs`. Multi-crate layout goes to `rust-workspace`; in-crate module design to `rust-module-layout`.
6. **Cargo.toml vs Cargo.lock** — apps commit the lockfile; libraries do not. Full policy and update workflow in `rust-dependencies`.
7. **Continuous Integration** — standard GitHub Actions / GitLab CI templates with caching, plus `--locked` / `--frozen` / `--offline` discipline.
8. **Cargo Home** — `$CARGO_HOME` layout and safe cleanup; full treatment in `references/cargo-reference-cheatsheet.md` §4.

Full commands, file shapes, CI templates, and gotchas for all eight topics live in `references/cargo-guide-workflow.md`.

## Capabilities & Boundaries

### Suitable For Handling

- Package (`lib`), binary (`bin`), example, test, bench, and library targets.
- Regular development builds with dependencies across multiple platforms and workspaces.
- Additive features, optional dependencies, feature unification strategies.
- Dev, release, and custom profiles for artifact-size or performance optimization.
- `build.rs`, native linking, generated files, conditional rebuilds based on build script inputs.
- Workspace members, shared dependencies, shared package fields.
- Target selection, linker configuration, runner setup, and cross-compilation settings.
- Commands: `cargo package`, `cargo publish`, yank operations, pre-publish validation steps.

### Offload to Other Skills

- Module tree structure, crate API definitions, file layouts → `rust-workspace`
- Testing strategies, doctests, coverage metrics → `rust-testing`
- Rust formatting (`rustfmt`) and linting (Clippy), edition migrations → `rust-style-clippy`
- Core Rust syntax and standard library usage → `rust-stable`
- Standard-library API lookup ("how do I use `HashMap`/`Vec`/`io::Read`?") → `rust-stdlib`
- "How do I write X in Rust?" tutorial-style questions (ownership, pattern matching, traits, concurrency idioms) → `rust-by-example`
- Supply-chain governance: license/advisory/ban audits via `cargo-deny`, dependency review, allowed/banned crate lists → `rust-dependencies`
- Semver versioning decisions, breaking-change classification, version bump strategy, `cargo-semver-checks` runs → `rust-semver`
- Workspace topology, member listing, shared dependency inheritance, virtual manifest design → `rust-workspace`

## Workflow

1. **Locate Root Manifest** — Use `cargo locate-project --workspace` to confirm the active workspace configuration.
2. **Declare Compatibility Boundaries** — Explicitly define edition, MSRV, supported platforms, and feature strategy.
3. **Design Dependencies** — Prioritize crates.io versions; use Git or local paths only when explicitly required, limiting features where possible.
4. **Configure Build Settings** — Set targets, profiles, build scripts, and `.cargo/config.toml` as needed.
5. **Validate Parsing Results** — Run `cargo metadata`, `cargo tree -e features`, and `cargo tree -d`.
6. **Execute Quality Gates** — Execute `fmt`, `check`, `test`, `clippy`; perform actual target builds for the specified platform(s).
7. **Verify Package Contents** — Before publishing, run `cargo package --list` and execute `cargo package`.

## Critical Decisions

### Edition, MSRV, and Resolver

- The edition controls language compatibility but does not equate to the compiler's minimum version requirement.
- Declare MSRV using `package.rust-version`, then validate on that toolchain.
- The resolver is a workspace-wide setting; resolver values in dependency manifests do not override the root workspace resolver.
- Default behavior: Edition 2021 uses resolver 2; Edition 2024 defaults to resolver 3.
- Resolver 3 makes `incompatible-rust-versions = "fallback"` the default; it does not replace resolver 2's feature-unification behavior.
- For virtual workspaces, explicitly declare a resolver in `[workspace]`.

### Features

- Treat features as additive capabilities; avoid designing mutually exclusive feature sets unless necessary.
- Use `dep:name` to control whether an optional dependency becomes a named feature.
- Forward dependencies via `crate/feature`, `crate?/feature`, or similar patterns depending on the crate type and resolver behavior.
- Validate actual enabled sources using `cargo tree -e features`.

### Build Scripts (`build.rs`)

- Generate outputs only to `OUT_DIR`; use them with `include!` macros or environment variables as needed.
- Declare rerun conditions for each input: `cargo::rerun-if-changed` (for file changes) or `cargo::rerun-if-env-changed`.
- Limit the scope of native linking parameters to avoid polluting entire workspace configurations.
- Do not download non-reproducible resources within build scripts; instead, use fixed dependencies or pre-generated assets.

### Profiles

- Measure bottlenecks first before adjusting linker (`lto`), codegen units, stripping (`strip`), and panic handling settings.
- Profile configuration applies only at the workspace root level.
- Do not infer debug behavior from release builds; do not assume reverse inference between them without explicit testing.

## Cargo Reference Deep Dive

The Cargo Book Reference covers advanced topics beyond the basic manifest. Use these summaries as entry points and consult `references/cargo-reference-cheatsheet.md` for full TOML shapes, gotchas, and validation commands. Pin a toolchain (`cargo --version`) before relying on any feature with a version gate.

1. **`[lints]` table** — Declares rustc and Clippy lint levels directly in `Cargo.toml` (Cargo 1.74+). Supports `[workspace.lints.rust]` / `[workspace.lints.clippy]` with member opt-in via `[lints] workspace = true`; per-lint `priority` controls layering. See reference Section 1.

2. **`[build-dependencies]` vs `[dependencies]`** — Four scopes (`[dependencies]`, `[dev-dependencies]`, `[build-dependencies]`, target-scoped). Build-deps compile for the **host** triple and are invisible to the final artifact; dev-deps cannot be used by `build.rs`. Same crate name in both tables resolves independently. See reference Section 2.

3. **`.cargo/config.toml`** — Sections: `[build]` (jobs, target-dir, rustflags), `[env]` (with `force = true` to override shell env), `[target.<triple>]` and `[target.'cfg(...)']`, `[net]` (git-fetch-with-cli, retry), `[source]` (replacement), `[alias]`, `[term]`. Precedence: CLI > cwd `.cargo/config.toml` walking up > `$CARGO_HOME/config.toml`. See reference Section 3.

4. **Cargo Home and build cache** — `CARGO_HOME` (default `~/.cargo/`) holds `bin/`, `registry/{index,cache,src}/`, `git/{db,checkouts}/`, and `credentials`. Pin its location in CI and cache `registry/cache` + `git/db` keyed on `Cargo.lock`. Never `rm -rf ~/.cargo` wholesale — use `cargo cache -a`. See reference Section 4.

5. **Source replacement** — Mirror crates.io via `[source.crates-io] replace-with = "mirror"` plus a `[source.mirror] registry = "sparse+https://..."`. Use `cargo vendor` + `[source.vendored-sources] directory = "vendor"` for air-gapped builds. Inject registry tokens via `CARGO_REGISTRIES_<NAME>_TOKEN` in CI, not files. License/advisory/ban governance belongs in `rust-dependencies`. See reference Section 5.

6. **`cargo metadata` for scripting** — Stable JSON (format-version 1) describing every resolved package; pair with `jq` for release tooling, dashboards, and migration audits. Use `--no-deps` for workspace-only and `--locked` in CI to stay deterministic. See reference Section 6.

7. **CI modes** — `--locked` fails if `Cargo.lock` would change (every CI job); `--frozen` adds `--offline` for air-gapped/hermetic builds; `--offline` allows lock updates against the local cache only. Fix `--locked` failures by running `cargo update` locally, never in CI. See reference Section 7.

8. **`cargo tree` deep usage** — `-e normal|dev|build|features|no-dev` selects edge kinds; `-d` (`--duplicates`) lists crates with multiple versions; `-i <crate>` (`--invert`) answers "who depends on X?"; `-e features -i <crate>` proves which features each consumer enables after unification. See reference Section 8.

Full TOML, semantics, worked examples, and per-topic gotchas live in `references/cargo-reference-cheatsheet.md`.

## Validation Commands

```bash
cargo fmt --all --check
cargo metadata --format-version 1 --locked
cargo check --workspace --all-targets --all-features
cargo test --workspace --all-targets --all-features
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo package --list

# If the workspace explicitly does not support `--all-features`, define a feature matrix instead of silently skipping.
```

## On-Demand References

- [Cargo Guide Workflow (Onboarding)](references/cargo-guide-workflow.md): Retrieve for beginner and "getting started" questions — `cargo new`/`init`, the everyday build/check/run/test loop, adding dependencies, canonical package layout, `Cargo.toml` vs `Cargo.lock` policy, and GitHub Actions / GitLab CI templates.
- [Manifest and Targets](references/manifest-targets.md)
- [Dependencies, Features, and Resolvers](references/dependencies-features-resolver.md)
- [Production Dependency Selection and Governance](references/production-dependency-governance.md): Retrieve when selecting third-party crates, narrowing feature/platform scope, auditing supply chains, or explaining version lock behavior.
- [Workspaces](references/workspaces.md)
- [Profiles and Optimization Strategies](references/profiles.md)
- [Build Scripts](references/build-scripts.md)
- [Cross-compilation](references/cross-compilation.md)
- [Packaging and Publishing](references/publishing.md)
- [Command Reference Guide](references/references.md)
- [Cargo Book Reference Cheatsheet](references/cargo-reference-cheatsheet.md): Retrieve when configuring `.cargo/config.toml` sections, `[lints]` tables, source replacement/mirroring, `cargo metadata` scripting, CI modes (`--locked`/`--frozen`/`--offline`), or advanced `cargo tree` diagnostics (`--duplicates`, `--invert`, `-e features`).
- [Copy-Pasteable Examples](examples/examples.md)
- `examples/golden-features/`: Feature examples compiled for CI.

## Common Pitfalls to Avoid

1. Omitting the resolver in a virtual workspace, causing member crates' editions to fail when selecting the root crate's resolver settings.
2. Assuming that disabling features at one dependency location cancels out already-enabled features elsewhere.
3. Simultaneously using both `include` and `exclude`, or failing to verify final published package contents after changes.
4. Applying workspace-level profile configurations in member crates, expecting them to override root configuration.
5. Modifying build script inputs without declaring corresponding rerun conditions (`cargo::rerun-if-changed`).
6. Treating `Cargo.lock` strategies universally: applications typically commit the lock file; CI pipelines must still validate locked dependencies against current versions and latest releases.
7. Relying solely on host machine `cargo check`, which does not verify target platform linkers, system libraries, or runtime environments in isolation.
8. Using broad Git branches without fixed sources, compromising reproducibility of builds across different environments.

## Official Sources

- [Cargo Book](https://doc.rust-lang.org/cargo/)
- [Manifest Format Reference](https://doc.rust-lang.org/cargo/reference/manifest.html)
- [Dependency Resolution Guide](https://doc.rust-lang.org/cargo/reference/resolver.html)
- [Features Documentation](https://doc.rust-lang.org/cargo/reference/features.html)
- [Build Scripts Docs](https://doc.rust-lang.org/cargo/reference/build-scripts.html)
- [Workspaces Reference](https://doc.rust-lang.org/cargo/reference/workspaces.html)
- [Publishing Guide](https://doc.rust-lang.org/cargo/reference/publishing.html)

## Data Privacy Policy

This skill does not collect, store, or transmit user data. Before executing `cargo publish`, accessing private registries, or modifying credentials, confirm explicit user authorization and target environment compliance with applicable security policies.
