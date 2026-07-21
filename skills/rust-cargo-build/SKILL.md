---
name: rust-cargo-build
description: Configure and diagnose Rust Cargo builds, including Cargo.toml manifests, dependency sources and versions, features, resolvers, profiles, build.rs, workspaces, cross-compilation, packaging, and publishing. Use when users ask about Cargo manifests, dependency resolution, feature unification, build output, MSRV-aware resolution, Cargo commands, or crates.io publishing; hand module layout to rust-workspace and test design to rust-testing.
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

- [Manifest and Targets](references/manifest-targets.md)
- [Dependencies, Features, and Resolvers](references/dependencies-features-resolver.md)
- [Production Dependency Selection and Governance](references/production-dependency-governance.md): Retrieve when selecting third-party crates, narrowing feature/platform scope, auditing supply chains, or explaining version lock behavior.
- [Workspaces](references/workspaces.md)
- [Profiles and Optimization Strategies](references/profiles.md)
- [Build Scripts](references/build-scripts.md)
- [Cross-compilation](references/cross-compilation.md)
- [Packaging and Publishing](references/publishing.md)
- [Command Reference Guide](references/references.md)
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
