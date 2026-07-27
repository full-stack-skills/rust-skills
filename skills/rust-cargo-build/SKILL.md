---
name: rust-cargo-build
description: Configure, operate, diagnose, and automate Cargo for Rust packages and workspaces. Cover manifests and targets, commands, dependency resolution and features, profiles, build scripts, configuration and environment variables, caches and build diagnostics, cross-compilation, registries, packaging, publishing, metadata, CI reproducibility, and stable-versus-nightly feature gates. Use for Cargo.toml, Cargo.lock, .cargo/config.toml, cargo build/check/run/tree/metadata/package/publish, resolver or feature problems, build output and performance, private registries, and beginner Cargo workflows. Route crate selection and supply-chain audits to rust-dependencies, workspace topology to rust-workspace, test design to rust-testing, documentation design to rust-documentation, lint policy to rust-style-clippy, and API compatibility decisions to rust-semver.
---

# Rust Cargo Build System

Use Cargo as a versioned package manager, build orchestrator, and automation interface. Base decisions on the project's actual Cargo version, MSRV, workspace root, targets, and release model. Use the official Cargo Book as the authority; keep this skill focused on task selection, execution, and validation.

## Preflight

Run the smallest relevant subset:

```bash
rustc --version --verbose
cargo --version
cargo locate-project --workspace
cargo metadata --no-deps --format-version 1
```

Determine:

- whether the root manifest is a package or virtual workspace;
- the declared `edition`, `rust-version`, resolver, and lockfile policy;
- selected packages, targets, features, profiles, and target triples;
- dependency sources, registry configuration, and offline constraints;
- whether the requested behavior is stable on the installed Cargo version.

## Route to the Right Reference

Read only the reference needed for the current task:

| Task | Reference |
|---|---|
| Find the authoritative Cargo Guide, Reference, command, or changelog page | [Official Documentation Map](references/official-doc-map.md) |
| Select a Cargo command and understand its side effects | [Cargo Command Map](references/cargo-command-map.md) |
| Start, build, run, test, document, or add CI to a package | [Cargo Guide Workflow](references/cargo-guide-workflow.md) |
| Configure package metadata and lib/bin/example/test/bench targets | [Manifest and Targets](references/manifest-targets.md) |
| Configure dependency sources, features, overrides, or resolvers | [Dependencies, Features, and Resolvers](references/dependencies-features-resolver.md) |
| Configure members and inherited workspace fields | [Workspaces](references/workspaces.md) |
| Configure `.cargo/config.toml`, environment variables, aliases, network, or target settings | [Configuration and Environment](references/configuration-environment.md) |
| Tune dev/release/custom profiles | [Profiles](references/profiles.md) |
| Generate code, compile native dependencies, or emit Cargo instructions from `build.rs` | [Build Scripts](references/build-scripts.md) |
| Diagnose rebuilds, duplicate compilation, cache layout, timings, or future incompatibilities | [Build Cache and Diagnostics](references/build-cache-diagnostics.md) |
| Configure a linker, runner, or non-host target | [Cross-compilation](references/cross-compilation.md) |
| Configure registries, source replacement, vendoring, credentials, or authentication | [Registries and Authentication](references/registries-authentication.md) |
| Inspect package contents, publish, manage owners, or yank a version | [Packaging and Publishing](references/publishing.md) |
| Build scripts and tooling around stable Cargo JSON or package IDs | [Metadata and Automation](references/metadata-automation.md) |
| Evaluate `cargo-features`, `-Z`, or other nightly-only behavior | [Unstable Cargo Features](references/unstable-features.md) |

## Core Workflow

1. **Locate the root** — Confirm the workspace root and effective manifest before editing.
2. **Declare compatibility** — Record edition, MSRV, supported targets, stable/nightly policy, and feature contract.
3. **Inspect effective state** — Use `cargo metadata`, `cargo tree`, and the effective configuration rather than inferring from one manifest.
4. **Make the smallest change** — Prefer conventional targets, additive features, workspace inheritance, and stable Cargo behavior.
5. **Exercise the requested matrix** — Select packages, targets, features, profiles, and target triples explicitly.
6. **Diagnose before optimizing** — Use timings, dependency edges, verbose output, and rebuild evidence before changing profiles or caches.
7. **Verify artifacts and side effects** — Inspect generated files, package contents, lockfile changes, registry targets, and credentials handling.

## Decision Rules

### Manifest, MSRV, and Resolver

- Do not equate an edition with MSRV; declare `package.rust-version` and test that toolchain.
- Treat the resolver as workspace-wide. Explicitly set it in virtual workspaces.
- Verify resolver defaults and version-gated fields against the installed Cargo documentation or changelog.
- Keep explicit target tables only when Cargo's conventional paths are insufficient.

### Cargo.lock and Reproducibility

- When in doubt, commit `Cargo.lock`; the current Cargo Guide recommends version control by default.
- Decide exceptions from the repository's release, CI, and dependency-verification policy, not from a blanket “applications yes, libraries no” rule.
- Use `--locked` when a committed lockfile must not change.
- Use `--frozen` only when both lockfile mutation and network access must be prohibited.
- Review lockfile diffs; do not delete the lockfile or run broad updates merely to bypass CI failures.

### Dependencies and Features

- Treat features as additive and validate unification with `cargo tree -e features`.
- Use target-specific dependencies for platform selection; do not put `cfg(feature = "...")` in target dependency tables.
- Pin Git dependencies to a revision when reproducibility requires them.
- Use `[patch]`, source replacement, and vendoring only for their documented purposes; do not treat them as interchangeable.

### Configuration and Environment

- Distinguish manifest configuration from hierarchical Cargo configuration.
- Verify `.cargo/config.toml` discovery from the command's working directory.
- Keep secrets out of committed configuration and command history.
- Separate host settings for build scripts and proc macros from target settings used for final artifacts.

### Build Scripts

- Write generated artifacts only to `OUT_DIR`.
- Emit precise `cargo::rerun-if-changed` and `cargo::rerun-if-env-changed` instructions.
- Keep outputs reproducible and avoid network access during builds.
- Treat native link directives and `links` metadata as public integration contracts.

### Profiles, Cache, and Diagnostics

- Measure the workflow being optimized: `check`, incremental development, tests, CI, release linking, runtime, or binary size.
- Keep profile definitions at the workspace root.
- Treat the build-directory layout as Cargo-internal unless the Reference documents an output location.
- Prefer `cargo build --timings`, `cargo tree -d`, and future-incompatibility reports over speculative cache deletion.

### Registries and Publishing

- Distinguish registries, source replacement, directory sources, and vendoring.
- Resolve credential providers and registry identity before login or publish operations.
- Run `cargo package --list` and package verification before publishing.
- Require explicit authorization before login, owner changes, publishing, yanking, or modifying credentials.

### Stable and Nightly

- Prefer stable Cargo behavior.
- Before recommending nightly, identify the exact unstable feature, invocation form, tracking issue, fallback, and removal condition.
- Never present `cargo-features`, `-Z`, or `[unstable]` configuration as stable.
- Re-check the changelog because unstable interfaces can stabilize, change, or disappear.

## Validation

Adapt the matrix instead of running unsupported combinations blindly:

```bash
cargo metadata --format-version 1
cargo fmt --all --check
cargo check --workspace --all-targets --all-features
cargo test --workspace --all-targets --all-features
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo package --list
```

Append `--locked` to supported Cargo commands when the repository commits or requires a lockfile. If the workspace intentionally excludes some features or targets, define an explicit matrix and record why.

## Boundaries

- Crate selection, advisories, licenses, bans, and supply-chain policy → `rust-dependencies`
- Workspace and crate topology → `rust-workspace`
- Test architecture, fixtures, property tests, and coverage → `rust-testing`
- rustdoc content and documentation architecture → `rust-documentation`
- rustfmt, Clippy policy, and edition migration → `rust-style-clippy`
- Runtime performance and allocation behavior → `rust-performance`
- API compatibility and version-bump decisions → `rust-semver`
- Embedded target runtime and hardware integration → `rust-embedded`

Cargo command mechanics may remain here even when the higher-level decision belongs to another skill.

## Completion Criteria

- Identify the effective workspace, Cargo version, MSRV, target, feature, and profile context.
- Link the relevant official Cargo page for version-sensitive behavior.
- Separate stable behavior from nightly experiments.
- Validate the effective dependency graph and configuration.
- Preserve reproducibility and credential safety.
- Confirm artifact, package, or registry side effects before declaring success.

## Data Privacy

This skill does not collect, store, or transmit user data. Treat registry tokens, Git credentials, environment variables, generated artifacts, and package contents as potentially sensitive.
