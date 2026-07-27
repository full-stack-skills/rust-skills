# Cargo Configuration and Environment

Use this reference for `.cargo/config.toml`, Cargo environment variables, aliases, network behavior, target-specific linkers/runners, and shared team configuration. Use [Cargo Configuration](https://doc.rust-lang.org/cargo/reference/config.html) and [Environment Variables](https://doc.rust-lang.org/cargo/reference/environment-variables.html) as the field-level authority.

## Contents

- Discovery, precedence, and scope
- Configuration area index
- Common sections
- Compiler flags and host/target separation
- Environment variables
- Validation

## Discovery and scope

Cargo searches for `.cargo/config.toml` or legacy `.cargo/config` from the invocation directory through its ancestors and also reads Cargo Home configuration. Configuration discovery follows the working directory, not each selected package directory. A config file inside a workspace member is therefore not applied when Cargo is invoked from the workspace root.

Before editing:

```bash
cargo --version
cargo locate-project --workspace
cargo build -vv
```

Use verbose output to confirm effective compiler, linker, runner, flags, and target behavior. For the same configuration key, command-line `--config` values take precedence over environment variables, which take precedence over hierarchical configuration files. Dedicated command options may have their own documented precedence.

## Configuration coverage

Consult the official schema instead of assuming this file lists every key:

| Area | Examples |
|---|---|
| Composition and aliases | `include`, `[alias]`, `[credential-alias]` |
| Build and documentation | `[build]`, `[doc]`, `[future-incompat-report]`, `[cache]` |
| Package creation and installation | `[cargo-new]`, `[install]` |
| Network and transport | `[http]`, `[net]`, `[net.ssh]` |
| Dependency and registry behavior | `[patch]`, `[registries]`, `[registry]`, `[source]`, `[resolver]` |
| Profiles and targets | `[profile]`, `[target]` |
| Environment and UI | `[env]`, `[term]` |

Some manifest-shaped configuration, such as patches and profiles, has different scope or inheritance rules from `Cargo.toml`. Read the field's own Reference section before moving declarations between files.

## Common sections

```toml
[build]
target-dir = "target"
jobs = 8

[env]
EXAMPLE_MODE = { value = "development", force = false, relative = false }

[target.x86_64-unknown-linux-gnu]
linker = "clang"
runner = "example-runner"

[target.'cfg(target_os = "linux")']
rustflags = ["-C", "link-arg=-fuse-ld=lld"]

[net]
retry = 3
git-fetch-with-cli = true

[alias]
xtask = "run --package xtask --"

[term]
color = "auto"
```

Rules:

- Prefer manifest fields when behavior belongs to the package's published build contract.
- Prefer workspace `.cargo/config.toml` when behavior belongs to contributors or a checked-in build environment.
- Prefer user Cargo Home configuration for developer-specific defaults.
- Use target triples for exact toolchains and `cfg(...)` tables for shared platform conditions.
- Do not place credentials, private tokens, or environment-specific absolute paths in committed configuration.
- Keep aliases thin; use an `xtask` or dedicated tool when orchestration needs branching, validation, or substantial logic.

## Flags and host/target separation

Build scripts and procedural macros execute for the host, while the final artifact may compile for another target. Avoid applying target link flags to host tools accidentally.

Use:

```bash
cargo build --target <triple> -vv
rustc --print cfg --target <triple>
```

Treat `RUSTFLAGS`, `CARGO_ENCODED_RUSTFLAGS`, target-specific `rustflags`, and `build.rustflags` as effective compiler inputs. Verify precedence from the current Configuration Reference rather than combining them by assumption.

## Environment variables

Cargo exposes package metadata, manifest paths, target properties, profile settings, and build-script context through documented environment variables. Distinguish:

- variables Cargo reads to change its own behavior;
- variables Cargo sets for crates and build scripts;
- `CARGO_CFG_*`, `OUT_DIR`, `HOST`, and `TARGET` build-script context;
- `DEP_<links>_*` metadata emitted by native dependency build scripts.

Do not rely on a Cargo-set variable outside the command phase where the Reference guarantees it. Never print secrets while diagnosing environment state.

## Validation

```bash
cargo metadata --no-deps --format-version 1
cargo check --workspace --all-targets -vv
```

For cross-compilation, verify both host and target commands in verbose output and execute the result on the target runner or environment.
