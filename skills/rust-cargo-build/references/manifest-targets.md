# Cargo Manifest and Targets

Use [Manifest Format](https://doc.rust-lang.org/cargo/reference/manifest.html), [Cargo Targets](https://doc.rust-lang.org/cargo/reference/cargo-targets.html), and [Rust Version](https://doc.rust-lang.org/cargo/reference/rust-version.html) for field-level semantics.

## Inspect before editing

```bash
cargo --version
cargo locate-project --workspace
cargo metadata --no-deps --format-version 1
```

Confirm whether the manifest is a package, a workspace root containing a package, or a virtual workspace.

## Package contract

```toml
[package]
name = "example"
version = "0.1.0"
edition = "2024"
rust-version = "1.85"
license = "Apache-2.0"
description = "Example crate"
repository = "https://example.invalid/repository"
readme = "README.md"
```

- Treat `rust-version` as the minimum supported compiler contract; verify it on that toolchain.
- Do not infer MSRV solely from edition.
- Use SPDX expressions in `license` or an intentional `license-file`.
- Keep publication metadata accurate and inspect the package archive rather than trusting repository layout.
- Put tool-specific metadata under `[package.metadata.<tool>]`; Cargo preserves it without assigning semantics.

## Conventional targets

Cargo discovers these without explicit target tables:

| Path | Target |
|---|---|
| `src/lib.rs` | Library |
| `src/main.rs` | Default binary |
| `src/bin/*.rs` | Additional binaries |
| `examples/*.rs` | Examples |
| `tests/*.rs` | Integration tests |
| `benches/*.rs` | Benchmarks |
| `build.rs` | Build script |

Add `[lib]`, `[[bin]]`, `[[example]]`, `[[test]]`, or `[[bench]]` only to override names, paths, crate types, harness behavior, documentation/bench flags, or required features.

```toml
[[bin]]
name = "example-server"
path = "src/server.rs"
required-features = ["server"]
```

Verify target selection:

```bash
cargo metadata --no-deps --format-version 1
cargo check --all-targets
```

## Package contents

Use `include` or `exclude` only with a clear packaging policy. Generated files, fixtures, secrets, large assets, and native archives require explicit review.

```bash
cargo package --list
cargo package
```

Do not assume `.gitignore` alone defines the archive. Inspect the installed Cargo's package output and minimized manifest/lockfile behavior.

## Lint tables

`[lints.rust]` and `[lints.clippy]` configure compiler-tool lint levels through Cargo manifests and may be inherited from `[workspace.lints]`. Route policy choices to `rust-style-clippy`.

Do not confuse them with Cargo's own `cargo::...` lint system, which may require nightly; see `unstable-features.md`.
